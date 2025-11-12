"""Pydantic models for image generation and editing."""

from typing import Any
from pydantic import BaseModel, Field


class ImageGenerationInput(BaseModel):
    """Input model for image generation."""
    prompt: str = Field(..., description="The text description of the image to generate")
    size: str = Field(default="1024x1024", description="The size of the image ('1024x1024', '1024x1536', '1536x1024')")
    quality: str = Field(default="standard", description="The quality of the image ('standard', 'hd')")
    model: str = Field(default="gpt-image-1", description="The model to use ('gpt-image-1', 'dall-e-3')")
    images: list[str] = Field(default_factory=list, description="List of reference images as URLs or base64 encoded strings (empty list for no references)")


class ImageEditInput(BaseModel):
    """Input model for image editing."""
    prompt: str = Field(..., description="The text description of the edit to apply")
    images: list[str] = Field(..., description="List of images as URLs or base64 encoded strings - first is main image, rest are references")
    mask: str = Field(default="", description="Mask image as URL or base64 encoded string for selective editing (use empty string for no mask)")
    size: str = Field(default="1024x1024", description="The size of the image ('1024x1024', '1024x1536', '1536x1024')")
    model: str = Field(default="gpt-image-1", description="The model to use for editing ('gpt-image-1' or 'dall-e-3')")


class ImageResponse(BaseModel):
    """Response model for image operations."""
    success: bool = Field(description="Whether the operation was successful")
    prompt: str = Field(description="The prompt used for the operation")
    model: str = Field(description="The model used")
    size: str = Field(description="The image size")
    image_url: str | None = Field(default=None, description="URL of the generated/edited image")
    message: str = Field(description="Status message")
    error: str | None = Field(default=None, description="Error message if operation failed")


class ImageGenerationResponse(ImageResponse):
    """Response model for image generation."""
    quality: str = Field(description="The quality setting used")


class ImageEditResponse(ImageResponse):
    """Response model for image editing."""
    images_count: int = Field(description="Number of input images processed")
    mask_provided: bool = Field(description="Whether a mask was provided")
