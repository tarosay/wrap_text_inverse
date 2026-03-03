# wrap_text_inverse.py
from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np
from PIL import Image


def find_alpha_bbox_xy(img_rgba: Image.Image, alpha_threshold: int = 1):
    """
    Return bbox (x0,y0,x1,y1) of pixels with alpha > alpha_threshold, or None.

    bbox uses half-open ranges: [x0, x1) x [y0, y1)
    """
    arr = np.asarray(img_rgba)
    a = arr[:, :, 3]
    ys, xs = np.where(a > alpha_threshold)
    if len(xs) == 0:
        return None
    return int(xs.min()), int(ys.min()), int(xs.max() + 1), int(ys.max() + 1)


def bbox_center_x(x0: int, x1_exclusive: int) -> float:
    """
    bbox-center x coordinate in the same coordinate system as x0/x1.
    Using: (x_min + x_max) / 2 where x_max is inclusive.
    With half-open bbox, x_max_inclusive = x1_exclusive - 1.
    """
    return (x0 + (x1_exclusive - 1)) / 2.0


def theta_from_x_perspective(x_img: float, R: float, d: float) -> float:
    """
    Invert:
        x_img(θ) = d*R*sinθ / (d + R*(1-cosθ))
    for θ in [-pi/2, pi/2], using half-angle substitution t = tan(θ/2).
    Uses the "minus branch" so that θ -> 0 as x_img -> 0.
    """
    if abs(x_img) < 1e-12:
        return 0.0

    disc = d * d * R * R - (x_img * x_img) * d * (d + 2.0 * R)
    if disc < 0.0:
        disc = 0.0

    num = d * R - math.sqrt(disc)  # minus branch
    den = x_img * (d + 2.0 * R)
    t = num / den
    return 2.0 * math.atan(t)


def warp_inverse_ortho(
    src_rgba: Image.Image,
    D_px: float,
    L_px: float,
    x_anchor: float,
    W_out: int | None = None,
):
    """
    Inverse-map cylindrical wrap (orthographic projection).
    y stays unchanged; only x is warped.

    Parameters:
      - D_px: cylinder diameter [px]
      - L_px: label arc length [px]
      - x_anchor: input x coordinate (in src_rgba) that maps to θ=0 (front)
      - W_out: output width; default = input width
    """
    src = np.asarray(src_rgba).astype(np.float32)
    H, W, C = src.shape
    if W_out is None:
        W_out = W

    R = D_px / 2.0
    if R <= 0:
        raise ValueError("D_px must be > 0")
    if L_px <= 0:
        raise ValueError("L_px must be > 0")

    theta_max = L_px / (2.0 * R)
    theta_vis = min(theta_max, math.pi / 2.0)

    X_max = R * math.sin(theta_vis)
    if X_max <= 0:
        raise ValueError("X_max <= 0 (check D_px / L_px)")

    xcp = (W_out - 1) / 2.0
    out = np.zeros((H, W_out, C), dtype=np.float32)

    for x_out in range(W_out):
        u = (x_out - xcp) / xcp if xcp != 0 else 0.0
        x_proj = u * X_max

        v = max(-1.0, min(1.0, x_proj / R))
        theta = math.asin(v)

        s = R * theta
        x_src = x_anchor + (s / L_px) * (W - 1)

        if x_src < 0 or x_src > (W - 1):
            continue

        x0 = int(np.floor(x_src))
        x1 = min(x0 + 1, W - 1)
        t = x_src - x0
        out[:, x_out, :] = (1 - t) * src[:, x0, :] + t * src[:, x1, :]

    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA"), theta_max


