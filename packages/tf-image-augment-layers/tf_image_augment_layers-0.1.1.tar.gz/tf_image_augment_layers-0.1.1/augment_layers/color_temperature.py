import tensorflow as tf


class RandomColorTemperatureLayer(tf.keras.layers.Layer):
    """
    画像の色温度（ケルビン値）を指定範囲でランダムに変更するレイヤー。
    光源変化をシミュレートし、学習データの一般化を高めることを目的とする。
    """

    def __init__(self, kelvin_range=(2500, 7500), **kwargs):
        """
        Parameters
        ----------
        kelvin_range : tuple(int, int)
            色温度の下限・上限（ケルビン値）。
        """
        super().__init__(**kwargs)
        self.kelvin_range = kelvin_range

    def build(self, input_shape):
        super().build(input_shape)

    @tf.function
    def call(self, inputs, training=None):
        """
        バッチ全体にランダムな色温度を適用。

        Parameters
        ----------
        inputs : Tensor
            画像テンソル (batch, H, W, 3)
        training : bool
            training=True のときのみ変換。
        """
        if training:
            batch_size = tf.shape(inputs)[0]

            # ランダムなケルビン値を生成
            kelvin_values = tf.random.uniform(
                [batch_size],
                minval=self.kelvin_range[0],
                maxval=self.kelvin_range[1],
                dtype=tf.float32,
            )

            # 画像に色温度を適用
            return tf.vectorized_map(
                lambda x: self.apply_random_color_temperature(x[0], x[1]),
                (inputs, kelvin_values),
            )

        return inputs

    # ----------------------------------------------------------------------
    # 色温度処理のメインロジック
    # ----------------------------------------------------------------------

    @tf.function
    def apply_random_color_temperature(self, image, kelvin_value):
        """1 枚の画像に色温度を適用"""
        return self.adjust_color_temperature(image, kelvin_value)

    @tf.function
    def adjust_color_temperature(self, image, kelvin_value):
        """
        RGB に対して 3×3 のカラー変換行列を適用して色温度を調整。
        """
        matrix = self.create_temperature_matrix(kelvin_value)
        matrix = tf.reshape(matrix, [1, 1, 3, 3])

        image = tf.expand_dims(image, axis=0)
        image = tf.nn.conv2d(image, matrix, strides=[1, 1, 1, 1], padding="SAME")
        image = tf.squeeze(image, axis=0)

        return image

    @tf.function
    def create_temperature_matrix(self, kelvin_value):
        """
        Kelvin 値から RGB の補正係数を計算し、3×3 の変換行列を生成。
        白熱灯〜青白い光源までの対応。
        """
        kelvin = kelvin_value / 100.0

        # Red
        red = tf.where(
            kelvin <= 66,
            255.0,
            tf.clip_by_value(
                329.698727446 * tf.pow(kelvin - 60.0, -0.1332047592), 0.0, 255.0
            ),
        )

        # Green
        green = tf.where(
            kelvin <= 66,
            tf.clip_by_value(
                99.4708025861 * tf.math.log(kelvin) - 161.1195681661,
                0.0,
                255.0,
            ),
            tf.clip_by_value(
                288.1221695283 * tf.pow(kelvin - 60.0, -0.0755148492),
                0.0,
                255.0,
            ),
        )

        # Blue
        blue = tf.where(
            kelvin >= 66,
            255.0,
            tf.where(
                kelvin <= 19,
                0.0,
                tf.clip_by_value(
                    138.5177312231 * tf.math.log(kelvin - 10.0) - 305.0447927307,
                    0.0,
                    255.0,
                ),
            ),
        )

        # 3x3 行列化（RGB の対角行列）
        matrix = tf.convert_to_tensor(
            [
                [red / 255.0, 0.0, 0.0],
                [0.0, green / 255.0, 0.0],
                [0.0, 0.0, blue / 255.0],
            ],
            dtype=tf.float32,
        )
        return matrix

    # ----------------------------------------------------------------------
    def get_config(self):
        config = super().get_config()
        config.update(
            {
                "kelvin_range": self.kelvin_range,
            }
        )
        return config
