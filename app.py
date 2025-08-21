from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import base64
from main import extract_and_translate_text

# Optional: Import image enhancement functions
try:
    from image_enhancer import enhance_image_from_base64
    IMAGE_ENHANCEMENT_AVAILABLE = True
except ImportError:
    IMAGE_ENHANCEMENT_AVAILABLE = False
    print("Image enhancement not available. Install Pillow, numpy, and opencv-python for enhanced processing.")

app = Flask(__name__)
CORS(app)

def clean_gpt_response(result):
    """Clean GPT response that might be wrapped in markdown code blocks"""
    result = result.strip()
    
    # Remove markdown code block markers
    if result.startswith('```json'):
        result = result[7:]  # Remove ```json
    elif result.startswith('```'):
        result = result[3:]  # Remove ```
    
    if result.endswith('```'):
        result = result[:-3]  # Remove trailing ```
    
    return result.strip()

@app.route('/api/translate', methods=['POST'])
def translate_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    print(f"Received file: {file.filename}")
    
    # Save temporarily
    temp_path = f"temp_{file.filename}"
    file.save(temp_path)
    print(f"Saved file to: {temp_path}")
    
    try:
        # Use your existing GPT function
        print("Calling extract_and_translate_text...")
        result = extract_and_translate_text(temp_path)
        print(f"GPT result: {result}")
        
        # Check if result is empty or None
        if not result or result.strip() == "":
            return jsonify({'error': 'No text detected in image'}), 400
        
        # Check if GPT refused to process the content
        if any(phrase in result.lower() for phrase in [
            "i'm sorry", "i can't", "unable to", "cannot assist", 
            "can't assist", "won't assist", "refuse to", "not allowed"
        ]):
            return jsonify({'error': 'GPT refused to process this content. Try cropping individual speech bubbles instead.'}), 400
        
        # Clean the response and try to parse the JSON
        cleaned_result = clean_gpt_response(result)
        print(f"Cleaned result: {cleaned_result}")
        
        try:
            translations = json.loads(cleaned_result)
            print(f"Parsed translations: {translations}")
            return jsonify(translations)
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Raw result: {repr(result)}")
            return jsonify({'error': f'Invalid response from GPT. Try cropping individual speech bubbles instead.'}), 500
            
    except Exception as e:
        print(f"Error in translation: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
            print(f"Cleaned up: {temp_path}")

@app.route('/api/translate-crop', methods=['POST'])
def translate_cropped_image():
    """Translate a cropped speech bubble from base64 image data"""
    data = request.get_json()
    image_b64 = data.get('image')

    if not image_b64:
        return jsonify({'error': 'No image data provided'}), 400

    print("Received cropped image for translation")

    try:
        # Handle both data URLs and raw base64
        if image_b64.startswith('data:image'):
            image_data = base64.b64decode(image_b64.split(",")[-1])
        else:
            image_data = base64.b64decode(image_b64)
        
        temp_path = "temp_crop.png"
        with open(temp_path, "wb") as f:
            f.write(image_data)
        
        print(f"Saved cropped image to: {temp_path}")
        print(f"Cropped image size: {len(image_data)} bytes")

        # Optionally enhance the image server-side for better text recognition
        if IMAGE_ENHANCEMENT_AVAILABLE:
            try:
                print("Applying server-side image enhancement...")
                enhanced_base64 = enhance_image_from_base64(image_b64)
                if enhanced_base64:
                    # Save enhanced version
                    enhanced_data = base64.b64decode(enhanced_base64)
                    enhanced_path = temp_path.replace('.png', '_enhanced.png')
                    with open(enhanced_path, "wb") as f:
                        f.write(enhanced_data)
                    print(f"Enhanced image saved to: {enhanced_path}")
                    # Use enhanced image for translation
                    result = extract_and_translate_text(enhanced_path)
                    # Clean up enhanced file
                    if os.path.exists(enhanced_path):
                        os.remove(enhanced_path)
                else:
                    # Fallback to original image
                    result = extract_and_translate_text(temp_path)
            except Exception as e:
                print(f"Image enhancement failed: {e}")
                # Fallback to original image
                result = extract_and_translate_text(temp_path)
        else:
            result = extract_and_translate_text(temp_path)
        print(f"Crop GPT result: {result}")
        
        if not result or result.strip() == "":
            return jsonify({'error': 'No text detected in cropped area. Try selecting a larger area with more context.'}), 400
        
        # Check if GPT refused to process the content
        if any(phrase in result.lower() for phrase in [
            "i'm sorry", "i can't", "unable to", "cannot assist", 
            "can't assist", "won't assist", "refuse to", "not allowed",
            "no visible text", "does not contain", "cannot process"
        ]):
            return jsonify({'error': 'GPT could not detect text in this area. Try selecting a different speech bubble or a larger area.'}), 400
        
        cleaned = clean_gpt_response(result)
        print(f"Crop cleaned result: {cleaned}")
        
        try:
            translations = json.loads(cleaned)
            print(f"Crop parsed translations: {translations}")
            
            if not translations or len(translations) == 0:
                return jsonify({'error': 'No translations found in the selected area. Try a different speech bubble.'}), 400
                
            return jsonify(translations)
        except json.JSONDecodeError as e:
            print(f"Crop JSON parsing error: {e}")
            print(f"Crop raw result: {repr(result)}")
            return jsonify({'error': 'Invalid response from GPT. Try selecting a different area.'}), 500
            
    except Exception as e:
        print(f"Error in crop translation: {str(e)}")
        return jsonify({'error': f'Processing error: {str(e)}'}), 500
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
            print(f"Cleaned up: {temp_path}")

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, port=5000) 