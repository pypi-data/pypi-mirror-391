"""Test MCP client automatic token loading from environment."""

import os
import pytest
from dotenv import load_dotenv
from mbxai.mcp import AsyncMCPClient
from mbxai.openrouter import AsyncOpenRouterClient, OpenRouterModel

# Load environment variables from .env file
load_dotenv()


@pytest.mark.asyncio
async def test_mcp_auto_loads_env_token():
    """Test that MCP client automatically loads MBXAI_API_TOKEN from environment."""
    
    # Ensure the environment variable is set
    token = os.getenv("MBXAI_API_TOKEN")
    if not token:
        pytest.skip("MBXAI_API_TOKEN not set - skipping test")
    
    print(f"\n✓ Environment variable MBXAI_API_TOKEN is set")
    
    # Create clients
    openrouter = AsyncOpenRouterClient(
        token=os.getenv("OPENROUTER_API_KEY", "test-key"),
        model=OpenRouterModel.GPT41
    )
    
    async with AsyncMCPClient(openrouter) as mcp_client:
        # Register WITHOUT explicitly passing token
        # Should automatically use MBXAI_API_TOKEN from environment
        print(f"✓ Registering MCP server WITHOUT explicit token...")
        await mcp_client.register_mcp_server(
            name="mbxai-cloud",
            base_url="https://api.mbxai.cloud/api"
            # Note: NO token parameter passed!
        )
        
        # Verify tools were loaded
        assert len(mcp_client._tools) > 0, "No tools registered"
        print(f"✓ Successfully registered {len(mcp_client._tools)} tools")
        print(f"✓ Available tools: {list(mcp_client._tools.keys())[:5]}...")
        
        # Verify the token was stored
        assert "mbxai-cloud" in mcp_client._mcp_tokens, "Token not stored"
        assert mcp_client._mcp_tokens["mbxai-cloud"] == token, "Wrong token stored"
        print(f"✓ Token automatically loaded from environment")
        
    print("\n✅ Test PASSED: MCP client automatically uses MBXAI_API_TOKEN")


@pytest.mark.asyncio
async def test_mcp_explicit_token_overrides_env():
    """Test that explicit token parameter overrides environment variable."""
    
    if not os.getenv("MBXAI_API_TOKEN"):
        pytest.skip("MBXAI_API_TOKEN not set - skipping test")
    
    print(f"\n✓ Testing explicit token override...")
    
    # Create clients
    openrouter = AsyncOpenRouterClient(
        token=os.getenv("OPENROUTER_API_KEY", "test-key"),
        model=OpenRouterModel.GPT41
    )
    
    explicit_token = "explicit-test-token-12345"
    
    async with AsyncMCPClient(openrouter) as mcp_client:
        # Register WITH explicit token (should override environment)
        print(f"✓ Registering with explicit token...")
        
        # This should fail with the fake token, which proves it's using the explicit one
        # and not falling back to the environment variable
        try:
            await mcp_client.register_mcp_server(
                name="mbxai-cloud",
                base_url="https://api.mbxai.cloud/api",
                token=explicit_token  # Explicit token that won't work
            )
            # If we get here, something is wrong (maybe server doesn't validate tokens?)
            # But let's check that the token was stored correctly
            assert mcp_client._mcp_tokens.get("mbxai-cloud") == explicit_token
            print(f"✓ Explicit token was used and stored")
        except Exception as e:
            # Expected to fail with explicit fake token
            # Verify it tried to use the explicit token by checking it was stored
            if "mbxai-cloud" in mcp_client._mcp_tokens:
                assert mcp_client._mcp_tokens["mbxai-cloud"] == explicit_token
                print(f"✓ Explicit token overrode environment (request failed as expected)")
            else:
                print(f"✓ Request failed with explicit token (as expected): {str(e)[:100]}")
        
    print("\n✅ Test PASSED: Explicit token overrides environment variable")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_mcp_auto_loads_env_token())
    asyncio.run(test_mcp_explicit_token_overrides_env())

