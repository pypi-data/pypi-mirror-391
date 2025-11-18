import tensorflow as tf


class RGBAtoRGBLayer(tf.keras.layers.Layer):
    """
    RGBA (4ch) 入力から RGB (3ch) のみを取り出すレイヤー。
    アルファチャンネルは破棄する。
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @tf.function
    def call(self, inputs, training=None):
        """
        training=True のときに RGBA → RGB の変換を行う。

        Parameters
        ----------
        inputs : Tensor
            形状 (batch, H, W, 4) を想定。
        training : bool
            学習時のみ変換し、推論時は入力をそのまま返す。
        """
        if training:
            return inputs[:, :, :, :3]
        else:
            return inputs

    def compute_output_shape(self, input_shape):
        return (input_shape[0], input_shape[1], input_shape[2], 3)
