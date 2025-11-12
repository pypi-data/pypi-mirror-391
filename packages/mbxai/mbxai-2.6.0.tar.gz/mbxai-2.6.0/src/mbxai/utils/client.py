"""Utility functions for image generation and editing."""

import os
import logging
from typing import Any
import io
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


async def generate_image_async(
    prompt: str,
    model: str = "gpt-image-1",
    size: str = "1024x1024",
    quality: str = "standard"
) -> str:
    """Generate an image using OpenAI's image generation API.
    
    Args:
        prompt: Text description of the image to generate
        model: Model to use for generation
        size: Image size
        quality: Image quality
        
    Returns:
        URL of the generated image
        
    Raises:
        ValueError: If generation fails
    """
    try:
        # Get OpenAI API key from environment
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        client = AsyncOpenAI(api_key=api_key)
        
        response = await client.images.generate(
            model=model,
            prompt=prompt,
            size=size,
            quality=quality,
            n=1
        )
        
        if not response.data or len(response.data) == 0:
            raise ValueError("No image generated in response")
        
        return response.data[0].url
        
    except Exception as e:
        logger.error(f"Image generation failed: {str(e)}")
        raise ValueError(f"Image generation failed: {str(e)}")


async def edit_image_async(
    prompt: str,
    image_files: list[io.BytesIO],
    mask_file: io.BytesIO | None = None,
    model: str = "gpt-image-1",
    size: str = "1024x1024"
) -> str:
    """Edit an image using OpenAI's image editing API.
    
    Args:
        prompt: Text description of the edit to apply
        image_files: List of image files (first is main image, rest are references)
        mask_file: Optional mask file for selective editing
        model: Model to use for editing
        size: Image size
        
    Returns:
        URL of the edited image
        
    Raises:
        ValueError: If editing fails
    """
    try:
        # Get OpenAI API key from environment
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        client = AsyncOpenAI(api_key=api_key)
        
        if not image_files or len(image_files) == 0:
            raise ValueError("At least one image file is required")
        
        # For now, use the first image as the main image for editing
        # In a full implementation, you might want to handle multiple reference images differently
        main_image = image_files[0]
        
        # Reset file position to beginning
        main_image.seek(0)
        if mask_file:
            mask_file.seek(0)
        
        if mask_file:
            # Edit with mask
            response = await client.images.edit(
                model=model,
                image=main_image,
                mask=mask_file,
                prompt=prompt,
                size=size,
                n=1
            )
        else:
            # Edit without mask (variation)
            response = await client.images.create_variation(
                image=main_image,
                n=1,
                size=size
            )
        
        if not response.data or len(response.data) == 0:
            raise ValueError("No image generated in response")
        
        return response.data[0].url
        
    except Exception as e:
        logger.error(f"Image editing failed: {str(e)}")
        raise ValueError(f"Image editing failed: {str(e)}")
