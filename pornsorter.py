import argparse
import collections
import math
import os
import re
import shutil
import sys

from PIL import Image

# Magic bytes, so we only try processing images
sig_size = 16           # Maximum signature size to look for, in bytes
magic_bytes = [
    b'\xff\xd8',        # JPEG
    b'\x89PNG\r\n\x1a'  # PNG
]
# TODO: Add WEBP/VP8 image support. Bytes 0-3 = 'RIFF', bytes 4-7 = variable (content len + 8?), 8-15 = 'WEBPVP8'


""" # Desired aspect ratios
desired_aspect = [
    (8, 5),     # 16:10
    (16, 9),    # 16:9
    (21, 9),    # 21:9
    (32, 9),    # 32:9
] """


def setup() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('src', type=str, help='Source directory to process.')

    # Mode selector
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--dst', type=str, help='Target directory for all matched files.')
    mode.add_argument('--list_sigs', action='store_true', help='Scan all files and list file signatures. Useful for adding missing types to magic_bytes list.')

    # Minimum resolution
    parser.add_argument('--min_x', type=int, default=1920, help='Minimum resolution to include in results. (Default: 1920)')
    parser.add_argument('--min_y', type=int, default=1080, help='Minimum resolution to include in results. (Default: 1080)')

    parser.add_argument('--aspect', type=str, nargs='+', default=['16:9'], help='Aspect ratios to match, separated by spaces. (e.g.: "--aspect 16:10 32:9") If this is not specified, only 16:9 images will be matched by default.')
    parser.add_argument('--copy_only', action='store_true', help='Used in conjunction with --dst, will not remove files from src.')
    return parser.parse_args()


def enumerate_files(path: str) -> list:
    dirs = []
    for root, _, file_list in os.walk(path):
        for f in file_list:
            dirs.append(os.path.join(root, f))
    return dirs


def get_sig(path) -> str:
    with open(path, 'rb') as fd:
        sig = fd.read(sig_size)
    return sig


# Main segment
args = setup()

# Mode switch
# --dst logic
if args.dst:
    # Build aspect list
    desired_aspect = []
    for aspect in args.aspect:
        if re.match('^\d+:\d+$', aspect) is None:
            print(f"Invalid --aspect parameter provided: {aspect}")
            sys.exit(1)
        else:
            desired_aspect.append(tuple([int(i) for i in aspect.split(':')]))

    # Build matched file list
    matches = []
    for path in enumerate_files(args.src):
        sig = get_sig(path)
        with open(path, 'rb') as fd:
            if any([sig.startswith(byte_pattern) for byte_pattern in magic_bytes]):
                img = Image.open(fd)
                x, y = img.size[0], img.size[1]
                gcd = math.gcd(x, y)
                aspect = (int(x / gcd), int(y / gcd))
                if aspect in desired_aspect:
                    if x < args.min_x or y < args.min_y:
                        print(f"Smaller than minimum resolution: {path} ({x}x{y})")
                    else:
                        print(f"OK: {path} {aspect}")
                        matches.append(path)
    # Relocate files as necessary
    for path in matches:
        # Strip the src dir from the matched file path, so we can create dirs as needed in dst.
        filesubdir = os.path.split(path)[0][len(args.src):]
        filename = os.path.split(path)[1]
        if not os.path.isdir(os.path.join(args.dst, filesubdir)):
            os.mkdir(os.path.join(args.dst, filesubdir))
        
        # Default operation is copy2 (data+metadata)
        if not args.copy_only:
            shutil.move(path, os.path.join(args.dst, filesubdir, filename))
        else:
            shutil.copy2(path, os.path.join(args.dst, filesubdir, filename))

# --list_sigs logic
elif args.list_sigs:
    dict_file_sigs = collections.defaultdict(list)
    for path in enumerate_files(args.src):
        dict_file_sigs[get_sig(path)].append(path)
    for sig in sorted(dict_file_sigs.keys()):
        print(f"{sig} ({len(dict_file_sigs[sig])} entries):")
        for path in sorted(dict_file_sigs[sig]):
            print(path)
        print('-' * 40)

else:
    print('???')
    sys.exit(1)
