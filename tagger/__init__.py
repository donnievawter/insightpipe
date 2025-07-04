import subprocess

def tag_image(path, description, model, timestamp):
    subprocess.run([
        "exiftool",
        f"-ImageDescription={description}",
        f"-UserComment=Tagged by InsightPipe using model: {model}",
        f"-DateTimeOriginal={timestamp}",
        "-overwrite_original",
        path
    ])

