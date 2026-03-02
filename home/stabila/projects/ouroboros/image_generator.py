#!/usr/bin/env python3
"""
Image Generator using Hugging Face Diffusers
Free and open-source image generation without API keys
"""

import torch
from diffusers import DiffusionPipeline
import base64
import io
from PIL import Image

def generate_image(prompt: str, width: int = 1920, height: int = 1080):
    """
    Generate image using Stable Diffusion
    
    Args:
        prompt (str): Text prompt for image generation
        width (int): Image width (default: 1920)
        height (int): Image height (default: 1080)
    
    Returns:
        PIL.Image: Generated image
    """
    try:
        # Load the Stable Diffusion XL pipeline
        pipe = DiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0", torch_dtype=torch.float16)
        
        # Move to GPU if available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        pipe = pipe.to(device)
        
        # Generate image
        image = pipe(prompt, width=width, height=height, num_inference_steps=50).images[0]
        
        return image
        
    except Exception as e:
        print(f"Error generating image: {e}")
        return None

def save_image(image, filename: str):
    """Save image to file"""
    image.save(filename)
    print(f"Image saved to {filename}")

def generate_images_series(prompts: list, output_dir: str = "images"):
    """
    Generate a series of images for video content
    
    Args:
        prompts (list): List of prompts for image generation
        output_dir (str): Directory to save images
    """
    import os
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    for i, prompt in enumerate(prompts):
        print(f"Generating image {i+1}/{len(prompts)}: {prompt}")
        image = generate_image(prompt)
        if image:
            filename = f"{output_dir}/image_{i+1:03d}.png"
            save_image(image, filename)
        else:
            print(f"Failed to generate image {i+1}")

if __name__ == "__main__":
    # Example usage
    prompts = [
        "Современный умный дом для новичков, уютный интерьер с умными технологиями, стильный дизайн, качественная иллюстрация, понятная визуализация",
        "Умный дом с системой автоматизации, комфортный интерьер, современные технологии",
        "Интерьер умного дома, голосовое управление, умное освещение, климат-контроль",
        "Безопасность умного дома, камеры наблюдения, система контроля доступа",
        "Энергосбережение в умном доме, умные розетки, автоматическое управление освещением"
    ]
    
    generate_images_series(prompts)