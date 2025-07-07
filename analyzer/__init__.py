import requests
import base64
import time

def analyze_image(path, model, url,  prompt="What do you see in this image?",retries=3 ,timeout=120):
    with open(path, "rb") as img:
        encoded = base64.b64encode(img.read()).decode("utf-8")

    payload = {
        "model": model,
        "prompt": prompt,
        "images": [encoded],
        "stream": False
    }

    for attempt in range(1, retries + 1):
        try:
            response = requests.post(url, json=payload, timeout=timeout)
            if response.status_code != 200:
                print(f"🟡 Attempt {attempt}: Bad response status {response.status_code}")
                time.sleep(5)
                continue

            desc = response.json().get("response", "").strip()
            if desc:
                return desc
            print(f"🟡 Attempt {attempt}: No response content")
        except Exception as e:
            print(f"🔴 Attempt {attempt} failed: {e}")

        time.sleep(5)

    return "No description generated after retries"
