import rawpy
import imageio
import os

def convert_orf_to_jpg(orf_path):
    with rawpy.imread(orf_path) as raw:
        rgb = raw.postprocess()
    jpg_path = os.path.splitext(orf_path)[0] + ".jpg"
    imageio.imwrite(jpg_path, rgb, format='JPEG')
    return jpg_path
foo="/Volumes/T54T/bridgeiso/2025/2025-07-12/_OM16275.ORF"
bar=convert_orf_to_jpg(foo)
print(bar)