from useckit.paradigms.time_series_classification.prediction_models.instance_normalization_layer import \
    InstanceNormalization
from useckit.paradigms.distance_learning.prediction_models.online_triplet_loss.triplet_semihard_loss_function import \
    TripletSemiHardLoss

import keras
import tensorflow as tf
import numpy as np

from enum import Enum

class ModelArchitecture(Enum):
    CNN_VALID = 0
    CNN_SAME = 1
    FCN = 2
    MLP = 3
    RESNET = 4
    ENCODER = 5
    MCNN = 6
    MCDCNN = 7
    TLENET = 8
    INCEPTION = 9
    TWIESN = 10
    AD = ANOMALY_DETECTION = 11

    @classmethod
    def get_by_string(cls, name: str):
        name = name.upper()
        return cls.__members__.get(name)

class Paradigm(Enum):
    TSC = TIME_SERIES_CLASSIFICATION = 0
    BV = BINARY_VERIFICATION = 1
    CL = CONTRASIVE_LOSS = 2
    TL = TRIPLET_LOSS = 3
    AD = ANOMALY_DETECTION = 4

    @classmethod
    def get_by_string(cls, name: str):
        name = name.upper()
        return cls.__members__.get(name)


def _mb_dl4tsc_cnn_mid(input_layer: keras.layers.Input, padding: str): 
    conv1 = keras.layers.Conv1D(filters=6, kernel_size=7, padding=padding, activation='sigmoid')(input_layer)
    conv1 = keras.layers.AveragePooling1D(pool_size=3)(conv1)

    conv2 = keras.layers.Conv1D(filters=12, kernel_size=7, padding=padding, activation='sigmoid')(conv1)
    conv2 = keras.layers.AveragePooling1D(pool_size=3)(conv2)

    flatten_layer = keras.layers.Flatten()(conv2)
    return flatten_layer


# use with batch_size=16 and epochs=2000
def mb_dl4tsc_fcn_mid(input_layer: keras.layers.Input): 
    conv1 = keras.layers.Conv1D(filters=128, kernel_size=8, padding='same')(input_layer)
    conv1 = keras.layers.BatchNormalization()(conv1)
    conv1 = keras.layers.Activation(activation='relu')(conv1)

    conv2 = keras.layers.Conv1D(filters=256, kernel_size=5, padding='same')(conv1)
    conv2 = keras.layers.BatchNormalization()(conv2)
    conv2 = keras.layers.Activation('relu')(conv2)

    conv3 = keras.layers.Conv1D(128, kernel_size=3, padding='same')(conv2)
    conv3 = keras.layers.BatchNormalization()(conv3)
    conv3 = keras.layers.Activation('relu')(conv3)

    gap_layer = keras.layers.GlobalAveragePooling1D()(conv3)
    return gap_layer


# use with batch_size=16 and epochs=5000
def mb_dl4tsc_mlp_mid(input_layer: keras.layers.Input): 
    # flatten/reshape because when multivariate all should be on the same axis
    input_layer_flattened = keras.layers.Flatten()(input_layer)

    layer_1 = keras.layers.Dropout(0.1)(input_layer_flattened)
    layer_1 = keras.layers.Dense(500, activation='relu')(layer_1)

    layer_2 = keras.layers.Dropout(0.2)(layer_1)
    layer_2 = keras.layers.Dense(500, activation='relu')(layer_2)

    layer_3 = keras.layers.Dropout(0.2)(layer_2)
    layer_3 = keras.layers.Dense(500, activation='relu')(layer_3)
    output_layer = keras.layers.Dropout(0.3)(layer_3)
    return output_layer


