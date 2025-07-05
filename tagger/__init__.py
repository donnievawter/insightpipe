import subprocess
import os

def tag_image(path, description, model, timestamp, prompt):
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    
    subprocess.run([
        "exiftool",
        f"-Headline=InsightPipe Inference",
        f"-Description={description}",
        f"-IPTC:Writer-Editor={model}",
        f"-Subject={prompt}", 
        f"-DateTimeOriginal={timestamp}",
        "-overwrite_original",
        path
    ])
