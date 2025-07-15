import subprocess
import os

def tag_image(path, description, model, timestamp, prompt=None, keywords=False):
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    
    args = [
        "/usr/local/bin/exiftool",
        "-Headline=InsightPipe Inference",
        f"-IPTC:Writer-Editor={model}",
        f"-DateTimeOriginal={timestamp}",
        "-overwrite_original"
    ]

    if keywords:
        keywords_list = [kw.strip() for kw in description.split(",")]
        args.extend([f"-IPTC:Keywords={kw}" for kw in keywords_list])
        args.extend([f"-XMP-dc:Subject={kw}" for kw in keywords_list])
        # Intentionally skip storing the prompt (it's `keywordprompt`, not useful)
    else:
        args.append(f"-Description={description}")
        if prompt:
            args.append(f"-XMP-dc:Title={prompt}")

    args.append(path)
    subprocess.run(args)
