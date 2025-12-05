"""
Image processing service.
OpenCV-based image transformation pipelines for cartoon effects.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional
import logging

from app.models.image_job import ImageStyle
from app.config import settings

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Image processing class with various cartoon effect methods."""
    
    @staticmethod
    def load_image(image_path: str) -> np.ndarray:
        """Load an image from file path."""
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image from {image_path}")
        return image
    
    @staticmethod
    def save_image(image: np.ndarray, output_path: str, quality: int = 85) -> str:
        """Save an image to file path."""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Determine format based on extension
        ext = Path(output_path).suffix.lower()
        if ext in ['.jpg', '.jpeg']:
            cv2.imwrite(output_path, image, [cv2.IMWRITE_JPEG_QUALITY, quality])
        elif ext == '.png':
            cv2.imwrite(output_path, image, [cv2.IMWRITE_PNG_COMPRESSION, 9 - quality // 12])
        else:
            cv2.imwrite(output_path, image)
        
        return output_path
    
    @staticmethod
    def resize_if_needed(image: np.ndarray, max_dimension: int = None) -> np.ndarray:
        """Resize image if it exceeds max dimension while maintaining aspect ratio."""
        if max_dimension is None:
            max_dimension = settings.MAX_IMAGE_DIMENSION
            
        h, w = image.shape[:2]
        if max(h, w) <= max_dimension:
            return image
        
        if h > w:
            new_h = max_dimension
            new_w = int(w * (max_dimension / h))
        else:
            new_w = max_dimension
            new_h = int(h * (max_dimension / w))
        
        return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    @staticmethod
    def cartoon_effect(image: np.ndarray, params: Optional[Dict[str, Any]] = None) -> np.ndarray:
        """
        Apply cartoon effect to an image.
        
        Steps:
        1. Convert to grayscale
        2. Apply median blur
        3. Use adaptive threshold for edges
        4. Apply bilateral filter on color image
        5. Combine edges and filtered color image
        """
        # Default parameters
        p = {
            'blur_kernel_size': 7,
            'threshold_block_size': 9,
            'threshold_c': 9,
            'bilateral_d': 9,
            'bilateral_sigma_color': 200,
            'bilateral_sigma_space': 200,
        }
        if params:
            p.update(params)
        
        # Ensure kernel sizes are odd
        p['blur_kernel_size'] = p['blur_kernel_size'] | 1
        p['threshold_block_size'] = p['threshold_block_size'] | 1
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply median blur
        gray_blur = cv2.medianBlur(gray, p['blur_kernel_size'])
        
        # Detect edges using adaptive threshold
        edges = cv2.adaptiveThreshold(
            gray_blur,
            255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY,
            p['threshold_block_size'],
            p['threshold_c']
        )
        
        # Apply bilateral filter to smooth colors while keeping edges sharp
        color = cv2.bilateralFilter(
            image,
            p['bilateral_d'],
            p['bilateral_sigma_color'],
            p['bilateral_sigma_space']
        )
        
        # Combine edges with color image
        cartoon = cv2.bitwise_and(color, color, mask=edges)
        
        return cartoon
    
    @staticmethod
    def pencil_sketch_effect(image: np.ndarray, params: Optional[Dict[str, Any]] = None) -> np.ndarray:
        """
        Apply pencil sketch effect to an image.
        
        Steps:
        1. Convert to grayscale
        2. Invert the grayscale image
        3. Apply Gaussian blur
        4. Blend using color dodge
        """
        # Default parameters
        p = {
            'blur_kernel_size': 21,
            'invert': True,
        }
        if params:
            p.update(params)
        
        # Ensure kernel size is odd
        p['blur_kernel_size'] = p['blur_kernel_size'] | 1
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Invert grayscale
        inverted = 255 - gray
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(inverted, (p['blur_kernel_size'], p['blur_kernel_size']), 0)
        
        # Color dodge blend
        sketch = cv2.divide(gray, 255 - blurred, scale=256)
        
        if not p['invert']:
            sketch = 255 - sketch
        
        # Convert back to BGR for consistency
        sketch_bgr = cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)
        
        return sketch_bgr
    
    @staticmethod
    def color_pencil_effect(image: np.ndarray, params: Optional[Dict[str, Any]] = None) -> np.ndarray:
        """
        Apply color pencil effect by blending sketch with original colors.
        
        Steps:
        1. Create pencil sketch
        2. Blend with original color image using weighted addition
        """
        # Default parameters
        p = {
            'sketch_weight': 0.7,
            'color_weight': 0.3,
            'blur_kernel_size': 21,
        }
        if params:
            p.update(params)
        
        # Create sketch
        sketch_params = {'blur_kernel_size': p['blur_kernel_size']}
        sketch = ImageProcessor.pencil_sketch_effect(image, sketch_params)
        
        # Blend sketch with original colors
        color_pencil = cv2.addWeighted(
            sketch, p['sketch_weight'],
            image, p['color_weight'],
            0
        )
        
        return color_pencil
    
    @staticmethod
    def oil_painting_effect(image: np.ndarray, params: Optional[Dict[str, Any]] = None) -> np.ndarray:
        """
        Apply oil painting effect using stylization.
        """
        # Default parameters
        p = {
            'sigma_s': 60,
            'sigma_r': 0.6,
        }
        if params:
            p.update(params)
        
        # Apply stylization filter
        oil_painting = cv2.stylization(
            image,
            sigma_s=p['sigma_s'],
            sigma_r=p['sigma_r']
        )
        
        return oil_painting
    
    @staticmethod
    def watercolor_effect(image: np.ndarray, params: Optional[Dict[str, Any]] = None) -> np.ndarray:
        """
        Apply watercolor effect using edge-preserving filter.
        """
        # Default parameters
        p = {
            'sigma_s': 60,
            'sigma_r': 0.4,
        }
        if params:
            p.update(params)
        
        # Apply edge-preserving filter
        watercolor = cv2.edgePreservingFilter(
            image,
            flags=cv2.RECURS_FILTER,
            sigma_s=p['sigma_s'],
            sigma_r=p['sigma_r']
        )
        
        return watercolor
    
    @staticmethod
    def pop_art_effect(image: np.ndarray, params: Optional[Dict[str, Any]] = None) -> np.ndarray:
        """
        Apply pop art effect by posterizing and enhancing colors.
        """
        # Default parameters
        p = {
            'num_colors': 8,
            'saturation_boost': 1.5,
        }
        if params:
            p.update(params)
        
        # Convert to HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
        
        # Boost saturation
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * p['saturation_boost'], 0, 255)
        
        # Convert back to BGR
        hsv = hsv.astype(np.uint8)
        boosted = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
        # Posterize (reduce colors)
        div = 256 // p['num_colors']
        posterized = (boosted // div) * div + div // 2
        
        return posterized
    
    @classmethod
    def process_image(
        cls,
        input_path: str,
        output_path: str,
        style: ImageStyle,
        params: Optional[Dict[str, Any]] = None,
        quality: int = None
    ) -> str:
        """
        Main method to process an image with the specified style.
        """
        if quality is None:
            quality = settings.DEFAULT_OUTPUT_QUALITY
        
        logger.info(f"Processing image: {input_path} with style: {style}")
        
        # Load and resize image if needed
        image = cls.load_image(input_path)
        image = cls.resize_if_needed(image)
        
        # Apply the appropriate effect
        style_methods = {
            ImageStyle.CARTOON: cls.cartoon_effect,
            ImageStyle.SKETCH: cls.pencil_sketch_effect,
            ImageStyle.COLOR_PENCIL: cls.color_pencil_effect,
            ImageStyle.OIL_PAINTING: cls.oil_painting_effect,
            ImageStyle.WATERCOLOR: cls.watercolor_effect,
            ImageStyle.POP_ART: cls.pop_art_effect,
        }
        
        method = style_methods.get(style)
        if not method:
            raise ValueError(f"Unknown style: {style}")
        
        processed = method(image, params)
        
        # Save and return output path
        output_path = cls.save_image(processed, output_path, quality)
        logger.info(f"Processed image saved to: {output_path}")
        
        return output_path
