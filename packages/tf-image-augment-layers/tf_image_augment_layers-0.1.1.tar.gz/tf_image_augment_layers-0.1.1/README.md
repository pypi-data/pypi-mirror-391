# tf-image-augment-layers

TensorFlow/Keras 用の高性能画像拡張レイヤーコレクション。市販カメラのホワイトバランスのゆらぎを模倣するために、色温度・色被りの拡張を実装してみました。
RGBA 背景合成・色温度変換・色被り生成など、標準の Keras augmentation にない高度拡張を GPU 上で高速に実行できます。特に背景差し替えは、先行研究で「CNN が対象物へより注視しやすくなる」と報告されており、その検証目的として本実装を追加しました。

---

## 🚀 Features

> **Why this library?** 標準の TensorFlow/Keras では扱えない RGBA 背景合成や高度な色変換が可能になり、データ拡張の幅が大きく広がります。

- 🖼 **RGBA 対応**（透明 PNG を安全に処理）
- 🎨 **背景ランダム置換（グレー / ノイズ / 白 / 黒）**
- 🌡 **色温度を Kelvin 指定でランダム変換**
- 💡 **色被り（Green / Magenta）をランダム付加**
- ⚡ **すべて TensorFlow グラフ上で実行され GPU / TPU に最適化**
- 🔄 **Keras Sequential / Functional / tf.data と完全互換**

---

## 📦 Installation

PyPI 公開後に使用できます：

```
pip install tf-image-augment-layers
```

---

## 🧩 Available Layers

| Layer                                 | Description                                |
| ------------------------------------- | ------------------------------------------ |
| `ReplaceBackgroundWithGrayNoiseLayer` | RGBA 背景をグレー / ノイズ / 白 / 黒に置換 |
| `RGBAtoRGBLayer`                      | RGBA → RGB に変換                          |
| `RandomColorTemperatureLayer`         | 色温度を Kelvin 範囲でランダム変換         |
| `ColorCastLayer`                      | 色被り（Green / Magenta）をランダム追加    |
| `background_composit()`               | 背景置換を行う関数（単独利用可）           |

---

## 🔧 Usage Example

### Keras Sequential に組み込む

> **Note:** 色温度変換（RandomColorTemperatureLayer）や色被り（ColorCastLayer）は RGB 画像を前提としています。RGBA の場合は必ず RGBAtoRGBLayer を適用して 3 チャンネルに変換してから使用してください。

```python
from augment_layers import (
    RGBAtoRGBLayer,
    ReplaceBackgroundWithGrayNoiseLayer,
    RandomColorTemperatureLayer,
    ColorCastLayer,
)
import tensorflow as tf

data_augmentation = tf.keras.Sequential([
    RGBAtoRGBLayer(),
    ReplaceBackgroundWithGrayNoiseLayer(use_white=True),
    RandomColorTemperatureLayer(kelvin_range=(3000, 7500)),
    ColorCastLayer(max_strength=0.3),
])

model = tf.keras.Sequential([
    data_augmentation,
    tf.keras.layers.Rescaling(1./255),
    tf.keras.layers.Conv2D(32, 3, activation="relu"),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(10, activation="softmax"),
])
```

---

## 🧪 Using with tf.data

```python
augment = ReplaceBackgroundWithGrayNoiseLayer(use_white=True)

def preprocess(image, label):
    return augment(image, training=True), label

dataset = dataset.map(preprocess)
```

---

## 🌈 RGBA → RGB

```python
from augment_layers import RGBAtoRGBLayer

rgba_to_rgb = RGBAtoRGBLayer()
rgb_image = rgba_to_rgb(rgba_batch, training=True)
```

---

## 🔥 Background Replacement

```python
from augment_layers import background_composit

aug_image = background_composit(rgba_image, use_white=True)
```

## 📜 License

MIT License

---

##
