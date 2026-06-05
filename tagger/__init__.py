import subprocess
import os

def tag_image(path, model, timestamp, description=None, keywords=None, title=None):
    """Write all metadata to image in a single exiftool call.
    
    Args:
        path: Path to the image file
        model: Model name used for inference
        timestamp: Timestamp for DateTimeOriginal
        description: Optional description text to write to Description field
        keywords: Optional list of keyword strings to write to Keywords/Subject fields
        title: Optional title text to write to Title field
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    
    args = [
        "/usr/bin/exiftool",
        "-m",  # Ignore minor errors (e.g., DNG preview issues)
        "-Headline=InsightPipe Inference",
        f"-IPTC:Writer-Editor={model}",
        f"-DateTimeOriginal={timestamp}",
        "-overwrite_original"
    ]

    # Write keywords if provided
    if keywords:
        for kw in keywords:
            args.append(f"-IPTC:Keywords={kw}")
            args.append(f"-XMP-dc:Subject={kw}")
    
    # Write description if provided
    if description:
        args.append(f"-Description={description}")
    
    # Write title if provided
    if title:
        args.append(f"-XMP-dc:Title={title}")

    args.append(path)
    subprocess.run(args)
  