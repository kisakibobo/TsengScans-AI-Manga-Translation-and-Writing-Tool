#!/usr/bin/env python3
"""
Test script for image enhancement functionality.
This script demonstrates the enhanced image processing for manga text recognition.
"""

import os
import sys
from pathlib import Path

def test_enhancement():
    """Test the image enhancement on a sample image"""
    
    # Check if we have the required dependencies
    try:
        from image_enhancer import enhance_manga_text
        print("✅ Image enhancement module loaded successfully")
    except ImportError as e:
        print(f"❌ Failed to load image enhancement: {e}")
        print("Install dependencies with: pip install Pillow numpy opencv-python")
        return False
    
    # Look for test images
    test_images = []
    
    # Check panels directory
    panels_dir = Path("panels")
    if panels_dir.exists():
        for img_file in panels_dir.glob("*.png"):
            test_images.append(str(img_file))
    
    # Check current directory
    for img_file in Path(".").glob("*.png"):
        if "enhanced" not in img_file.name:  # Skip already enhanced images
            test_images.append(str(img_file))
    
    if not test_images:
        print("❌ No test images found!")
        print("Please place a PNG image in the 'panels' directory or current directory")
        return False
    
    print(f"📁 Found {len(test_images)} test image(s):")
    for img in test_images:
        print(f"   - {img}")
    
    # Test enhancement on first image
    test_image = test_images[0]
    print(f"\n🔧 Testing enhancement on: {test_image}")
    
    try:
        # Apply enhancement
        enhanced = enhance_manga_text(test_image)
        
        # Save enhanced version
        output_path = test_image.replace('.png', '_enhanced.png')
        enhanced.save(output_path, 'PNG', quality=95)
        
        print(f"✅ Enhancement completed!")
        print(f"📄 Original: {test_image}")
        print(f"📄 Enhanced: {output_path}")
        print(f"📊 Size comparison:")
        
        # Get file sizes
        original_size = os.path.getsize(test_image)
        enhanced_size = os.path.getsize(output_path)
        
        print(f"   Original: {original_size:,} bytes")
        print(f"   Enhanced: {enhanced_size:,} bytes")
        print(f"   Ratio: {enhanced_size/original_size:.1f}x larger")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhancement failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Manga Text Enhancement")
    print("=" * 40)
    
    success = test_enhancement()
    
    if success:
        print("\n✅ Test completed successfully!")
        print("💡 The enhanced image should have much clearer text for GPT to read.")
    else:
        print("\n❌ Test failed!")
        print("🔧 Make sure you have the required dependencies installed.")
        sys.exit(1)
