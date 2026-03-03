# wrap_text_inverse.py
from __future__ import annotations
import argparse
import math
from pathlib import Path

import numpy as np
from PIL import Image


def find_alpha_bbox(img_rgba: Image.Image, alpha_threshold: int = 1):
    arr = np.asarray(img_rgba)
    a = arr[:, :, 3]
    ys, xs = np.where(a > alpha_threshold)
    if len(xs) == 0:
        return None
    return int(xs.min()), int(ys.min()), int(xs.max() + 1), int(ys.max() + 1)


def warp_cylinder_inverse(crop: Image.Image, D_px: float, L_px: float, W_out: int | None = None):
    """
    Inverse-map cylindrical wrap (orthographic projection).
    y stays unchanged; only x is warped.
    D_px, L_px are in pixels.
    """
    src = np.asarray(crop).astype(np.float32)
    H, W, C = src.shape
    if W_out is None:
        W_out = W

    R = D_px / 2.0
    if R <= 0:
        raise ValueError("D_px must be > 0")

    # Max angle spanned by label (centered at 0)
    theta_max = L_px / (2.0 * R)
    # Visible limit is +/- 90deg
    theta_vis = min(theta_max, math.pi / 2.0)

    X_max = R * math.sin(theta_vis)
    if X_max <= 0:
        raise ValueError("X_max <= 0 (check D_px / L_px)")

    x_c = (W - 1) / 2.0
    xcp = (W_out - 1) / 2.0

    out = np.zeros((H, W_out, C), dtype=np.float32)

    for x_out in range(W_out):
        # normalize to [-1,1]
        u = (x_out - xcp) / xcp if xcp != 0 else 0.0
        # projection x in [-X_max, X_max]
        x_proj = u * X_max

        # arcsin argument should be in [-1,1]
        v = max(-1.0, min(1.0, x_proj / R))
        theta = math.asin(v)  # [-pi/2, pi/2]

        s = R * theta  # arc length (px)
        x_src = x_c + (s / L_px) * (W - 1)

        # sample src at x_src (bilinear in x)
        if x_src < 0 or x_src > (W - 1):
            continue

        x0 = int(np.floor(x_src))
        x1 = min(x0 + 1, W - 1)
        t = x_src - x0
        out[:, x_out, :] = (1 - t) * src[:, x0, :] + t * src[:, x1, :]

    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA"), theta_max


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path, help="input RGBA PNG (transparent background)")
    ap.add_argument("-o", "--output", type=Path, required=True, help="output PNG")
    ap.add_argument("--D", type=float, required=True, help="cylinder diameter in pixels (D_px)")
    ap.add_argument("--L", type=float, default=None, help="label arc length in pixels (L_px). default: use crop width")
    ap.add_argument("--margin", type=int, default=40, help="crop margin (px)")
    ap.add_argument("--alpha_threshold", type=int, default=1, help="alpha threshold (0..255)")
    ap.add_argument("--cam", type=float, default=None,
                help="camera distance in pixels for perspective. "
                     "If omitted, use orthographic.")
    args = ap.parse_args()

    img = Image.open(args.input).convert("RGBA")

    bbox = find_alpha_bbox(img, alpha_threshold=args.alpha_threshold)
    if bbox is None:
        raise SystemExit("No non-transparent pixels found.")

    x0, y0, x1, y1 = bbox
    m = args.margin
    x0c = max(0, x0 - m); y0c = max(0, y0 - m)
    x1c = min(img.width, x1 + m); y1c = min(img.height, y1 + m)

    crop = img.crop((x0c, y0c, x1c, y1c))
    L_px = float(args.L) if args.L is not None else float(crop.width)

    if args.cam is None:
        warped, theta_max = warp_cylinder_inverse(crop, D_px=args.D, L_px=L_px)
    else:
        warped, theta_max = warp_cylinder_inverse_perspective(
            crop, D_px=args.D, L_px=L_px, cam_dist_px=float(args.cam)
        )

    # paste back into full-size transparent canvas
    canvas = Image.new("RGBA", img.size, (0, 0, 0, 0))
    canvas.paste(warped, (x0c, y0c), warped)
    canvas.save(args.output)
    print("Saved:", args.output.resolve())
    
    # optional: print span angle in degrees
    print(f"theta_max = {theta_max * 180/math.pi:.2f} deg (label half-span). "
          f"{'OVER 90deg (backside)' if theta_max > math.pi/2 else 'within 90deg'}")

def theta_from_x_perspective(x_img: float, R: float, d: float) -> float:
    """
    Invert x_img = d*R*sinθ / (d + R*(1-cosθ))  for θ in [-pi/2, pi/2]
    using t = tan(θ/2) closed-form (minus branch).
    """
    if abs(x_img) < 1e-12:
        return 0.0

    # Discriminant inside sqrt:
    disc = d*d*R*R - (x_img*x_img) * d * (d + 2.0*R)
    if disc < 0.0:
        # out of valid range due to rounding or too-large x_img
        disc = 0.0

    num = d*R - math.sqrt(disc)  # minus branch
    den = x_img * (d + 2.0*R)

    t = num / den
    return 2.0 * math.atan(t)


def warp_cylinder_inverse_perspective(
    crop: Image.Image,
    D_px: float,
    L_px: float,
    cam_dist_px: float,
    W_out: int | None = None
):
    """
    Inverse-map cylindrical wrap (perspective projection).
    y stays unchanged; only x is warped.
    All units are pixels.
    """
    src = np.asarray(crop).astype(np.float32)
    H, W, C = src.shape
    if W_out is None:
        W_out = W

    R = D_px / 2.0
    d = cam_dist_px
    if R <= 0:
        raise ValueError("D_px must be > 0")
    if d <= 0:
        raise ValueError("cam_dist_px must be > 0")

    theta_max = L_px / (2.0 * R)
    theta_vis = min(theta_max, math.pi / 2.0)

    # Max visible x_img at theta_vis (for scaling u -> x_img)
    x_img_max = (d * R * math.sin(theta_vis)) / (d + R * (1.0 - math.cos(theta_vis)))
    if x_img_max <= 0:
        raise ValueError("x_img_max <= 0 (check parameters)")

    x_c = (W - 1) / 2.0
    xcp = (W_out - 1) / 2.0

    out = np.zeros((H, W_out, C), dtype=np.float32)

    for x_out in range(W_out):
        u = (x_out - xcp) / xcp if xcp != 0 else 0.0
        x_img = u * x_img_max  # desired projected coordinate

        theta = theta_from_x_perspective(x_img, R=R, d=d)

        s = R * theta  # arc length (px)
        x_src = x_c + (s / L_px) * (W - 1)

        if x_src < 0 or x_src > (W - 1):
            continue

        x0 = int(np.floor(x_src))
        x1 = min(x0 + 1, W - 1)
        t = x_src - x0
        out[:, x_out, :] = (1 - t) * src[:, x0, :] + t * src[:, x1, :]

    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA"), theta_max

if __name__ == "__main__":
    main()