def warp_inverse_persp(
    src_rgba: Image.Image,
    D_px: float,
    L_px: float,
    cam_dist_px: float,
    x_anchor: float,
    W_out: int | None = None,
):
    """
    Inverse-map cylindrical wrap (perspective projection).
    y stays unchanged; only x is warped.

    Parameters:
      - D_px: cylinder diameter [px]
      - L_px: label arc length [px]
      - cam_dist_px: camera distance [px]
      - x_anchor: input x coordinate (in src_rgba) that maps to θ=0 (front)
      - W_out: output width; default = input width
    """
    src = np.asarray(src_rgba).astype(np.float32)
    H, W, C = src.shape
    if W_out is None:
        W_out = W

    R = D_px / 2.0
    d = cam_dist_px
    if R <= 0:
        raise ValueError("D_px must be > 0")
    if L_px <= 0:
        raise ValueError("L_px must be > 0")
    if d <= 0:
        raise ValueError("cam_dist_px must be > 0")

    theta_max = L_px / (2.0 * R)
    theta_vis = min(theta_max, math.pi / 2.0)

    x_img_max = (d * R * math.sin(theta_vis)) / (d + R * (1.0 - math.cos(theta_vis)))
    if x_img_max <= 0:
        raise ValueError("x_img_max <= 0 (check parameters)")

    xcp = (W_out - 1) / 2.0
    out = np.zeros((H, W_out, C), dtype=np.float32)

    for x_out in range(W_out):
        u = (x_out - xcp) / xcp if xcp != 0 else 0.0
        x_img = u * x_img_max

        theta = theta_from_x_perspective(x_img, R=R, d=d)

        s = R * theta
        x_src = x_anchor + (s / L_px) * (W - 1)

        if x_src < 0 or x_src > (W - 1):
            continue

        x0 = int(np.floor(x_src))
        x1 = min(x0 + 1, W - 1)
        t = x_src - x0
        out[:, x_out, :] = (1 - t) * src[:, x0, :] + t * src[:, x1, :]

    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA"), theta_max


def main():
    ap = argparse.ArgumentParser(description="Cylindrical label warp (trim-to-alpha, inverse mapping).")
    ap.add_argument("input", type=Path, help="input RGBA PNG")
    ap.add_argument("-o", "--output", type=Path, required=True, help="output PNG")

    ap.add_argument("--D", type=float, required=True, help="cylinder diameter in pixels (D_px)")
    ap.add_argument(
        "--L",
        type=float,
        default=None,
        help="label arc length in pixels (L_px). default: trimmed width",
    )
    ap.add_argument(
        "--cam",
        type=float,
        default=None,
        help="camera distance in pixels for perspective. If omitted, use orthographic.",
    )

    ap.add_argument(
        "--alpha-threshold",
        type=int,
        default=1,
        help="alpha threshold (0..255) for trimming and bbox-center (default 1)",
    )

    # Spec: anchor is bbox-center, and shift is pixel-specified.
    ap.add_argument(
        "--dx",
        type=float,
        default=0.0,
        help="anchor x offset in pixels from bbox-center (right positive).",
    )

    args = ap.parse_args()

    img = Image.open(args.input).convert("RGBA")

    bbox = find_alpha_bbox_xy(img, alpha_threshold=args.alpha_threshold)
    if bbox is None:
        raise SystemExit("No non-transparent pixels found (after alpha threshold).")

    x0, y0, x1, y1 = bbox
    crop = img.crop((x0, y0, x1, y1))

    # In crop coordinates, bbox is the whole crop: [0, Wc) in x.
    Wc = crop.width
    x_center = bbox_center_x(0, Wc)
    x_anchor = x_center + float(args.dx)

    L_px = float(args.L) if args.L is not None else float(Wc)

    if args.cam is None:
        out, theta_max = warp_inverse_ortho(crop, D_px=args.D, L_px=L_px, x_anchor=x_anchor)
    else:
        out, theta_max = warp_inverse_persp(
            crop, D_px=args.D, L_px=L_px, cam_dist_px=float(args.cam), x_anchor=x_anchor
        )

    out.save(args.output)

    print("Saved:", args.output.resolve())
    print(
        f"theta_max = {theta_max * 180 / math.pi:.2f} deg (label half-span). "
        f"{'OVER 90deg (backside)' if theta_max > math.pi/2 else 'within 90deg'}"
    )


if __name__ == "__main__":
    main()
