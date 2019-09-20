from keras_squeeze_excite_network import TF

if TF:
    from tensorflow.keras.layers import GlobalAveragePooling2D, Reshape, Dense, multiply, add, Permute, Conv2D
    from tensorflow.keras import backend as K
else:
    from keras.layers import GlobalAveragePooling2D, Reshape, Dense, multiply, add, Permute, Conv2D
    import keras.backend as K


def squeeze_excite_block(tensor, ratio=16):
    """ Create a channel-wise squeeze-excite block

    Args:
        tensor: input tensor
        ratio: number of output filters

    Returns: a keras tensor

    References
    -   [Squeeze and Excitation Networks](https://arxiv.org/abs/1709.01507)
    """
    init = tensor
    channel_axis = 1 if K.image_data_format() == "channels_first" else -1
    filters = init._keras_shape[channel_axis]
    se_shape = (1, 1, filters)

    se = GlobalAveragePooling2D()(init)
    se = Reshape(se_shape)(se)
    se = Dense(filters // ratio, activation='relu', kernel_initializer='he_normal', use_bias=False)(se)
    se = Dense(filters, activation='sigmoid', kernel_initializer='he_normal', use_bias=False)(se)

    if K.image_data_format() == 'channels_first':
        se = Permute((3, 1, 2))(se)

    x = multiply([init, se])
    return x


def spatial_squeeze_excite_block(tensor):
    """ Create a spatial squeeze-excite block

    Args:
        tensor: input tensor

    Returns: a keras tensor

    References
    -   [Concurrent Spatial and Channel Squeeze & Excitation in Fully Convolutional Networks](https://arxiv.org/abs/1803.02579)
    """

    se = Conv2D(1, (1, 1), activation='sigmoid', use_bias=False,
                kernel_initializer='he_normal')(tensor)

    x = multiply([tensor, se])
    return x


def channel_spatial_squeeze_excite(tensor, ratio=16):
    """ Create a spatial squeeze-excite block

    Args:
        tensor: input tensor
        ratio: number of output filters

    Returns: a keras tensor

    References
    -   [Squeeze and Excitation Networks](https://arxiv.org/abs/1709.01507)
    -   [Concurrent Spatial and Channel Squeeze & Excitation in Fully Convolutional Networks](https://arxiv.org/abs/1803.02579)
    """

    cse = squeeze_excite_block(tensor, ratio)
    sse = spatial_squeeze_excite_block(tensor)

    x = add([cse, sse])
    return x