# use with batch_size=min(64, train_data/10) and epochs=1500
def mb_dl4tsc_resnet_mid(input_layer: keras.layers.Input): 
    n_feature_maps = 64

    # BLOCK 1
    conv_x = keras.layers.Conv1D(filters=n_feature_maps, kernel_size=8, padding='same')(input_layer)
    conv_x = keras.layers.BatchNormalization()(conv_x)
    conv_x = keras.layers.Activation('relu')(conv_x)

    conv_y = keras.layers.Conv1D(filters=n_feature_maps, kernel_size=5, padding='same')(conv_x)
    conv_y = keras.layers.BatchNormalization()(conv_y)
    conv_y = keras.layers.Activation('relu')(conv_y)

    conv_z = keras.layers.Conv1D(filters=n_feature_maps, kernel_size=3, padding='same')(conv_y)
    conv_z = keras.layers.BatchNormalization()(conv_z)

    # expand channels for the sum
    shortcut_y = keras.layers.Conv1D(filters=n_feature_maps, kernel_size=1, padding='same')(input_layer)
    shortcut_y = keras.layers.BatchNormalization()(shortcut_y)

    output_block_1 = keras.layers.add([shortcut_y, conv_z])
    output_block_1 = keras.layers.Activation('relu')(output_block_1)

    # BLOCK 2

    conv_x = keras.layers.Conv1D(filters=n_feature_maps * 2, kernel_size=8, padding='same')(output_block_1)
    conv_x = keras.layers.BatchNormalization()(conv_x)
    conv_x = keras.layers.Activation('relu')(conv_x)

    conv_y = keras.layers.Conv1D(filters=n_feature_maps * 2, kernel_size=5, padding='same')(conv_x)
    conv_y = keras.layers.BatchNormalization()(conv_y)
    conv_y = keras.layers.Activation('relu')(conv_y)

    conv_z = keras.layers.Conv1D(filters=n_feature_maps * 2, kernel_size=3, padding='same')(conv_y)
    conv_z = keras.layers.BatchNormalization()(conv_z)

    # expand channels for the sum
    shortcut_y = keras.layers.Conv1D(filters=n_feature_maps * 2, kernel_size=1, padding='same')(output_block_1)
    shortcut_y = keras.layers.BatchNormalization()(shortcut_y)

    output_block_2 = keras.layers.add([shortcut_y, conv_z])
    output_block_2 = keras.layers.Activation('relu')(output_block_2)

    # BLOCK 3

    conv_x = keras.layers.Conv1D(filters=n_feature_maps * 2, kernel_size=8, padding='same')(output_block_2)
    conv_x = keras.layers.BatchNormalization()(conv_x)
    conv_x = keras.layers.Activation('relu')(conv_x)

    conv_y = keras.layers.Conv1D(filters=n_feature_maps * 2, kernel_size=5, padding='same')(conv_x)
    conv_y = keras.layers.BatchNormalization()(conv_y)
    conv_y = keras.layers.Activation('relu')(conv_y)

    conv_z = keras.layers.Conv1D(filters=n_feature_maps * 2, kernel_size=3, padding='same')(conv_y)
    conv_z = keras.layers.BatchNormalization()(conv_z)

    # no need to expand channels because they are equal
    shortcut_y = keras.layers.BatchNormalization()(output_block_2)

    output_block_3 = keras.layers.add([shortcut_y, conv_z])
    output_block_3 = keras.layers.Activation('relu')(output_block_3)

    # FINAL
    gap_layer = keras.layers.GlobalAveragePooling1D()(output_block_3)
    return gap_layer


# use with batch_size=12 and epochs=100
def mb_dl4tsc_encoder_mid(input_layer: keras.layers.Input):
    # conv block -1
    conv1 = keras.layers.Conv1D(filters=128, kernel_size=5, strides=1, padding='same')(input_layer)
    conv1 = InstanceNormalization()(conv1)
    conv1 = keras.layers.PReLU(shared_axes=[1])(conv1)
    conv1 = keras.layers.Dropout(rate=0.2)(conv1)
    conv1 = keras.layers.MaxPooling1D(pool_size=2)(conv1)
    # conv block -2
    conv2 = keras.layers.Conv1D(filters=256, kernel_size=11, strides=1, padding='same')(conv1)
    conv2 = InstanceNormalization()(conv2)
    conv2 = keras.layers.PReLU(shared_axes=[1])(conv2)
    conv2 = keras.layers.Dropout(rate=0.2)(conv2)
    conv2 = keras.layers.MaxPooling1D(pool_size=2)(conv2)
    # conv block -3
    conv3 = keras.layers.Conv1D(filters=512, kernel_size=21, strides=1, padding='same')(conv2)
    conv3 = InstanceNormalization()(conv3)
    conv3 = keras.layers.PReLU(shared_axes=[1])(conv3)
    conv3 = keras.layers.Dropout(rate=0.2)(conv3)
    # split for attention
    attention_data = keras.layers.Lambda(lambda x: x[:, :, :256])(conv3)
    attention_softmax = keras.layers.Lambda(lambda x: x[:, :, 256:])(conv3)
    # attention mechanism
    attention_softmax = keras.layers.Softmax()(attention_softmax)
    multiply_layer = keras.layers.Multiply()([attention_softmax, attention_data])
    # last layer
    dense_layer = keras.layers.Dense(units=256, activation='sigmoid')(multiply_layer)
    dense_layer = InstanceNormalization()(dense_layer)
    flatten_layer = keras.layers.Flatten()(dense_layer)
    return flatten_layer


