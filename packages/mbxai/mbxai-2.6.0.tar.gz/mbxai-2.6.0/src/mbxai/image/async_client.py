"""
Async Image client implementation for MBX AI.
"""

import logging
import base64
import io
from typing import Any
import httpx

from .models import (
    ImageGenerationInput, ImageEditInput, 
    ImageGenerationResponse, ImageEditResponse
)
from ..utils.client import generate_image_async, edit_image_async

logger = logging.getLogger(__name__)


class AsyncImageClient:
    """Async client for image generation and editing operations."""

    def __init__(self, api_key: str | None = None) -> None:
        """Initialize the AsyncImageClient.

        Args:
            api_key: OpenAI API key. If None, will try to get from environment
        """
        import os
        self._api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self._api_key:
            raise ValueError("OpenAI API key is required. Provide it or set OPENAI_API_KEY environment variable.")
        
        # Set the API key in environment for utility functions
        os.environ["OPENAI_API_KEY"] = self._api_key

    async def _process_image_input(self, image_input: str, name: str) -> io.BytesIO:
        """Process an image input that can be either a URL or base64 string.
        
        Args:
            image_input: Either a URL or base64 encoded string
            name: Name to assign to the file object
            
        Returns:
            BytesIO object containing the image data
            
        Raises:
            ValueError: If the input is invalid or download fails
        """
        # Check if it's a URL (starts with http:// or https://)
        if image_input.startswith(('http://', 'https://')):
            logger.info(f"Processing image URL: {image_input}")
            try:
                # Download the image from URL
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(image_input)
                    response.raise_for_status()
                    
                    img_file = io.BytesIO(response.content)
                    img_file.name = name
                    logger.info(f"Successfully downloaded image from URL: {len(response.content)} bytes")
                    return img_file
                    
            except Exception as e:
                raise ValueError(f"Failed to download image from URL {image_input}: {str(e)}")
        else:
            # Log first characters of base64 for debugging
            preview = image_input[:50] + "..." if len(image_input) > 50 else image_input
            logger.info(f"Processing base64 image: {preview}")
            
            try:
                # Assume it's base64 encoded
                # Remove data URL prefix if present (e.g., "data:image/png;base64,")
                if image_input.startswith('data:'):
                    image_input = image_input.split(',', 1)[1]
                    logger.info(f"Removed data URL prefix, base64 length: {len(image_input)}")
                
                img_data = base64.b64decode(image_input)
                img_file = io.BytesIO(img_data)
                img_file.name = name
                logger.info(f"Successfully decoded base64 image: {len(img_data)} bytes")
                return img_file
                
            except Exception as e:
                raise ValueError(f"Failed to decode base64 image: {str(e)}")

    async def generate(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard",
        model: str = "gpt-image-1",
        images: list[str] | None = None
    ) -> ImageGenerationResponse:
        """Generate an image based on a text prompt.
        
        Args:
            prompt: The text description of the image to generate
            size: The size of the image ('1024x1024', '1024x1536', '1536x1024')
            quality: The quality of the image ('standard', 'hd')
            model: The model to use ('gpt-image-1', 'dall-e-3')
            images: List of reference images as URLs or base64 encoded strings (empty list for no references)
            
        Returns:
            ImageGenerationResponse containing the generated image data and metadata
        """
        try:
            logger.info(f"Generating image with prompt: {prompt[:100]}...")
            
            # Create input model
            input_data = ImageGenerationInput(
                prompt=prompt,
                size=size,
                quality=quality,
                model=model,
                images=images or []
            )
            
            # Use defaults if empty strings provided
            model_to_use = input_data.model if input_data.model and input_data.model.strip() else "gpt-image-1"
            size_to_use = input_data.size if input_data.size and input_data.size.strip() else "1024x1024"
            quality_to_use = input_data.quality if input_data.quality and input_data.quality.strip() else "standard"
            
            # Check if using reference images with gpt-image-1
            if input_data.images and len(input_data.images) > 0 and any(img.strip() for img in input_data.images):
                if model_to_use != "gpt-image-1":
                    logger.warning("Reference images provided but model is not gpt-image-1. Switching to gpt-image-1.")
                    model_to_use = "gpt-image-1"
                
                # Process images (URLs or base64) to file-like objects for reference image generation
                image_files = []
                for i, img_input in enumerate(input_data.images):
                    if img_input and img_input.strip():  # Skip empty strings
                        try:
                            # Log what type of input we're processing
                            if img_input.startswith(('http://', 'https://')):
                                logger.info(f"Reference image {i}: URL - {img_input}")
                            else:
                                preview = img_input[:50] + "..." if len(img_input) > 50 else img_input
                                logger.info(f"Reference image {i}: Base64 - {preview}")
                            
                            img_file = await self._process_image_input(img_input, f"reference_{i}.png")
                            image_files.append(img_file)
                            logger.info(f"Processed reference image {i}: {len(img_file.getvalue())} bytes")
                        except Exception as e:
                            raise ValueError(f"Failed to process reference image {i}: {str(e)}")
                
                # Use edit_image_async for reference image generation (no mask needed)
                image_url = await edit_image_async(
                    prompt=input_data.prompt,
                    image_files=image_files,
                    mask_file=None,
                    model=model_to_use,
                    size=size_to_use
                )
                
            else:
                # Standard image generation without reference images
                image_url = await generate_image_async(
                    prompt=input_data.prompt,
                    model=model_to_use,
                    size=size_to_use,
                    quality=quality_to_use
                )
            
            return ImageGenerationResponse(
                success=True,
                prompt=input_data.prompt,
                model=model_to_use,
                size=size_to_use,
                quality=quality_to_use,
                image_url=image_url,
                message="Image generated successfully"
            )
            
        except Exception as e:
            logger.error("=== Image Generation Error ===")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error message: {str(e)}")
            logger.error(f"Input parameters:")
            logger.error(f"  - Prompt: {prompt}")
            logger.error(f"  - Model: {model_to_use if 'model_to_use' in locals() else model}")
            logger.error(f"  - Size: {size_to_use if 'size_to_use' in locals() else size}")
            logger.error(f"  - Quality: {quality_to_use if 'quality_to_use' in locals() else quality}")
            logger.error(f"  - Images count: {len(images) if images else 0}")
            
            # Determine error type for better user feedback
            error_message = "Failed to generate image"
            error_details = str(e)
            
            if "400" in str(e) or "bad request" in str(e).lower():
                error_message = "Invalid request parameters"
                logger.error("This appears to be a 400 Bad Request error. Common causes:")
                logger.error("  - Invalid prompt content (violates content policy)")
                logger.error("  - Invalid size or quality parameters")
                logger.error("  - Prompt too long or too short")
                logger.error("  - Unsupported characters in prompt")
                
            elif "timeout" in str(e).lower():
                error_message = "Timeout while generating image"
                logger.error("Request timed out - this may indicate network issues or API overload")
                
            elif "http" in str(e).lower() and "401" in str(e):
                error_message = "Authentication failed"
                logger.error("401 Unauthorized - check API key configuration")
                
            elif "http" in str(e).lower() and "403" in str(e):
                error_message = "Access forbidden"
                logger.error("403 Forbidden - check API permissions and quota")
                
            elif "http" in str(e).lower() and "429" in str(e):
                error_message = "Rate limit exceeded"
                logger.error("429 Too Many Requests - API rate limit exceeded")
                
            elif "http" in str(e).lower() and "500" in str(e):
                error_message = "Server error during image generation"
                logger.error("500 Internal Server Error - OpenAI API server issue")
                
            elif "http" in str(e).lower():
                error_message = "Network error during image generation"
                logger.error("HTTP error occurred during API request")
            
            # Log the full error context for debugging
            logger.error(f"Full error context: {error_details}")
            
            return ImageGenerationResponse(
                success=False,
                error=error_details,
                prompt=prompt,
                model=model_to_use if 'model_to_use' in locals() else model,
                size=size_to_use if 'size_to_use' in locals() else size,
                quality=quality_to_use if 'quality_to_use' in locals() else quality,
                message=error_message
            )

    async def edit(
        self,
        prompt: str,
        images: list[str],
        mask: str = "",
        size: str = "1024x1024",
        model: str = "gpt-image-1"
    ) -> ImageEditResponse:
        """Edit an image based on a text prompt.
        
        Args:
            prompt: The text description of the edit to apply
            images: List of images as URLs or base64 encoded strings - first is main image, rest are references
            mask: Mask image as URL or base64 encoded string for selective editing (use empty string for no mask)
            size: The size of the image ('1024x1024', '1024x1536', '1536x1024')
            model: The model to use for editing ('gpt-image-1' or 'dall-e-3')
            
        Returns:
            ImageEditResponse containing the edited image data and metadata
        """
        try:
            logger.info(f"Editing image with prompt: {prompt[:100]}...")
            
            # Create input model
            input_data = ImageEditInput(
                prompt=prompt,
                images=images,
                mask=mask,
                size=size,
                model=model
            )
            
            # Set default values if empty strings provided
            size_to_use = input_data.size if input_data.size and input_data.size.strip() else "1024x1024"
            model_to_use = input_data.model if input_data.model and input_data.model.strip() else "gpt-image-1"
            
            logger.info(f"Using size: {size_to_use}, model: {model_to_use}")
            
            # Process images (URLs or base64) to file-like objects
            image_files = []
            for i, img_input in enumerate(input_data.images):
                try:
                    # Log what type of input we're processing
                    if img_input.startswith(('http://', 'https://')):
                        logger.info(f"Input image {i}: URL - {img_input}")
                    else:
                        preview = img_input[:50] + "..." if len(img_input) > 50 else img_input
                        logger.info(f"Input image {i}: Base64 - {preview}")
                    
                    img_file = await self._process_image_input(img_input, f"image_{i}.png")
                    image_files.append(img_file)
                    logger.info(f"Processed image {i}: {len(img_file.getvalue())} bytes")
                except Exception as e:
                    raise ValueError(f"Failed to process image {i}: {str(e)}")
            
            # Process mask if provided
            mask_file = None
            if input_data.mask and input_data.mask.strip():
                try:
                    # Log what type of mask input we're processing
                    if input_data.mask.startswith(('http://', 'https://')):
                        logger.info(f"Mask: URL - {input_data.mask}")
                    else:
                        preview = input_data.mask[:50] + "..." if len(input_data.mask) > 50 else input_data.mask
                        logger.info(f"Mask: Base64 - {preview}")
                    
                    mask_file = await self._process_image_input(input_data.mask, "mask.png")
                    logger.info(f"Processed mask: {len(mask_file.getvalue())} bytes")
                except Exception as e:
                    raise ValueError(f"Failed to process mask: {str(e)}")
            
            # Edit the image using the async client function
            image_url = await edit_image_async(
                prompt=input_data.prompt,
                image_files=image_files,
                mask_file=mask_file,
                model=model_to_use,
                size=size_to_use
            )
            
            return ImageEditResponse(
                success=True,
                prompt=input_data.prompt,
                model=model_to_use,
                size=size_to_use,
                images_count=len(input_data.images),
                mask_provided=input_data.mask is not None and input_data.mask.strip(),
                image_url=image_url,
                message="Image edited successfully"
            )
            
        except Exception as e:
            logger.error("=== Image Editing Error ===")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error message: {str(e)}")
            logger.error(f"Input parameters:")
            logger.error(f"  - Prompt: {prompt}")
            logger.error(f"  - Model: {model_to_use if 'model_to_use' in locals() else model}")
            logger.error(f"  - Size: {size_to_use if 'size_to_use' in locals() else size}")
            logger.error(f"  - Images count: {len(images)}")
            logger.error(f"  - Mask provided: {mask is not None and mask.strip()}")
            
            # Determine error type for better user feedback
            error_message = "Failed to edit image"
            error_details = str(e)
            
            if "400" in str(e) or "bad request" in str(e).lower():
                error_message = "Invalid request parameters"
                logger.error("This appears to be a 400 Bad Request error. Common causes:")
                logger.error("  - Invalid prompt content (violates content policy)")
                logger.error("  - Invalid image format or size")
                logger.error("  - Invalid mask format or dimensions")
                logger.error("  - Unsupported model or parameters")
                
            elif "timeout" in str(e).lower():
                error_message = "Timeout while editing image"
                logger.error("Request timed out - this may indicate network issues or API overload")
                
            elif "http" in str(e).lower() and "401" in str(e):
                error_message = "Authentication failed"
                logger.error("401 Unauthorized - check API key configuration")
                
            elif "http" in str(e).lower() and "403" in str(e):
                error_message = "Access forbidden"
                logger.error("403 Forbidden - check API permissions and quota")
                
            elif "http" in str(e).lower() and "429" in str(e):
                error_message = "Rate limit exceeded"
                logger.error("429 Too Many Requests - API rate limit exceeded")
                
            elif "http" in str(e).lower() and "500" in str(e):
                error_message = "Server error during image editing"
                logger.error("500 Internal Server Error - OpenAI API server issue")
                
            elif "http" in str(e).lower():
                error_message = "Network error during image editing"
                logger.error("HTTP error occurred during API request")
            
            # Log the full error context for debugging
            logger.error(f"Full error context: {error_details}")
            
            return ImageEditResponse(
                success=False,
                error=error_details,
                prompt=prompt,
                model=model_to_use if 'model_to_use' in locals() else model,
                size=size_to_use if 'size_to_use' in locals() else size,
                images_count=len(images),
                mask_provided=mask is not None and mask.strip(),
                message=error_message
            )

    async def parse(
        self,
        messages: list[dict[str, Any]],
        response_format: object,
        *,
        model: str | None = None,
        **kwargs: Any,
    ) -> Any:
        """Parse method for compatibility with other clients. Not implemented for image client.
        
        Raises:
            NotImplementedError: This method is not applicable for image operations
        """
        raise NotImplementedError("parse method is not applicable for image operations. Use generate() or edit() instead.")

    async def chat(
        self,
        messages: list[dict[str, Any]],
        *,
        model: str | None = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> Any:
        """Chat method for compatibility with other clients. Not implemented for image client.
        
        Raises:
            NotImplementedError: This method is not applicable for image operations
        """
        raise NotImplementedError("chat method is not applicable for image operations. Use generate() or edit() instead.")

    async def create(
        self,
        messages: list[dict[str, Any]],
        *,
        model: str | None = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> Any:
        """Create method for compatibility with other clients. Not implemented for image client.
        
        Raises:
            NotImplementedError: This method is not applicable for image operations
        """
        raise NotImplementedError("create method is not applicable for image operations. Use generate() or edit() instead.")
