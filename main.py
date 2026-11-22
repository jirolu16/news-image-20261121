"""Entry point for the news-image-20261121 entry.

The deliverable is entry.png, the one-page newspaper of Saturday
21 November 2026 produced by gen_image.py. This script locates that
image beside itself, refuses to proceed if it is missing or larger
than 1 MiB, copies it into the directory named by the
MAKEFUN_OUTPUT_DIR environment variable (default /output) and then
verifies the copy before reporting success.
"""

import hashlib
import os
import shutil
import sys

ONE_MIB = 1024 * 1024


def digest_of(path):
    """SHA-256 hex digest of a file, read in 64 KiB chunks."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(65536), b""):
            h.update(block)
    return h.hexdigest()


def find_source():
    """Absolute path of the entry.png sitting next to this file."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "entry.png")


def main():
    src = find_source()
    if not os.path.isfile(src):
        print(f"error: entry.png not found next to main.py ({src})",
              file=sys.stderr)
        return 1

    size = os.path.getsize(src)
    if size > ONE_MIB:
        print(f"error: entry.png is {size} bytes, over the 1 MiB limit",
              file=sys.stderr)
        return 1

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)

    src_digest = digest_of(src)
    if os.path.getsize(dst) != size or digest_of(dst) != src_digest:
        print("error: copy failed verification (size or SHA-256 mismatch)",
              file=sys.stderr)
        return 1

    print(f"success: entry.png copied to {dst} "
          f"({size} bytes, sha256 {src_digest})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
