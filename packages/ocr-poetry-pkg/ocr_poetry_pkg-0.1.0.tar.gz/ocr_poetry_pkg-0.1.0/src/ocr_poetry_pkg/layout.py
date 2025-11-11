import os
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

IMAGES_DIR = Path("/home/alkaks1309/Desktop/ocr_poetry_pkg/images")
VALID_EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}

# tune this: number of parallel processes to run
MAX_WORKERS = min(8, (os.cpu_count() or 4))  # example: up to 8 or CPU count

def run_layout(image_path: Path):
    cmd = ["surya_layout", str(image_path)]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return (image_path.name, True, proc.stdout, proc.stderr)
    except subprocess.CalledProcessError as e:
        return (image_path.name, False, e.stdout or "", e.stderr or str(e))

def get_images(folder: Path):
    return [p for p in folder.iterdir() if p.suffix.lower() in VALID_EXTS]

def main():
    images = get_images(IMAGES_DIR)
    if not images:
        print("No images found.")
        return

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(run_layout, img): img for img in images}
        for fut in as_completed(futures):
            name, ok, out, err = fut.result()
            if ok:
                print(f"{name} finished.")
                if out.strip():
                    print(f"  stdout: {out.strip()}")
            else:
                print(f"{name} failed.")
                if err:
                    print(f"  stderr: {err.strip()}")

if __name__ == "__main__":
    main()
