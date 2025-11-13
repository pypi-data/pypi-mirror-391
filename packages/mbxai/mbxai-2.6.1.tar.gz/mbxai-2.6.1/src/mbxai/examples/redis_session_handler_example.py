"""
Example of a Redis session handler for the AgentClient.

This demonstrates how to implement a custom session handler that uses Redis
for storing agent sessions, enabling distributed and persistent session storage.

Requirements:
    pip install redis

Usage:
    python redis_session_handler_example.py
"""

import json
import logging
from typing import Dict, Any, Optional
import redis

from mbxai import AgentClient, OpenRouterClient
from mbxai.agent.models import SessionHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RedisSessionHandler:
    """Redis-based session handler for AgentClient."""
    
    def __init__(
        self, 
        redis_client: redis.Redis = None,
        key_prefix: str = "mbxai:agent:session:",
        ttl_seconds: int = 86400  # 24 hours default TTL
    ):
        """
        Initialize Redis session handler.
        
        Args:
            redis_client: Redis client instance (creates default if None)
            key_prefix: Prefix for Redis keys
            ttl_seconds: Session TTL in seconds (0 = no expiration)
        """
        self.redis_client = redis_client or redis.Redis(
            host='localhost', 
            port=6379, 
            db=0, 
            decode_responses=True
        )
        self.key_prefix = key_prefix
        self.ttl_seconds = ttl_seconds
        
    def _get_key(self, agent_id: str) -> str:
        """Get Redis key for agent session."""
        return f"{self.key_prefix}{agent_id}"
    
    def get_session(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a session by agent ID."""
        try:
            key = self._get_key(agent_id)
            session_json = self.redis_client.get(key)
            
            if session_json:
                session_data = json.loads(session_json)
                logger.debug(f"Retrieved session {agent_id} from Redis")
                return session_data
            
            logger.debug(f"Session {agent_id} not found in Redis")
            return None
            
        except (redis.RedisError, json.JSONDecodeError) as e:
            logger.error(f"Error retrieving session {agent_id}: {e}")
            return None
    
    def set_session(self, agent_id: str, session_data: Dict[str, Any]) -> None:
        """Store session data for an agent ID."""
        try:
            key = self._get_key(agent_id)
            session_json = json.dumps(session_data, default=str)
            
            if self.ttl_seconds > 0:
                self.redis_client.setex(key, self.ttl_seconds, session_json)
            else:
                self.redis_client.set(key, session_json)
                
            logger.debug(f"Stored session {agent_id} in Redis")
            
        except (redis.RedisError, json.JSONEncodeError) as e:
            logger.error(f"Error storing session {agent_id}: {e}")
            raise
    
    def delete_session(self, agent_id: str) -> bool:
        """Delete a session by agent ID."""
        try:
            key = self._get_key(agent_id)
            result = self.redis_client.delete(key)
            
            if result > 0:
                logger.debug(f"Deleted session {agent_id} from Redis")
                return True
            else:
                logger.debug(f"Session {agent_id} not found for deletion")
                return False
                
        except redis.RedisError as e:
            logger.error(f"Error deleting session {agent_id}: {e}")
            return False
    
    def list_sessions(self) -> list[str]:
        """List all active session IDs."""
        try:
            pattern = f"{self.key_prefix}*"
            keys = self.redis_client.keys(pattern)
            
            # Extract agent IDs from keys
            agent_ids = [
                key.replace(self.key_prefix, "") 
                for key in keys
            ]
            
            logger.debug(f"Found {len(agent_ids)} sessions in Redis")
            return agent_ids
            
        except redis.RedisError as e:
            logger.error(f"Error listing sessions: {e}")
            return []
    
    def session_exists(self, agent_id: str) -> bool:
        """Check if a session exists."""
        try:
            key = self._get_key(agent_id)
            return self.redis_client.exists(key) > 0
        except redis.RedisError as e:
            logger.error(f"Error checking session existence {agent_id}: {e}")
            return False
    
    def get_session_ttl(self, agent_id: str) -> int:
        """Get remaining TTL for a session (Redis-specific method)."""
        try:
            key = self._get_key(agent_id)
            return self.redis_client.ttl(key)
        except redis.RedisError as e:
            logger.error(f"Error getting TTL for session {agent_id}: {e}")
            return -1
    
    def extend_session_ttl(self, agent_id: str, additional_seconds: int = None) -> bool:
        """Extend session TTL (Redis-specific method)."""
        try:
            key = self._get_key(agent_id)
            ttl = additional_seconds or self.ttl_seconds
            return self.redis_client.expire(key, ttl)
        except redis.RedisError as e:
            logger.error(f"Error extending TTL for session {agent_id}: {e}")
            return False


class DistributedRedisSessionHandler(RedisSessionHandler):
    """Redis session handler with clustering/sentinel support."""
    
    def __init__(
        self,
        redis_sentinels: list[tuple[str, int]] = None,
        service_name: str = "mymaster",
        **kwargs
    ):
        """
        Initialize with Redis Sentinel for high availability.
        
        Args:
            redis_sentinels: List of (host, port) tuples for sentinels
            service_name: Name of the Redis service in Sentinel
        """
        if redis_sentinels:
            sentinel = redis.Sentinel(redis_sentinels)
            redis_client = sentinel.master_for(service_name, decode_responses=True)
        else:
            redis_client = None
            
        super().__init__(redis_client=redis_client, **kwargs)


def main():
    """Example usage of Redis session handler."""
    
    try:
        # Create Redis session handler
        redis_handler = RedisSessionHandler(
            ttl_seconds=3600  # 1 hour TTL
        )
        
        # Test Redis connection
        redis_handler.redis_client.ping()
        logger.info("✅ Connected to Redis")
        
        # Create AgentClient with Redis session handler
        openrouter_client = OpenRouterClient(
            api_key="your-api-key-here"  # Replace with actual key
        )
        
        agent = AgentClient(
            ai_client=openrouter_client,
            human_in_loop=True,
            session_handler=redis_handler
        )
        
        logger.info("✅ AgentClient created with Redis session handler")
        
        # Example: Create a session
        from pydantic import BaseModel
        
        class SimpleResponse(BaseModel):
            message: str
        
        # Start agent conversation
        response = agent.agent(
            prompt="Hello, this is a test with Redis session storage",
            final_response_structure=SimpleResponse
        )
        
        agent_id = response.agent_id
        logger.info(f"✅ Created agent session: {agent_id}")
        
        # Test session persistence
        session_info = agent.get_session_info(agent_id)
        logger.info(f"✅ Session retrieved: {len(session_info)} fields")
        
        # Test session TTL
        ttl = redis_handler.get_session_ttl(agent_id)
        logger.info(f"✅ Session TTL: {ttl} seconds")
        
        # List all sessions
        sessions = agent.list_sessions()
        logger.info(f"✅ Active sessions: {sessions}")
        
        # Clean up
        agent.delete_session(agent_id)
        logger.info(f"✅ Session {agent_id} deleted")
        
    except redis.ConnectionError:
        logger.error("❌ Could not connect to Redis. Make sure Redis is running on localhost:6379")
        logger.info("Start Redis with: redis-server")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
