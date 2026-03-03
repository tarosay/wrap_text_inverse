# wrap_text_inverse

Cylindrical Label Projection with Inverse Mapping (Orthographic +
Perspective)

------------------------------------------------------------------------

# 日本語版

## 概要

`wrap_text_inverse.py` は、透過PNG画像（文字やロゴなど）を
**円筒に巻き付けた見え方に変換するPythonスクリプト**です。

-   縦方向のピクセルは変更しません
-   横方向のみ数学的に変換します
-   逆写像（inverse mapping）を使用するため穴あきが発生しません
-   正射影（orthographic）と透視投影（perspective）の両方に対応

------------------------------------------------------------------------

## 数学モデル

### 1. 基本パラメータ

-   円筒直径: `D_px`
-   半径: `R = D_px / 2`
-   ラベル弧長: `L_px`
-   入力画像幅: `W`
-   カメラ距離（透視時）: `d`

------------------------------------------------------------------------

## 正射影（Orthographic Projection）

円筒角度:

θ = (L_px / R) \* (x - x_c) / (W - 1)

投影:

x_proj = R \* sin(θ)

------------------------------------------------------------------------

## 透視投影（Perspective Projection）

3D円筒座標:

X(θ) = R sinθ\
Z(θ) = R (1 - cosθ)

透視投影式:

x_img(θ) = d R sinθ / ( d + R (1 - cosθ) )

本プログラムでは解析的逆解（t = tan(θ/2)）を用いて θ を求めています。

------------------------------------------------------------------------

## 必要環境

-   Python 3.9+
-   Pillow
-   NumPy

インストール:

pip install pillow numpy

------------------------------------------------------------------------

## 使用方法

### 正射影

python wrap_text_inverse.py input.png -o output.png --D 800

### 透視投影

python wrap_text_inverse.py input.png -o output.png --D 800 --cam 2000

------------------------------------------------------------------------

## オプション

--D : 円筒直径（px）【必須】\
--L : ラベル弧長（px）※省略時は画像幅\
--cam : カメラ距離（px）※指定時は透視投影\
--margin : 自動トリミング余白（既定40px）\
--alpha_threshold : 透過判定しきい値

------------------------------------------------------------------------

## パラメータ調整の目安

-   強く巻き付けたい → D を小さく
-   緩やかにしたい → D を大きく
-   透視効果を強く → cam を小さく
-   正射影に近づける → cam を大きく

推奨初期値: cam ≈ 3R 〜 10R

------------------------------------------------------------------------

# English Version

## Overview

`wrap_text_inverse.py` converts a transparent PNG into a **cylindrical
wrapped projection**.

Features:

-   Vertical pixels remain unchanged
-   Horizontal axis warped mathematically
-   Inverse mapping (no pixel holes)
-   Supports orthographic and perspective projection

------------------------------------------------------------------------

## Orthographic Projection

θ = (L_px / R) \* (x - x_c) / (W - 1)

x_proj = R \* sin(θ)

------------------------------------------------------------------------

## Perspective Projection

X(θ) = R sinθ\
Z(θ) = R (1 - cosθ)

x_img(θ) = d R sinθ / ( d + R (1 - cosθ) )

θ is solved analytically using the half-angle substitution.

------------------------------------------------------------------------

## Requirements

-   Python 3.9+
-   Pillow
-   NumPy

Install:

pip install pillow numpy

------------------------------------------------------------------------

## Usage

Orthographic:

python wrap_text_inverse.py input.png -o output.png --D 800

Perspective:

python wrap_text_inverse.py input.png -o output.png --D 800 --cam 2000

------------------------------------------------------------------------

## License

MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.
