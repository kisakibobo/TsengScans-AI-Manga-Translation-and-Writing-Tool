import os

from dotenv import load_dotenv
load_dotenv("api.env")
print("Loaded API key:", os.getenv("OPENAI_API_KEY"))

from openai import OpenAI
import base64
from pathlib import Path


# === CONFIGURATION ===
MODEL = "gpt-4o"
IMAGE_PATH = "panels/page_005.png"  # Only used for standalone script runs

# === FUNCTION: Encode image to base64 ===
def encode_image(image_path):
    image_bytes = Path(image_path).read_bytes()
    return base64.b64encode(image_bytes).decode("utf-8")

# === FUNCTION: Use GPT-4 to detect + translate text ===
def extract_and_translate_text(image_path):
    base64_image = encode_image(image_path)
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "You're a professional Japanese manga translator. "
                            "Carefully examine the manga panel image below. "
                            "Return the full Japanese text *as it appears* in the panel, "
                            "then provide a natural English translation for each line.\n\n"
                            "Format your response as a JSON array like this:\n"
                            "[\n"
                            "  {\"jp\": \"Japanese sentence\", \"en\": \"English translation\"},\n"
                            "  ...\n"
                            "]\n\n"
                            "Do not skip any bubbles or captions."
                        )
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}",
                            "detail": "high"
                        }
                    }
                ]
            }
        ],
        max_tokens=2048
    )
    content = response.choices[0].message.content
    if content is not None:
        return content.strip()
    else:
        return "[No content returned by GPT-4]"

# === MAIN EXECUTION ===
if __name__ == "__main__":
    print(f"Analyzing image: {IMAGE_PATH}")
    result = extract_and_translate_text(IMAGE_PATH)
    
    print("\n=== GPT-4 Output ===\n")
    print(result)

    # Optional: Save to file
    output_path = "output/page_005.json"
    os.makedirs("output", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result)
    print(f"\nSaved output to {output_path}")
