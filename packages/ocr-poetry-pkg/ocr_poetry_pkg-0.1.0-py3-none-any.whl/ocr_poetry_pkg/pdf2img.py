from pdf2image import convert_from_path
from pathlib import Path

PDF = "/path/to/input.pdf"
OUT_DIR = Path("out_images")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# convert all pages
pages = convert_from_path(PDF, dpi=300)  # increase dpi for better quality
for i, page in enumerate(pages, start=1):
    out_path = OUT_DIR / f"page_{i:03d}.jpg"
    page.save(out_path, "JPEG", quality=95)

# Convert a page range or single page:
# pages = convert_from_path(PDF, dpi=300, first_page=2, last_page=5)
