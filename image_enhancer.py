from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
import cv2
import io
import base64

def enhance_manga_text(image_path, output_path=None):
    """
    Enhanced image processing specifically for manga text recognition.
    Applies multiple techniques to improve text clarity for OCR/GPT.
    """
    # Load image
    img = Image.open(image_path)
    
    # Convert to RGB if necessary
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Step 1: Resize for better processing (4x enlargement)
    width, height = img.size
    img = img.resize((width * 4, height * 4), Image.Resampling.LANCZOS)
    
    # Step 2: Convert to grayscale for text processing
    gray = img.convert('L')
    
    # Step 3: Apply contrast enhancement
    enhancer = ImageEnhance.Contrast(gray)
    gray = enhancer.enhance(2.0)  # Increase contrast
    
    # Step 4: Apply brightness adjustment
    enhancer = ImageEnhance.Brightness(gray)
    gray = enhancer.enhance(1.2)  # Slightly increase brightness
    
    # Step 5: Apply sharpening
    gray = gray.filter(ImageFilter.SHARPEN)
    gray = gray.filter(ImageFilter.SHARPEN)  # Apply twice for stronger effect
    
    # Step 6: Apply threshold for binary text
    # Convert to numpy array for processing
    img_array = np.array(gray)
    
    # Apply adaptive thresholding
    # This works better than simple thresholding for varying lighting
    if cv2 is not None:
        # Use OpenCV for adaptive thresholding if available
        img_cv = cv2.cvtColor(img_array, cv2.COLOR_GRAY2BGR)
        gray_cv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(
            gray_cv, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        # Convert back to PIL
        enhanced = Image.fromarray(thresh)
    else:
        # Fallback to simple thresholding
        threshold = 150
        enhanced = gray.point(lambda x: 0 if x < threshold else 255, '1')
    
    # Step 7: Add border for better definition
    border_size = 2
    enhanced = Image.new('RGB', (enhanced.width + 2*border_size, enhanced.height + 2*border_size), 'white')
    enhanced.paste(enhanced, (border_size, border_size))
    
    # Step 8: Convert back to RGB for consistency
    enhanced = enhanced.convert('RGB')
    
    # Save if output path provided
    if output_path:
        enhanced.save(output_path, 'PNG', quality=95)
    
    return enhanced

def enhance_image_from_base64(base64_data, output_path=None):
    """
    Enhance image from base64 data (for web API use)
    """
    try:
        # Decode base64 data
        if base64_data.startswith('data:image'):
            # Remove data URL prefix
            base64_data = base64_data.split(',')[1]
        
        image_data = base64.b64decode(base64_data)
        
        # Create image from bytes
        img = Image.open(io.BytesIO(image_data))
        
        # Apply enhancement
        enhanced = enhance_manga_text(img, output_path)
        
        # Convert back to base64
        buffer = io.BytesIO()
        enhanced.save(buffer, format='PNG', quality=95)
        enhanced_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return enhanced_base64
        
    except Exception as e:
        print(f"Error enhancing image: {e}")
        return None

if __name__ == "__main__":
    # Test the enhancement
    import sys
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
        output_path = input_path.replace('.png', '_enhanced.png')
        enhanced = enhance_manga_text(input_path, output_path)
        print(f"Enhanced image saved to: {output_path}")
    else:
        print("Usage: python image_enhancer.py <input_image_path>")