def mb_inception(input_layer):
    # TODO choose which will be changable
    use_residual = True
    use_bottleneck = True
    depth = 6
    kernel_size = 41
    nb_filters = 32
    stride = 1
    activation = 'linear'

    bottleneck_size = 32
        
    x = input_layer
    input_res = input_layer

    for d in range(depth):
        if use_bottleneck and int(x.shape[-1]) > bottleneck_size:
            input_inception = keras.layers.Conv1D(filters=bottleneck_size, kernel_size=1,
                                                    padding='same', activation=activation, use_bias=False)(x)
        else:
            input_inception = x

        # kernel_size_s = [3, 5, 8, 11, 17]
        kernel_size_s = [kernel_size // (2 ** i) for i in range(3)]

        conv_list = []

        for i in range(len(kernel_size_s)):
            conv_list.append(keras.layers.Conv1D(filters=nb_filters, kernel_size=kernel_size_s[i],
                                                    strides=stride, padding='same', activation=activation, use_bias=False)(
                input_inception))

        max_pool_1 = keras.layers.MaxPool1D(pool_size=3, strides=stride, padding='same')(x)

        conv_6 = keras.layers.Conv1D(filters=nb_filters, kernel_size=1,
                                        padding='same', activation=activation, use_bias=False)(max_pool_1)

        conv_list.append(conv_6)

        x = keras.layers.Concatenate(axis=2)(conv_list)
        x = keras.layers.BatchNormalization()(x)
        x = keras.layers.Activation(activation='relu')(x)

        if use_residual and d % 3 == 2:
            shortcut_y = keras.layers.Conv1D(filters=int(x.shape[-1]), kernel_size=1,
                                                padding='same', use_bias=False)(input_res)
            shortcut_y = keras.layers.BatchNormalization()(shortcut_y)

            x = keras.layers.Add()([shortcut_y, x])
            x = keras.layers.Activation('relu')(x)
            
            input_res = x

    gap_layer = keras.layers.GlobalAveragePooling1D()(x)

    return gap_layer


def mb_tlenet(input_layer):
    conv_1 = keras.layers.Conv1D(filters=5, kernel_size=5, activation='relu', padding='same')(input_layer)
    conv_1 = keras.layers.MaxPool1D(pool_size=2)(conv_1)

    conv_2 = keras.layers.Conv1D(filters=20, kernel_size=5, activation='relu', padding='same')(conv_1)
    conv_2 = keras.layers.MaxPool1D(pool_size=4)(conv_2)

    # they did not mention the number of hidden units in the fully-connected layer
    # so we took the lenet they referenced 

    flatten_layer = keras.layers.Flatten()(conv_2)
    fully_connected_layer = keras.layers.Dense(500, activation='relu')(flatten_layer)

    return fully_connected_layer


def mb_mcnn(input_layers, pool_factor, kernel_size):
    stage_1_layers = []
    for input_layer in input_layers:
        conv_layer = keras.layers.Conv1D(filters=256, kernel_size=kernel_size, padding='same',
                                            activation='sigmoid')(input_layer)

        # should all concatenated have the same length
        pool_size = int(int(conv_layer.shape[1]) / pool_factor)
        max_layer = keras.layers.MaxPooling1D(pool_size=pool_size)(conv_layer)
        
        stage_1_layers.append(max_layer)

    concat_layer = keras.layers.Concatenate(axis=-1)(stage_1_layers)
    kernel_size = int(min(kernel_size, int(concat_layer.shape[1])))  # kernel shouldn't exceed the length
    full_conv = keras.layers.Conv1D(filters=256, kernel_size=kernel_size, padding='same',
                                    activation='sigmoid')(concat_layer)
    pool_size = int(int(full_conv.shape[1]) / pool_factor)
    full_max = keras.layers.MaxPooling1D(pool_size=pool_size)(full_conv)
    full_max = keras.layers.Flatten()(full_max)
    fully_connected = keras.layers.Dense(units=256, activation='sigmoid')(full_max)

    return fully_connected


def mb_mcdcnn(input_layers, n_t, n_vars):
    # TODO use padding var in mb_dl4tsc to choose independent of n_t?
    padding = 'valid'
    if n_t < 60:  # for ItalyPowerOndemand
        padding = 'same'

    conv2_layers = []
    for input_layer in input_layers:
        conv1_layer = keras.layers.Conv1D(filters=8, kernel_size=5, activation='relu', padding=padding)(input_layer)
        conv1_layer = keras.layers.MaxPooling1D(pool_size=2)(conv1_layer)

        conv2_layer = keras.layers.Conv1D(filters=8, kernel_size=5, activation='relu', padding=padding)(conv1_layer)
        conv2_layer = keras.layers.MaxPooling1D(pool_size=2)(conv2_layer)
        conv2_layer = keras.layers.Flatten()(conv2_layer)

        conv2_layers.append(conv2_layer)

    if n_vars == 1:
        # to work with univariate time series
        concat_layer = conv2_layers[0]
    else:
        concat_layer = keras.layers.Concatenate(axis=-1)(conv2_layers)

    fully_connected = keras.layers.Dense(units=732, activation='relu')(concat_layer)

    return fully_connected


def mb_ad_mid(input_layer: keras.layers.Input):
    flatten_layer = keras.layers.Flatten()(input_layer)
    encode_layer = keras.layers.Dense(50, activation='relu')(flatten_layer)

    return encode_layer


def mb_ad_lower(architecture: ModelArchitecture, prev_layer, nb_classes, input_shape):
    metrics = ['accuracy', 'mse']

    loss = 'binary_crossentropy'

    learning_rate = 0.001

    optimizer = keras.optimizers.Adam(learning_rate)

    hidden_size = np.prod(np.array(input_shape))
    decode_layer = keras.layers.Dense(hidden_size, activation='sigmoid')(prev_layer)
    output_layer = keras.layers.Reshape(input_shape)(decode_layer)

    return output_layer, (optimizer, loss, metrics)


# TODO name doesn't fit purpose anymore
def mb_dl4tsc(architecture: ModelArchitecture, input_shape: tuple,
              pool_factor=None, kernel_size=None):
    if architecture == ModelArchitecture.MCNN:
        input_layer = []
        for shape in input_shape:
            input_layer.append(keras.layers.Input(shape))
        
        # self.pool_factors = [2, 3, 5]
        mid = mb_mcnn(input_layer, pool_factor, kernel_size)
    elif architecture == ModelArchitecture.MCDCNN:
        n_t = input_shape[0]
        n_vars = input_shape[1]
        
        input_layer = []
        for _ in range(n_vars):
            input_layer.append(keras.layers.Input((n_t, 1)))
        
        mid = mb_mcdcnn(input_layer, n_t, n_vars)
    else:
        input_layer = keras.layers.Input(input_shape)
    
        if architecture == ModelArchitecture.CNN_VALID:
            mid = _mb_dl4tsc_cnn_mid(input_layer, "valid")

        if architecture == ModelArchitecture.CNN_SAME:
            mid = _mb_dl4tsc_cnn_mid(input_layer, "same")

        if architecture == ModelArchitecture.FCN:
            mid = mb_dl4tsc_fcn_mid(input_layer)

        if architecture == ModelArchitecture.MLP:
            mid = mb_dl4tsc_mlp_mid(input_layer)

        if architecture == ModelArchitecture.RESNET:
            mid = mb_dl4tsc_resnet_mid(input_layer)

        if architecture == ModelArchitecture.ENCODER:
            mid = mb_dl4tsc_encoder_mid(input_layer)
        
        if architecture == ModelArchitecture.INCEPTION:
            mid = mb_inception(input_layer)

        if architecture == ModelArchitecture.TLENET:
            mid = mb_tlenet(input_layer)

        if architecture == ModelArchitecture.TWIESN:
            raise NotImplementedError("TWIESN architecture is not implemented yet.")

        if architecture == ModelArchitecture.AD:
            mid = mb_ad_mid(input_layer)

    return input_layer, mid


def mb_dl4tsc_lower(architecture: ModelArchitecture, prev_layer, nb_classes):
    metrics = ['accuracy']
    if architecture == ModelArchitecture.AD:
        metrics = ['accuracy', 'mse']

    loss = 'categorical_crossentropy'
    if architecture == ModelArchitecture.AD:
        loss = 'binary_crossentropy'

    activation = 'softmax'
    if architecture == ModelArchitecture.CNN_VALID \
    or architecture == ModelArchitecture.CNN_SAME:
        loss = 'mean_squared_error'
        activation = 'sigmoid'
    
    learning_rate = 0.001
    if architecture == ModelArchitecture.ENCODER:
        learning_rate = 0.00001
    if architecture == ModelArchitecture.MCNN:
        learning_rate = 0.1
    if architecture == ModelArchitecture.MCDCNN \
    or architecture == ModelArchitecture.TLENET:
        learning_rate = 0.01
    
    optimizer = keras.optimizers.Adam(learning_rate)
    if architecture == ModelArchitecture.MLP:
        optimizer = keras.optimizers.Adadelta()
    if architecture == ModelArchitecture.MCDCNN:
        optimizer = keras.optimizers.SGD(learning_rate, momentum=0.9, decay=0.0005)
    if architecture == ModelArchitecture.TLENET:
        optimizer = keras.optimizers.Adam(learning_rate, decay=0.005)
    if architecture == ModelArchitecture.INCEPTION:
        optimizer = keras.optimizers.Adam(learning_rate)
    
    output_layer = prev_layer
    if architecture != ModelArchitecture.AD:
        output_layer = keras.layers.Dense(nb_classes, activation=activation)(prev_layer)

    return output_layer, (optimizer, loss, metrics)

def mb_dl4cl_lower(architecture: ModelArchitecture, prev_layer, nb_classes):
    metrics = ['accuracy']

    optimizer="RMSprop"
    
    loss = 'contrastive_loss'
    
    activation = 'sigmoid'
    merge_layer = tf.linalg.norm((prev_layer(input) - prev_layer(input)), axis=1, keepdims=True)
    normal_layer = tf.keras.layers.BatchNormalization()(merge_layer)
    output_layer = tf.keras.layers.Dense(1, activation=activation)(normal_layer)
    return output_layer, (optimizer, loss, metrics)

def mb_dl4tl_lower(architecture: ModelArchitecture, prev_layer, nb_classes):
    pass
    metrics = ['accuracy']
    optimizer = f"{keras.optimizers.Adam(0.0001)}"
    loss = TripletSemiHardLoss()
    t0 = prev_layer #anchor
    t1 = prev_layer #positive
    t2 = prev_layer #negative
    ap_distance = tf.keras.layers.Layer(tf.reduce_sum(tf.square(t0 - t1), -1))
    an_distance = tf.keras.layers.Layer(tf.reduce_sum(tf.square(t0 - t2), -1))

def mb_bv_lower(architecture: ModelArchitecture, prev_layer, nb_classes):
    loss = 'binary_crossentropy'
    optimizer = keras.optimizers.Adam()
    metrics = ['accuracy']
    output_layer = keras.layers.Dense(1, activation='sigmoid')(prev_layer)
    return output_layer, (optimizer, loss, metrics)
