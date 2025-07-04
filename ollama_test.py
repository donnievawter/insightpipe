import base64
import requests
import sys

# === Usage: python ollama_test.py /path/to/image.jpg ===

def encode_image_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

def send_to_ollama(img_base64, model="llava", prompt="Describe this image"):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "images": [img_base64],
        "stream": False  # 👈 disable streaming mode for one JSON response
    }
    response = requests.post(url, json=payload)
    return response.json()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python ollama_test.py /path/to/image.jpg")
        sys.exit(1)

    img_path = sys.argv[1]
    img_data = encode_image_base64(img_path)
    result = send_to_ollama(img_data)
    print(result.get("response", "No response received"))
