# wrap_text_inverse

透過PNG（文字/ロゴ）を「円筒に巻き付けた見え方」に変換するスクリプトです。  
**トリム前提**（非透明領域の bbox で切り出してから変形）で、**inverse mapping** なので穴あきしません。  
正射影（orthographic）と透視投影（perspective）に対応します。

---

## 日本語

### 何をするか

- 入力：透明背景付きPNG（RGBA）
- 処理：
  1. `alpha > threshold` の画素から bbox を求める
  2. bbox で画像を **切り出す（trim）**
  3. 切り出した画像を円筒投影で横方向のみワープ（縦方向は不変）
- 出力：ワープ後のPNG（サイズはトリム後サイズ）

### bbox-center の定義

トリム後の画像（幅 `W`）において、

- `x_min = 0`
- `x_max_exclusive = W`

なので、bbox-center は

`x_center = (x_min + (x_max_exclusive - 1)) / 2 = (W - 1) / 2`

円筒の正面（θ=0）に来るアンカーは

`x_anchor = x_center + dx`

です。

### インストール

```bash
pip install pillow numpy
```

### 使い方

#### 正射影（デフォルト）

```bash
python wrap_text_inverse.py input.png -o output.png --D 800
```

#### 透視投影

```bash
python wrap_text_inverse.py input.png -o output.png --D 800 --cam 2000
```

#### アンカーを右へ 25px ずらす（dx）

```bash
python wrap_text_inverse.py input.png -o output.png --D 800 --cam 2000 --dx 25
```

### オプション

- `--D` : 円筒直径（px）【必須】
- `--L` : ラベル弧長（px）※省略時はトリム後幅
- `--cam` : カメラ距離（px）※指定すると透視投影
- `--dx` : bbox-center からのアンカーずらし（px、右が正）
- `--alpha-threshold` : bbox を取る alpha しきい値（0..255）

### パラメータ調整の目安

- 巻き付き強め：`D` を小さく
- 巻き付き弱め：`D` を大きく
- 透視強め：`cam` を小さく
- 正射影に近づく：`cam` を大きく（`cam` 未指定が完全な正射影）

---

## English

### What it does

- Input: RGBA PNG with transparency
- Steps:
  1. Compute bbox from pixels where `alpha > threshold`
  2. **Trim** to the bbox
  3. Warp horizontally using a cylindrical projection (vertical pixels unchanged)
- Output: warped PNG (size equals trimmed size)

### bbox-center definition

After trimming, bbox spans `[0, W)` in x, so:

`x_center = (W - 1) / 2`

Anchor (θ=0):

`x_anchor = x_center + dx`

### Install

```bash
pip install pillow numpy
```

### Usage

Orthographic:

```bash
python wrap_text_inverse.py input.png -o output.png --D 800
```

Perspective:

```bash
python wrap_text_inverse.py input.png -o output.png --D 800 --cam 2000
```

Shift anchor:

```bash
python wrap_text_inverse.py input.png -o output.png --D 800 --cam 2000 --dx 25
```

---

## License

MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.
