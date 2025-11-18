import tensorflow as tf

def _contrastive_loss(y_true, y_pred, margin = 1.0) -> tf.Tensor:
    r"""Computes the contrastive loss between `y_true` and `y_pred`.

    This loss encourages the embedding to be close to each other for
    the samples of the same label and the embedding to be far apart at least
    by the margin constant for the samples of different labels.

    The euclidean distances `y_pred` between two embedding matrices
    `a` and `b` with shape `[batch_size, hidden_size]` can be computed
    as follows:

    >>> a = tf.constant([[1, 2],
    ...                 [3, 4],
    ...                 [5, 6]], dtype=tf.float16)
    >>> b = tf.constant([[5, 9],
    ...                 [3, 6],
    ...                 [1, 8]], dtype=tf.float16)
    >>> y_pred = tf.linalg.norm(a - b, axis=1)
    >>> y_pred
    <tf.Tensor: shape=(3,), dtype=float16, numpy=array([8.06 , 2.   , 4.473],
    dtype=float16)>

    <... Note: constants a & b have been used purely for
    example purposes and have no significant value ...>

    See: http://yann.lecun.com/exdb/publis/pdf/hadsell-chopra-lecun-06.pdf

    Args:
      y_true: 1-D integer `Tensor` with shape `[batch_size]` of
        binary labels indicating positive vs negative pair.
      y_pred: 1-D float `Tensor` with shape `[batch_size]` of
        distances between two embedding matrices.
      margin: margin term in the loss definition.

    Returns:
      contrastive_loss: 1-D float `Tensor` with shape `[batch_size]`.
    """
    y_pred = tf.convert_to_tensor(y_pred)
    y_true = tf.dtypes.cast(y_true, y_pred.dtype)
    return y_true * tf.math.square(y_pred) + (1.0 - y_true) * tf.math.square(
        tf.math.maximum(margin - y_pred, 0.0)
    )