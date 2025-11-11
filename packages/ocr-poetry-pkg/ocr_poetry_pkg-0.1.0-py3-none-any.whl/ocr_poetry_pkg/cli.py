import json
import math
import traceback
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image
import torch
from unsloth import FastVisionModel

# ---------------- Model Loading ----------------
model, tokenizer = FastVisionModel.from_pretrained(
    "AhmedZaky1/DIMI-Arabic-OCR-v2",
    load_in_4bit=True,
    device_map={"": 0},
)
FastVisionModel.for_inference(model)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# ---------------- Config ----------------.
IMAGES_DIR = Path("/home/alkaks1309/Desktop/ocr_poetry_pkg/images")  # folder containing page images
JSON_BASE = Path("/home/alkaks1309/Desktop/ocr_poetry_pkg/detections/results")  # base folder for detection jsons
OUT_DIR = Path("/home/alkaks1309/Desktop/ocr_poetry_pkg/output")
OUT_DIR.mkdir(parents=True, exist_ok=True)

        # shrink from 2048 for speed


# ---------------- Helpers ----------------
def clamp(v, lo, hi): return max(lo, min(v, hi))

def axis_aligned_from_polygon(poly, img_w, img_h):
    xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
    x0, y0 = clamp(int(min(xs)), 0, img_w - 1), clamp(int(min(ys)), 0, img_h - 1)
    x1, y1 = clamp(int(max(xs)), 0, img_w), clamp(int(max(ys)), 0, img_h)
    return [x0, y0, x1, y1]

INSTRUCTION = (
    "Extract only the Arabic text visible in this image. Ignore Urdu or Persian. "
    "Preserve diacritics and punctuation exactly. Do not translate. Output Arabic only."
)

# ---------------- Core Function ----------------
def process_image(image_path: Path):
    try:
        img = Image.open(image_path).convert("RGB")
        img_w, img_h = img.size

        # Construct the detection JSON path like:
        # /kaggle/input/json-folder/results/surya/{stem}/results.json
        json_path = JSON_BASE / image_path.stem / "results.json"
        if not json_path.exists():
            return {"image": str(image_path), "error": f"missing detection JSON: {json_path}"}

        result_data = json.loads(json_path.read_text(encoding="utf-8"))
        if isinstance(result_data, dict):
            page_entries = next(iter(result_data.values()))
        elif isinstance(result_data, list):
            page_entries = result_data
        else:
            return {"image": str(image_path), "error": "invalid JSON structure"}

        metadata = []
        for p in page_entries:
            for bb in p.get("bboxes", []):
                poly = bb.get("polygon")
                if not poly:
                    continue
                x0, y0, x1, y1 = axis_aligned_from_polygon(poly[:4], img_w, img_h)
                crop = img.crop((x0, y0, x1, y1))
                
                messages = [
                    {"role": "user", "content": [
                        {"type": "image", "image": crop},
                        {"type": "text", "text": INSTRUCTION},
                    ]}
                ]
                text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                inputs = tokenizer(text=[text], images=[crop], return_tensors="pt", padding=True)
                inputs = {k: v.to(device) if hasattr(v, "to") else v for k, v in inputs.items()}

                with torch.inference_mode():
                    outputs = model.generate(**inputs, max_new_tokens=2048)
                input_len = inputs["input_ids"].shape[1]
                preds = outputs[:, input_len:]
                decoded = tokenizer.batch_decode(preds, skip_special_tokens=True)
                prediction = decoded[0] if decoded else ""

                metadata.append({
                    "bbox": bb,
                    "prediction": prediction,
                })

        out_file = OUT_DIR / f"{image_path.stem}.json"
        out_file.write_text(json.dumps({"image": str(image_path), "results": metadata}, ensure_ascii=False, indent=2))
        return {"image": str(image_path), "status": "done"}

    except Exception as e:
        return {"image": str(image_path), "error": str(e), "traceback": traceback.format_exc()}

# ---------------- Parallel Runner ----------------
def main():
    images = sorted([p for p in IMAGES_DIR.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"}])
    for img in images:
        result = process_image(img)
        print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()