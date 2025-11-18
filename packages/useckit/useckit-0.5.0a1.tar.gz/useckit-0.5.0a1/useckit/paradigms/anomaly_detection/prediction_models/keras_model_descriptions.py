from abc import ABC, abstractmethod

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from tensorflow import keras
from tensorflow.keras import Sequential
from tensorflow.keras import layers


class KerasBaseDescription(ABC):

    @abstractmethod
    def build_model(self, input_shape) -> keras.models.Model:
        pass

    @abstractmethod
    def callbacks(self) -> [keras.callbacks.Callback]:
        pass


class SequentialAutoEncoder(KerasBaseDescription):

    def build_model(self, input_shape):
        hidden_size = np.prod(np.array(input_shape))

        model = Sequential()
        model.add(layers.Flatten(input_shape=input_shape))
        model.add(layers.Dense(50, activation='relu'))
        model.add(layers.Dense(hidden_size, activation='sigmoid'))
        model.add(layers.Reshape(input_shape))
        model.build(input_shape=input_shape)
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['acc', 'mse'])
        return model

    def callbacks(self) -> [keras.callbacks.Callback]:
        return [keras.callbacks.EarlyStopping(monitor="mse",
                                              patience=25,
                                              mode="min",
                                              restore_best_weights=True)]
