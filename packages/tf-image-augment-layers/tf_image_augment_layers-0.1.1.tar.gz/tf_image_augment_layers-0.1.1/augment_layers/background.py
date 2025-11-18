import tensorflow as tf


@tf.function
def background_composit(inputs, use_white=False, use_black=False):
    """
    背景をランダムに置換する関数。
    アルファチャンネルを持つ RGBA 入力を想定。
    """

    # アルファチャンネル取得
    alpha_channel = inputs[:, :, -1:]
    mask = alpha_channel / 255.0
    mask2 = 1.0 - mask

    # ランダムノイズ背景
    noise_background = tf.random.uniform(
        shape=tf.shape(inputs[:, :, :-1]),
        minval=0,
        maxval=255,
        dtype=tf.float32,
    )

    # 背景の種類をランダムに選ぶ
    def select_background(branch_index):
        if branch_index == 0:
            return 127.0 * tf.ones_like(inputs[:, :, :3], dtype=tf.float32)  # Gray
        elif branch_index == 1:
            return noise_background  # Random noise
        elif use_white and branch_index == 2:
            return 255.0 * tf.ones_like(inputs[:, :, :3], dtype=tf.float32)  # White
        elif use_black and branch_index == 3:
            return tf.zeros_like(inputs[:, :, :3], dtype=tf.float32)  # Black
        else:
            return 127.0 * tf.ones_like(inputs[:, :, :3], dtype=tf.float32)

    maxval = 2 + int(use_white) + int(use_black)
    branch_index = tf.random.uniform(shape=(), maxval=maxval, dtype=tf.int32)
    background = select_background(branch_index)

    # 合成
    foreground = inputs[:, :, :3] * mask
    merged_background = background * mask2
    outputs = foreground + merged_background

    return outputs


class ReplaceBackgroundWithGrayNoiseLayer(tf.keras.layers.Layer):
    """
    RGBA画像の背景をグレー、ノイズ、白、黒のいずれかでランダム置換するレイヤー
    """

    def __init__(self, use_white=False, use_black=False, **kwargs):
        super().__init__(**kwargs)
        self.use_white = use_white
        self.use_black = use_black

    @tf.function
    def call(self, inputs, training=None):
        if training:
            batch_size = tf.shape(inputs)[0]
            aug_images = tf.TensorArray(tf.float32, size=batch_size)

            for i in tf.range(batch_size):
                aug_images = aug_images.write(
                    i, background_composit(inputs[i], self.use_white, self.use_black)
                )

            aug_images = aug_images.stack()
            aug_images.set_shape((None, None, None, 3))
            return aug_images
        else:
            return inputs

    def get_config(self):
        config = super().get_config()
        config.update(
            {
                "use_white": self.use_white,
                "use_black": self.use_black,
            }
        )
        return config
