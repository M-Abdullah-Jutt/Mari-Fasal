import argparse
import csv
from pathlib import Path

import cv2
import numpy as np
import torch

try:
    import segmentation_models_pytorch as smp
except ImportError:
    raise ImportError("Install with: pip install segmentation-models-pytorch")

from .plant_mask import compute_plant_mask

IMG_SIZE = 256


def load_model(model_path, device):
    model = smp.Unet(
        encoder_name="resnet34",
        encoder_weights=None,  # weights come from trained checkpoint
        in_channels=3,
        classes=2,
    )
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()
    return model


def predict_disease_mask(model, img_bgr, device, img_size=IMG_SIZE):
    orig_h, orig_w = img_bgr.shape[:2]
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    img_resized = cv2.resize(img_rgb, (img_size, img_size), interpolation=cv2.INTER_LINEAR)
    img_norm = img_resized.astype(np.float32) / 255.0
    img_tensor = torch.from_numpy(img_norm).permute(2, 0, 1).unsqueeze(0).to(device)

    with torch.no_grad():
        out = model(img_tensor)
        pred = torch.argmax(out, dim=1)[0].cpu().numpy().astype(np.uint8)

    pred_full = cv2.resize(pred, (orig_w, orig_h), interpolation=cv2.INTER_NEAREST)
    return pred_full > 0  # boolean disease mask


def estimate_severity(image_or_path, model, device):
    if isinstance(image_or_path, (str, Path)):
        img_bgr = cv2.imread(str(image_or_path))
        if img_bgr is None:
            raise ValueError(f"Could not read image: {image_or_path}")
    else:
        img_bgr = image_or_path  # already a numpy array (e.g. from FastAPI upload)

    plant_mask = compute_plant_mask(img_bgr)
    disease_mask = predict_disease_mask(model, img_bgr, device)

    # Disease predictions outside the plant area (background misclassified as
    # disease) are excluded - only trust disease predictions within plant pixels.
    disease_mask = disease_mask & plant_mask

    plant_pixels = int(plant_mask.sum())
    disease_pixels = int(disease_mask.sum())
    healthy_pixels = plant_pixels - disease_pixels

    severity_pct = (100.0 * disease_pixels / plant_pixels) if plant_pixels > 0 else 0.0

    return {
        "severity_pct": round(severity_pct, 2),
        "plant_pixels": plant_pixels,
        "disease_pixels": disease_pixels,
        "healthy_pixels": healthy_pixels,
        "plant_mask": plant_mask,
        "disease_mask": disease_mask,
        "img_bgr": img_bgr,
    }


def save_visualization(result, out_path):
    img_bgr = result["img_bgr"]
    plant_mask = result["plant_mask"]
    disease_mask = result["disease_mask"]

    plant_viz = np.zeros_like(img_bgr)
    plant_viz[plant_mask] = [0, 200, 0]

    overlay = img_bgr.copy()
    overlay[disease_mask] = [0, 0, 255]
    blended = cv2.addWeighted(img_bgr, 0.6, overlay, 0.4, 0)

    combined = np.hstack([img_bgr, plant_viz, blended])
    cv2.imwrite(str(out_path), combined)


def run_single(args, model, device):
    result = estimate_severity(args.image, model, device)
    print(f"\nImage: {args.image}")
    print(f"Severity: {result['severity_pct']}%")
    print(f"Plant pixels: {result['plant_pixels']}  |  Disease: {result['disease_pixels']}  |  Healthy: {result['healthy_pixels']}")

    if args.visualize:
        out_path = Path(args.image).with_suffix(".severity_viz.png")
        save_visualization(result, out_path)
        print(f"Visualization saved to: {out_path}")


def run_batch(args, model, device):
    input_dir = Path(args.input_dir)
    image_paths = sorted([
        p for p in input_dir.iterdir()
        if p.suffix.lower() in (".jpg", ".jpeg", ".png") and "severity_viz" not in p.stem
    ])

    if not image_paths:
        print(f"No images found in {input_dir}")
        return

    rows = []
    for p in image_paths:
        try:
            result = estimate_severity(p, model, device)
            rows.append({
                "image": str(p),
                "severity_pct": result["severity_pct"],
                "plant_pixels": result["plant_pixels"],
                "disease_pixels": result["disease_pixels"],
                "healthy_pixels": result["healthy_pixels"],
            })
        except Exception as e:
            print(f"Skipping {p}: {e}")

    with open(args.output_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["image", "severity_pct", "plant_pixels", "disease_pixels", "healthy_pixels"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nSaved {len(rows)} results to {args.output_csv}")
    if rows:
        sevs = [r["severity_pct"] for r in rows]
        print(f"Mean severity: {np.mean(sevs):.2f}%  |  Min: {np.min(sevs):.2f}%  |  Max: {np.max(sevs):.2f}%")


def main():
    parser = argparse.ArgumentParser(description="Local severity inference (U-Net disease mask + plant mask)")
    parser.add_argument("--mode", choices=["single", "batch"], required=True)
    parser.add_argument("--model", required=True, help="Path to trained .pth checkpoint (copied from Colab)")
    parser.add_argument("--image", help="Path to single image (mode=single)")
    parser.add_argument("--input_dir", help="Path to folder of images (mode=batch)")
    parser.add_argument("--output_csv", default="severity_results.csv")
    parser.add_argument("--visualize", action="store_true")
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = load_model(args.model, device)

    if args.mode == "single":
        if not args.image:
            parser.error("--image is required for mode=single")
        run_single(args, model, device)
    else:
        if not args.input_dir:
            parser.error("--input_dir is required for mode=batch")
        run_batch(args, model, device)


if __name__ == "__main__":
    main()
