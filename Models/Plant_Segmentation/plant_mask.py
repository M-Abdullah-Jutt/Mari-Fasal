"""
plant_mask.py - Isolate Plant/Leaf Pixels from Complex Real-World Backgrounds
================================================================================
PlantSeg's masks only label DISEASED regions - they don't separate healthy
plant tissue from background. Since severity = diseased / (diseased + healthy
PLANT tissue), we need a second, separate way to know which pixels are plant
at all (vs soil, sky, hands, other objects in an in-the-wild photo).

This uses ExG (Excess Green Index), a well-established vegetation index from
agricultural computer vision, which works on natural/complex backgrounds -
unlike our earlier Option A approach, which assumed a plain/black background.

    ExG = 2*G - R - B   (computed on normalized RGB channels)

High ExG = likely vegetation. We threshold this with Otsu to get a plant mask.

This is used in BOTH the Colab training/inference pipeline and can be reused
locally - it has no Colab-specific dependencies.
"""

import cv2
import numpy as np


def compute_plant_mask(img_bgr, clean=True):
    """
    Returns a boolean mask where True = plant/vegetation pixel.
    Works on natural backgrounds (soil, other objects, sky, etc.) - not just
    plain/black backgrounds.
    """
    img_float = img_bgr.astype(np.float32)
    b, g, r = img_float[:, :, 0], img_float[:, :, 1], img_float[:, :, 2]

    # Normalize to avoid overall brightness dominating the index
    total = r + g + b + 1e-6
    r_n, g_n, b_n = r / total, g / total, b / total

    exg = 2 * g_n - r_n - b_n  # Excess Green Index
    exg_norm = cv2.normalize(exg, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

    _, plant_mask = cv2.threshold(exg_norm, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    plant_mask = plant_mask > 0

    if clean:
        mask_uint8 = (plant_mask.astype(np.uint8)) * 255
        kernel = np.ones((5, 5), np.uint8)
        mask_uint8 = cv2.morphologyEx(mask_uint8, cv2.MORPH_OPEN, kernel)
        mask_uint8 = cv2.morphologyEx(mask_uint8, cv2.MORPH_CLOSE, kernel)
        plant_mask = mask_uint8 > 0

    return plant_mask


def visualize_plant_mask(img_bgr, plant_mask):
    """Returns a visualization: plant pixels highlighted in a semi-transparent overlay."""
    overlay = img_bgr.copy()
    overlay[plant_mask] = [0, 255, 0]
    blended = cv2.addWeighted(img_bgr, 0.6, overlay, 0.4, 0)
    return blended
