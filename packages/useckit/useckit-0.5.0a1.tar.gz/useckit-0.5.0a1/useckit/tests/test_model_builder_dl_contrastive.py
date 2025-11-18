import unittest
import numpy as np
import keras
from tensorflow.keras.datasets import mnist
from tensorflow.keras import backend as K
from sklearn.metrics import confusion_matrix


class TestSiameseNetwork(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Hyperparameters
        cls.epochs = 10
        cls.batch_size = 16
        cls.margin = 1  # Margin for contrastive loss

        # Load and preprocess MNIST data
        (x_train_val, y_train_val), (x_test, y_test) = mnist.load_data()

        # Add channel dimension and normalize
        x_train_val = x_train_val.astype("float32") / 255.0
        x_train_val = np.expand_dims(x_train_val, -1)  # Add channel dimension

        x_test = x_test.astype("float32") / 255.0
        x_test = np.expand_dims(x_test, -1)  # Add channel dimension

        # Split train/validation
        cls.x_train, cls.x_val = x_train_val[:30000], x_train_val[30000:]
        cls.y_train, cls.y_val = y_train_val[:30000], y_train_val[30000:]
        cls.x_test, cls.y_test = x_test, y_test

        # Create pairs
        cls.pairs_train, cls.labels_train = cls.make_pairs(cls.x_train, cls.y_train)
        cls.pairs_val, cls.labels_val = cls.make_pairs(cls.x_val, cls.y_val)
        cls.pairs_test, cls.labels_test = cls.make_pairs(cls.x_test, cls.y_test)

    @staticmethod
    def make_pairs(x, y):
        num_classes = max(y) + 1
        digit_indices = [np.where(y == i)[0] for i in range(num_classes)]

        pairs = []
        labels = []

        for idx1 in range(len(x)):
            x1 = x[idx1]
            label1 = y[idx1]

            # Positive pair
            idx2 = np.random.choice(digit_indices[label1])
            x2 = x[idx2]
            pairs += [[x1, x2]]
            labels += [0]  # 0 means same class (positive pair)

            # Negative pair
            label2 = np.random.randint(0, num_classes)
            while label2 == label1:
                label2 = np.random.randint(0, num_classes)

            idx2 = np.random.choice(digit_indices[label2])
            x2 = x[idx2]
            pairs += [[x1, x2]]
            labels += [1]  # 1 means different class (negative pair)

        return np.array(pairs), np.array(labels).astype("float32")

    def test_siamese_network(self):
        # Build model
        siamese_model = self.create_siamese_model()

        # Use a smaller learning rate to prevent NaN loss
        optimizer = keras.optimizers.RMSprop(learning_rate=0.0005)

        siamese_model.compile(
            loss=self.contrastive_loss(margin=self.margin),
            optimizer=optimizer,
            metrics=["accuracy"]
        )

        # Prepare data
        x_train_1, x_train_2 = self.pairs_train[:, 0], self.pairs_train[:, 1]
        x_val_1, x_val_2 = self.pairs_val[:, 0], self.pairs_val[:, 1]

        # Train
        history = siamese_model.fit(
            [x_train_1, x_train_2],
            self.labels_train,
            validation_data=([x_val_1, x_val_2], self.labels_val),
            batch_size=self.batch_size,
            epochs=self.epochs
        )

        # Evaluate
        x_test_1, x_test_2 = self.pairs_test[:, 0], self.pairs_test[:, 1]
        results = siamese_model.evaluate([x_test_1, x_test_2], self.labels_test)
        print("Test loss, test acc:", results)

        # Generate predictions
        predictions = siamese_model.predict([x_test_1, x_test_2])
        y_pred = (predictions > 0.5).astype("int32")

        # Generate confusion matrix
        cm = confusion_matrix(self.labels_test, y_pred)
        print("Confusion Matrix:\n", cm)

    def create_siamese_model(self):
        # Embedding network with L2 regularization
        input = keras.layers.Input((28, 28, 1))

        # Add batch normalization at the input
        x = keras.layers.BatchNormalization()(input)

        x = keras.layers.Conv2D(4, (5, 5), activation="relu",
                                kernel_regularizer=keras.regularizers.l2(1e-4))(x)
        x = keras.layers.AveragePooling2D(pool_size=(2, 2))(x)

        x = keras.layers.Conv2D(16, (5, 5), activation="relu",
                                kernel_regularizer=keras.regularizers.l2(1e-4))(x)
        x = keras.layers.AveragePooling2D(pool_size=(2, 2))(x)

        x = keras.layers.Flatten()(x)

        # Change to ReLU and add regularization
        x = keras.layers.Dense(10, activation="relu",
                               kernel_regularizer=keras.regularizers.l2(1e-4))(x)

        # Add a final batch normalization
        x = keras.layers.BatchNormalization()(x)

        embedding_network = keras.Model(input, x)

        # Siamese network
        input_1 = keras.layers.Input((28, 28, 1))
        input_2 = keras.layers.Input((28, 28, 1))
        tower_1 = embedding_network(input_1)
        tower_2 = embedding_network(input_2)

        # Add small epsilon to prevent numerical instability
        merge_layer = keras.layers.Lambda(
            lambda vects: K.sqrt(K.sum(K.square(vects[0] - vects[1]), axis=1, keepdims=True) + 1e-10)
        )([tower_1, tower_2])

        # Remove the batch normalization after distance calculation
        output_layer = keras.layers.Dense(1, activation="sigmoid")(merge_layer)
        return keras.Model(inputs=[input_1, input_2], outputs=output_layer)

    def contrastive_loss(self, margin=1):
        def loss(y_true, y_pred):
            # Add small epsilon to avoid numerical instability
            square_pred = K.square(y_pred)
            margin_square = K.square(K.maximum(margin - y_pred, 0))
            return K.mean((1 - y_true) * square_pred + y_true * margin_square)

        return loss


if __name__ == '__main__':
    unittest.main()