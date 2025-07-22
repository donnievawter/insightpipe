import os
import shutil
import sys

def copy_files(source, destination):
    # check if source exists and is a directory
    if not os.path.exists(source) or not os.path.isdir(source):
        raise Exception(f"Source {source} does not exist or is not a directory")

    # check if destination exists and is a directory
    if not os.path.exists(destination) or not os.path.isdir(destination):
        raise Exception(f"Destination {destination} does not exist or is not a directory")

    # walk the source directory and copy all files to the root of the destination directory
    #image_extensions = [".jpg", ".jpeg", ".png", ".tif", ".tiff", ".orf"]
    image_extensions = [ ".orf"]
    for root, dirs, files in os.walk(source):
        for filename in files:
            source_path = os.path.join(root, filename)
            destination_path = os.path.join(destination, filename)
            if any(filename.lower().endswith(ext) for ext in image_extensions):
                shutil.copy2(source_path, destination_path)


if __name__ == "__main__":
    # set default values for source and destination
    source = "/Volumes/OM SYSTEM"
    destination = "/Volumes/T54T/ready_to_process"

    # check if cli arguments were provided to override defaults
    if len(sys.argv) >= 3:
        source = sys.argv[1]
        destination = sys.argv[2]

    try:
        copy_files(source, destination)
        print(f"All files copied from {source} to {destination}")
    except Exception as e:
        print(e)