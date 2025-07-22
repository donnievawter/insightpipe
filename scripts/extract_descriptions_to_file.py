import os
import subprocess

image_dir = "/Volumes/T54T/processed"
output_file = "/Users/crow/metadata_descriptions.txt"

with open(output_file, "w") as out:
    for filename in sorted(os.listdir(image_dir)):
        if filename.lower().endswith((".jpg", ".png", ".tiff", ".orf")):
            filepath = os.path.join(image_dir, filename)
            # Use exiftool to extract Description field
            result = subprocess.run(["exiftool", "-Description", filepath], capture_output=True, text=True)
            description = result.stdout.strip().split(": ", 1)[-1] if ": " in result.stdout else "No description"
            out.write(f"{filename}\t{description}\n")
