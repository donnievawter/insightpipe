import subprocess
import os

def tag_image(path, description, model, timestamp, prompt=None,keywords=False):
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    args = [
    "exiftool",
    "-Headline=InsightPipe Inference",
    f"-IPTC:Writer-Editor={model}",
    f"-DateTimeOriginal={timestamp}",
    "-overwrite_original"
]

    if keywords:
        keywords_list = [kw.strip() for kw in description.split(",")]
        args.extend([f"-IPTC:Keywords={kw}" for kw in keywords_list])

    else:
        args.append(f"-Description={description}")
        args.append(f"-Subject={prompt}")    # prompt only relevant in description mode

    args.append(path)
    subprocess.run(args)

  