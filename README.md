# wrap_text_inverse

## 日本語説明

### 概要

`wrap_text_inverse.py`
は、透過PNG画像（文字やロゴなど）を**円筒に巻き付けた見え方に変換するPythonスクリプト**です。

縦方向のピクセル位置は変更せず、横方向のみを数学的に円筒投影（逆写像 /
inverse mapping）で変換します。

物理モデルに基づいた変換を行うため、

-   円筒の直径（ピクセル単位）
-   巻き付けるラベルの弧長（ピクセル単位）

を入力パラメータとして指定できます。

------------------------------------------------------------------------

## 数学的モデル

-   円筒直径: `D_px`
-   半径: `R = D_px / 2`
-   ラベル弧長: `L_px`
-   入力画像幅: `W`

入力座標 x を円筒上の角度 θ に変換:

θ = (L_px / R) \* (x - x_c) / (W - 1)

正面投影では:

x_proj = R \* sin(θ)

本プログラムでは穴あきを防ぐために**inverse
mapping（逆写像）**を採用しています。

------------------------------------------------------------------------

## 必要環境

-   Python 3.9+
-   Pillow
-   NumPy

インストール:

pip install pillow numpy

------------------------------------------------------------------------

## 使用方法

python wrap_text_inverse.py input.png -o output.png --D 800

### オプション

--D : 円筒直径（px）※必須\
--L : ラベル弧長（px）※省略時は画像幅\
--margin : 自動トリミング余白（既定40px）\
--alpha_threshold : 透過判定しきい値

例:

python wrap_text_inverse.py text.png -o wrapped.png --D 600 --L 500

------------------------------------------------------------------------

## パラメータ調整のヒント

-   より強く巻き付けたい → D を小さくする\
-   緩やかにしたい → D を大きくする\
-   L を小さくすると、より中央寄りに圧縮される

------------------------------------------------------------------------

# English Description

## Overview

`wrap_text_inverse.py` transforms a transparent PNG (text or logo) into
a **cylindrical wrapped projection**.

The vertical pixel positions remain unchanged.\
Only the horizontal axis is transformed using a mathematically correct
cylindrical projection model with inverse mapping.

You can control:

-   Cylinder diameter (in pixels)
-   Label arc length (in pixels)

------------------------------------------------------------------------

## Mathematical Model

-   Cylinder diameter: `D_px`
-   Radius: `R = D_px / 2`
-   Label arc length: `L_px`
-   Input width: `W`

Mapping input x to cylinder angle θ:

θ = (L_px / R) \* (x - x_c) / (W - 1)

Front projection:

x_proj = R \* sin(θ)

The implementation uses inverse mapping to avoid pixel holes.

------------------------------------------------------------------------

## Requirements

-   Python 3.9+
-   Pillow
-   NumPy

Install:

pip install pillow numpy

------------------------------------------------------------------------

## Usage

python wrap_text_inverse.py input.png -o output.png --D 800

Example:

python wrap_text_inverse.py text.png -o wrapped.png --D 600 --L 500

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

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
