"""
metadata_tool.py - SAFE, LOCAL photo-metadata (EXIF) viewer and cleaner.

* Runs entirely on your computer. The image is NEVER uploaded anywhere.
* Shows only metadata that is explicitly present in the file (no guessing / inference).
* "--strip" saves a CLEAN COPY (pixels only). Your original file is never modified.

Usage:
    python tools/metadata_tool.py photo.jpg            # view metadata
    python tools/metadata_tool.py photo.jpg --strip    # also write photo_clean.jpg
"""
import argparse
from pathlib import Path

from PIL import ExifTags, Image

GPS_IFD = 0x8825


def read_metadata(path):
    """Return {'basic': {...}, 'exif': {...}, 'gps': {...}} using only what is stored in the file."""
    with Image.open(path) as img:
        basic = {"format": img.format, "size": f"{img.width}x{img.height}", "mode": img.mode}
        exif = img.getexif()
        tags = {ExifTags.TAGS.get(k, str(k)): v for k, v in exif.items() if k != GPS_IFD}
        gps_raw = exif.get_ifd(GPS_IFD) if GPS_IFD in exif else {}
        gps = {ExifTags.GPSTAGS.get(k, str(k)): v for k, v in gps_raw.items()}
    return {"basic": basic, "exif": tags, "gps": gps}


def strip_metadata(path):
    """Write '<name>_clean<ext>' containing pixel data only. Returns the new path."""
    src = Path(path)
    dst = src.with_name(f"{src.stem}_clean{src.suffix}")
    with Image.open(src) as img:
        clean = Image.new(img.mode, img.size)
        clean.paste(img)                 # copies pixels only; EXIF/GPS are not carried over
        clean.save(dst)
    return dst


PRIVACY_NOTES = {
    "GPS": "GPS fields show where the photo was taken - remove before sharing publicly.",
    "Make": "Device make/model can identify the phone or camera used.",
    "DateTime": "Timestamps reveal when you were at a place.",
    "Software": "Software strings can reveal the device or editing app.",
}


def main():
    ap = argparse.ArgumentParser(description="Local image metadata viewer (nothing is uploaded).")
    ap.add_argument("image"); ap.add_argument("--strip", action="store_true", help="save a metadata-free copy")
    args = ap.parse_args()
    meta = read_metadata(args.image)
    print("== Basic ==");  [print(f"  {k}: {v}") for k, v in meta["basic"].items()]
    print("== EXIF =="); print("  (none found)") if not meta["exif"] else [print(f"  {k}: {v}") for k, v in meta["exif"].items()]
    print("== GPS (only if explicitly stored) =="); print("  (none found)") if not meta["gps"] else [print(f"  {k}: {v}") for k, v in meta["gps"].items()]
    if meta["gps"]:
        print("\nPrivacy note:", PRIVACY_NOTES["GPS"])
    if args.strip:
        print("\nClean copy written to:", strip_metadata(args.image))


if __name__ == "__main__":
    main()
