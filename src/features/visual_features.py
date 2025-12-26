"""
Visual analysis features for screenshot intelligence
Includes SSIM, OCR, visual entropy, and UI change detection
"""

import numpy as np
from typing import Dict, Any, Optional, Tuple
from PIL import Image
import warnings

# Optional dependencies
try:
    from skimage.metrics import structural_similarity as ssim
    from skimage import img_as_float
    SKIMAGE_AVAILABLE = True
except ImportError:
    SKIMAGE_AVAILABLE = False

try:
    import pytesseract
    from ..utils.config import TESSERACT_PATH, OCR_LANGUAGE, OCR_ENABLED
    if TESSERACT_PATH:
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False
    OCR_ENABLED = False

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

from ..utils.logger import setup_logger
from ..utils.config import LOG_LEVEL, LOG_FILE

logger = setup_logger(__name__, LOG_FILE, LOG_LEVEL)


class VisualFeatureExtractor:
    """
    Extract visual intelligence features from screenshots
    
    Features:
    1. Image similarity (SSIM)
    2. Visual entropy
    3. OCR text extraction
    4. OCR text comparison
    5. UI change detection
    """
    
    def __init__(self):
        """Initialize visual feature extractor"""
        self.last_ocr_text = None
        
        # Check dependencies
        if not SKIMAGE_AVAILABLE:
            logger.warning("scikit-image not available - SSIM disabled")
        if not PYTESSERACT_AVAILABLE or not OCR_ENABLED:
            logger.warning("pytesseract not available or disabled - OCR disabled")
        if not CV2_AVAILABLE:
            logger.warning("opencv-python not available - some features disabled")
        
        logger.info("VisualFeatureExtractor initialized")
    
    def calculate_similarity(
        self, 
        img1: Image.Image, 
        img2: Image.Image
    ) -> float:
        """
        Calculate structural similarity between two images using SSIM
        
        Args:
            img1: First PIL Image
            img2: Second PIL Image
        
        Returns:
            Similarity score (0-1, higher = more similar)
        """
        if not SKIMAGE_AVAILABLE:
            return 0.0
        
        try:
            # Convert to grayscale numpy arrays
            gray1 = np.array(img1.convert('L'))
            gray2 = np.array(img2.convert('L'))
            
            # Resize to same dimensions if needed
            if gray1.shape != gray2.shape:
                gray2 = cv2.resize(gray2, (gray1.shape[1], gray1.shape[0]))
            
            # Calculate SSIM
            similarity = ssim(gray1, gray2)
            
            return float(similarity)
        
        except Exception as e:
            logger.error(f"Error calculating SSIM: {e}")
            return 0.0
    
    def calculate_visual_entropy(self, img: Image.Image) -> float:
        """
        Calculate visual entropy (complexity) of image
        
        Args:
            img: PIL Image
        
        Returns:
            Entropy score (0-8, higher = more complex/varied)
        """
        try:
            # Convert to grayscale
            gray = np.array(img.convert('L'))
            
            # Calculate histogram
            histogram, _ = np.histogram(gray, bins=256, range=(0, 256))
            
            # Normalize histogram
            histogram = histogram / histogram.sum()
            
            # Calculate entropy
            entropy = -np.sum(histogram * np.log2(histogram + 1e-10))
            
            return float(entropy)
        
        except Exception as e:
            logger.error(f"Error calculating visual entropy: {e}")
            return 0.0
    
    def extract_text(self, img: Image.Image) -> str:
        """
        Extract text from screenshot using OCR
        
        Args:
            img: PIL Image
        
        Returns:
            Extracted text string
        """
        if not PYTESSERACT_AVAILABLE or not OCR_ENABLED:
            return ""
        
        try:
            # Extract text
            text = pytesseract.image_to_string(
                img,
                lang=OCR_LANGUAGE,
                config='--psm 6'  # Assume uniform block of text
            )
            
            return text.strip()
        
        except Exception as e:
            logger.error(f"Error extracting OCR text: {e}")
            return ""
    
    def compare_text(self, text1: str, text2: str) -> float:
        """
        Compare similarity between two text strings
        
        Args:
            text1: First text
            text2: Second text
        
        Returns:
            Similarity ratio (0-1, higher = more similar)
        """
        if not text1 or not text2:
            return 0.0
        
        try:
            from difflib import SequenceMatcher
            
            # Calculate similarity ratio
            ratio = SequenceMatcher(None, text1, text2).ratio()
            
            return float(ratio)
        
        except Exception as e:
            logger.error(f"Error comparing text: {e}")
            return 0.0
    
    def calculate_ocr_change_ratio(
        self, 
        img1: Image.Image, 
        img2: Image.Image
    ) -> float:
        """
        Calculate how much OCR text has changed between two screenshots
        
        Args:
            img1: First PIL Image
            img2: Second PIL Image
        
        Returns:
            Change ratio (0-1, higher = more text change)
        """
        if not PYTESSERACT_AVAILABLE or not OCR_ENABLED:
            return 0.0
        
        try:
            text1 = self.extract_text(img1)
            text2 = self.extract_text(img2)
            
            if not text1 and not text2:
                return 0.0
            
            similarity = self.compare_text(text1, text2)
            change_ratio = 1.0 - similarity
            
            return float(change_ratio)
        
        except Exception as e:
            logger.error(f"Error calculating OCR change ratio: {e}")
            return 0.0
    
    def detect_ui_changes(
        self, 
        img1: Image.Image, 
        img2: Image.Image
    ) -> float:
        """
        Detect UI/visual changes between two screenshots
        
        Args:
            img1: First PIL Image
            img2: Second PIL Image
        
        Returns:
            Change score (0-1, higher = more UI changes)
        """
        if not CV2_AVAILABLE:
            return 0.0
        
        try:
            # Convert to numpy arrays
            arr1 = np.array(img1)
            arr2 = np.array(img2)
            
            # Resize if needed
            if arr1.shape != arr2.shape:
                arr2 = cv2.resize(arr2, (arr1.shape[1], arr1.shape[0]))
            
            # Calculate absolute difference
            diff = cv2.absdiff(arr1, arr2)
            
            # Calculate mean difference
            mean_diff = np.mean(diff) / 255.0
            
            return float(mean_diff)
        
        except Exception as e:
            logger.error(f"Error detecting UI changes: {e}")
            return 0.0
    
    def extract_visual_features(
        self, 
        screenshot1: Optional[Dict[str, Any]], 
        screenshot2: Optional[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Extract all visual features from a pair of screenshots
        
        Args:
            screenshot1: First screenshot dict (older)
            screenshot2: Second screenshot dict (newer)
        
        Returns:
            Dictionary of visual features
        """
        features = {
            'screen_similarity_score': 0.0,
            'visual_entropy': 0.0,
            'ocr_text_change_ratio': 0.0,
            'ui_change_score': 0.0,
        }
        
        # If no screenshots available, return zeros
        if not screenshot1 or not screenshot2:
            return features
        
        try:
            img1 = screenshot1['image']
            img2 = screenshot2['image']
            
            # Calculate similarity
            features['screen_similarity_score'] = self.calculate_similarity(img1, img2)
            
            # Calculate visual entropy (of latest screenshot)
            features['visual_entropy'] = self.calculate_visual_entropy(img2)
            
            # Calculate OCR text change
            features['ocr_text_change_ratio'] = self.calculate_ocr_change_ratio(img1, img2)
            
            # Detect UI changes
            features['ui_change_score'] = self.detect_ui_changes(img1, img2)
            
            logger.debug(f"Visual features: similarity={features['screen_similarity_score']:.3f}, "
                        f"entropy={features['visual_entropy']:.3f}, "
                        f"ocr_change={features['ocr_text_change_ratio']:.3f}")
        
        except Exception as e:
            logger.error(f"Error extracting visual features: {e}")
        
        return features


# Standalone test
if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    print("Testing VisualFeatureExtractor...")
    print(f"scikit-image available: {SKIMAGE_AVAILABLE}")
    print(f"pytesseract available: {PYTESSERACT_AVAILABLE}")
    print(f"opencv available: {CV2_AVAILABLE}")
    print()
    
    extractor = VisualFeatureExtractor()
    
    # Test with dummy images
    img1 = Image.new('RGB', (800, 600), color='white')
    img2 = Image.new('RGB', (800, 600), color='white')
    
    print("Testing with identical white images...")
    similarity = extractor.calculate_similarity(img1, img2)
    print(f"Similarity: {similarity:.3f} (should be ~1.0)")
    
    entropy = extractor.calculate_visual_entropy(img1)
    print(f"Visual entropy: {entropy:.3f}")
    
    # Test with different images
    img3 = Image.new('RGB', (800, 600), color='black')
    similarity2 = extractor.calculate_similarity(img1, img3)
    print(f"\nSimilarity (white vs black): {similarity2:.3f} (should be ~0.0)")
    
    print("\n✅ Visual feature extraction test complete")
