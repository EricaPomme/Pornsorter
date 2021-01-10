import os
import sys
from PIL import Image
import math
import shutil

# Magic bytes, so we only try processing images
magic_bytes = [
    b'\xff\xd8',
    b'\x89PNG\r\n\x1a'
]

# Desired aspect ratios
desired_aspect = [
    (8, 5),     # 16:10
    (16, 9),    # 16:9
    (21, 9),    # 21:9
    (32, 9),    # 32:9
]

# Minimum acceptable resolution
min_x = 1920
min_y = 1080

if len(sys.argv) < 3:
    print(f"Usage: {sys.argv[0]} <dir to process> <dir to move acceptable files to>")
    sys.exit(1)

if not os.path.isdir(sys.argv[1]):
    print(f"Source dir ({sys.argv[1]}) not found.")
    sys.exit(2)

if not os.path.isdir(sys.argv[2]):
    print(f"Target dir ({sys.argv[2]}) not found.")
    sys.exit(4)

for root, dir_list, file_list in os.walk(sys.argv[1]):
    for f in file_list:
        path = os.path.join(root, f)
        fd = open(path, 'rb')
        startbytes = fd.read(32)
        if any([startbytes.startswith(byte_pattern) for byte_pattern in magic_bytes]):
            img = Image.open(fd)
            x, y = img.size[0], img.size[1]
            fd.close()
            gcd = math.gcd(x, y)
            aspect = (int(x/gcd), int(y/gcd))
            if aspect in desired_aspect:
                if x < min_x or y < min_y:
                    print(f"Smaller than minimum resolution: {path} ({x}x{y})")
                else:
                    print(f"OK: {path} {aspect}")
                    shutil.move(path, sys.argv[2])
            else:
                # Ignore files that don't fit our requirements
                continue
        else:
            fd.close()
            print(f"Unrecognized file signature: {startbytes} in {path}")
