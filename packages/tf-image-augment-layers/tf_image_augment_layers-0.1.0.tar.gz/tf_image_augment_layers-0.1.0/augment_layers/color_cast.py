import tensorflow as tf


class ColorCastLayer(tf.keras.layers.Layer):
    """
    ランダムに色被り（グリーンまたはマゼンタ）を付加するレイヤー。
    ホワイトバランスの乱れを人工的に生成し、データの多様性を向上させる。
    """

    def __init__(self, max_strength=0.5, **kwargs):
        """
        Parameters
        ----------
        max_strength : float
            色被りの最大強度（0.0〜1.0 を推奨）。
        """
        super().__init__(**kwargs)
        self.max_strength = max_strength

    def build(self, input_shape):
        # 特に学習可能パラメータは無し
        super().build(input_shape)

    @tf.function
    def call(self, inputs, training=None):
        """
        Parameters
        ----------
        inputs : Tensor
            形状 (batch, H, W, 3) の RGB 画像。
        training : bool
            training=True のときのみランダムな色被りを付加。
        """
        if not training:
            return inputs

        batch_size = tf.shape(inputs)[0]

        # 0=green, 1=magenta をランダム選択
        color_choices = tf.random.uniform(
            shape=[batch_size],
            minval=0,
            maxval=2,
            dtype=tf.int32,
        )

        # 各画像の被り強度
        random_strengths = tf.random.uniform(
            shape=[batch_size],
            minval=0.0,
            maxval=self.max_strength,
            dtype=tf.float32,
        )

        return self.color_cast_batch(inputs, color_choices, random_strengths)

    # ----------------------------------------------------------------------
    # 色被りのロジック（高速化のためバッチ処理）
    # ----------------------------------------------------------------------
    @tf.function
    def color_cast_batch(self, images, color_choices, random_strengths):
        """
        グリーンまたはマゼンタの色被りをバッチで適用。
        """

        batch_size = tf.shape(images)[0]

        # Green cast : (1, 1+strength, 1)
        green_mask = tf.stack(
            [
                tf.ones(batch_size),
                1.0 + random_strengths,
                tf.ones(batch_size),
            ],
            axis=1,
        )

        # Magenta cast : (1+strength, 1, 1)
        magenta_mask = tf.stack(
            [
                1.0 + random_strengths,
                tf.ones(batch_size),
                tf.ones(batch_size),
            ],
            axis=1,
        )

        # 0 → green、1 → magenta
        masks = tf.where(
            tf.expand_dims(tf.equal(color_choices, 0), axis=-1),
            green_mask,
            magenta_mask,
        )

        masks = tf.reshape(masks, [batch_size, 1, 1, 3])

        # 色被り適用
        outputs = images * masks

        # RGB 値を保持
        outputs = tf.clip_by_value(outputs, 0.0, 255.0)

        return outputs

    # ----------------------------------------------------------------------
    def get_config(self):
        config = super().get_config()
        config.update(
            {
                "max_strength": self.max_strength,
            }
        )
        return config
