import re
import unittest
import tempfile
import os
import urllib.request
import subprocess
from glob import glob
from statistics import median
import random
from collections import defaultdict

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
import tensorflow as tf
from keras import layers, Model, metrics, optimizers
from tensorflow.keras import backend as K
from keras.src.utils import pad_sequences
from sklearn.preprocessing import MinMaxScaler


class TestSiameseTripletLoss(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up the test class and download the dataset if needed."""
        cls.dataset_dir = tempfile.TemporaryDirectory()
        cls.download_tsc_dataset()
        cls.DATASET = cls.load_dataset()

    @classmethod
    def tearDownClass(cls):
        """Clean up the temporary directory after all tests."""
        cls.dataset_dir.cleanup()

    @classmethod
    def download_tsc_dataset(cls):
        """Download and extract the dataset to the temporary directory."""
        temp_dir = cls.dataset_dir.name

        file1 = "Data_Set_for_Understanding_User_Identification_in_Virtual_Reality_Through_Behavioral_Biometrics_and_the_Effect_of_Body_Normalization.7z.001"
        file2 = "Data_Set_for_Understanding_User_Identification_in_Virtual_Reality_Through_Behavioral_Biometrics_and_the_Effect_of_Body_Normalization.7z.002"

        print("Downloading dataset...")
        urllib.request.urlretrieve(
            "https://hci.informatik.uni-due.de/fileadmin/fileupload/I-HCI/Paper/Data_Set_for_Understanding_User_Identification_in_Virtual_Reality_Through_Behavioral_Biometrics_and_the_Effect_of_Body_Normalization.7z.001",
            os.path.join(temp_dir, file1))
        urllib.request.urlretrieve(
            "https://hci.informatik.uni-due.de/fileadmin/fileupload/I-HCI/Paper/Data_Set_for_Understanding_User_Identification_in_Virtual_Reality_Through_Behavioral_Biometrics_and_the_Effect_of_Body_Normalization.7z.002",
            os.path.join(temp_dir, file2))

        print("Extracting dataset...")
        subprocess.run(["7z", "x", os.path.join(temp_dir, file1), "-o" + temp_dir, "-y"], check=True)
        os.remove(os.path.join(temp_dir, file1))
        os.remove(os.path.join(temp_dir, file2))

    @classmethod
    def load_dataset(cls):
        filename_pattern = r'(?P<activity>\w+)_p(?P<pid>\d+)_(?P<condition>\w+)_session(?P<session>\d+)_repetition(?P<rep>\d+)\.csv'
        file_paths = glob(f"{cls.dataset_dir.name}/*.csv")

        def process_single_file(g):
            filename = os.path.basename(g)
            match = re.match(filename_pattern, filename)
            parsed_data = match.groupdict()
            df = pd.read_csv(g)
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            cols_to_drop = ["ParticipantID", "study_session", "repetition", "timestamp_ms", "phase",
                            "HeightNormalization", "ArmLengthNormalization"]
            cols_to_drop += [col for col in df.columns if col.lower().startswith(("ball", "arrow", "rightcontrolleranchor", "leftcontrolleranchor", "scenario"))]
            df.drop(columns=cols_to_drop, inplace=True, errors='raise')
            return {
                'df': df,
                'pid': f"P{parsed_data['pid']}",
                'condition': parsed_data['condition'],
                'session': int(parsed_data['session']),
                'rep': int(parsed_data['rep']),
                'activity': parsed_data['activity']
            }

        DATASET = Parallel(n_jobs=-1)(delayed(process_single_file)(g) for g in file_paths)
        return DATASET

    @staticmethod
    def preprocess_sample(df):
        for lr in ["Left", "Right"]:
            for XYZ in ["X", "Y", "Z"]:
                df[f"{lr}VirtualHand_pos_{XYZ}"] -= df[f"CenterEyeAnchor_pos_{XYZ}"]
        df.drop(columns=['CenterEyeAnchor_pos_X', 'CenterEyeAnchor_pos_Y', 'CenterEyeAnchor_pos_Z',
                         'CenterEyeAnchor_euler_X', 'CenterEyeAnchor_euler_Y', 'CenterEyeAnchor_euler_Z'], inplace=True)
        for c in df.columns:
            df[c] -= df[c].iloc[0]
        cols = df.columns
        arr = MinMaxScaler().fit_transform(df)
        df = pd.DataFrame(arr, columns=cols)
        return df

    def test_siamese_triplet_loss(self):
        DATASET = [d for d in self.DATASET if d['activity'].lower() == "bowling"]

        for d in DATASET:
            d['df'] = self.preprocess_sample(d['df'])

        med_len = int(median(len(d['df']) for d in DATASET))
        cols = DATASET[0]['df'].columns
        for d, d_padded in zip(DATASET, pad_sequences([d['df'].values for d in DATASET], maxlen=med_len, dtype='float32')):
            d['df'] = pd.DataFrame(d_padded, columns=cols)

        train_data = [d for d in DATASET if d['session'] == 1]

        pid_to_samples = defaultdict(list)
        for d in train_data:
            pid = d['pid']
            sample = d['df'].values.astype('float32')
            pid_to_samples[pid].append(sample)

        valid_pids = [pid for pid, samples in pid_to_samples.items() if len(samples) >= 2]
        pid_to_samples = {pid: pid_to_samples[pid] for pid in valid_pids}

        anchors, positives, negatives = [], [], []
        for pid in valid_pids:
            samples = pid_to_samples[pid]
            num_samples = len(samples)
            for i in range(num_samples):
                anchor = samples[i]
                positive_idx = (i + 1) % num_samples
                positive = samples[positive_idx]
                other_pids = [p for p in valid_pids if p != pid]
                if not other_pids:
                    continue
                negative_pid = random.choice(other_pids)
                negative = random.choice(pid_to_samples[negative_pid])
                anchors.append(anchor)
                positives.append(positive)
                negatives.append(negative)

        anchors = np.array(anchors)
        positives = np.array(positives)
        negatives = np.array(negatives)

        dataset = tf.data.Dataset.from_tensor_slices((anchors, positives, negatives))
        dataset = dataset.shuffle(1024)

        num_samples = len(anchors)
        train_size = int(0.8 * num_samples)
        train_dataset = dataset.take(train_size).batch(32).prefetch(tf.data.AUTOTUNE)
        val_dataset = dataset.skip(train_size).batch(32).prefetch(tf.data.AUTOTUNE)

        input_shape = (med_len, len(cols))
        embedding_model = self.create_embedding_model(input_shape)

        anchor_input = layers.Input(input_shape, name="anchor")
        positive_input = layers.Input(input_shape, name="positive")
        negative_input = layers.Input(input_shape, name="negative")

        distances = DistanceLayer()(
            embedding_model(anchor_input),
            embedding_model(positive_input),
            embedding_model(negative_input)
        )
        siamese_network = Model(inputs=[anchor_input, positive_input, negative_input], outputs=distances)

        siamese_model = SiameseModel(siamese_network)
        siamese_model.compile(optimizer=optimizers.Adam(0.0001))
        history = siamese_model.fit(train_dataset, epochs=10, validation_data=val_dataset)

        val_sample = next(iter(val_dataset))
        anchor, positive, negative = val_sample

        anchor_embedding = embedding_model(anchor)
        positive_embedding = embedding_model(positive)
        negative_embedding = embedding_model(negative)

        cosine_sim = metrics.CosineSimilarity()
        pos_sim = cosine_sim(anchor_embedding, positive_embedding)
        neg_sim = cosine_sim(anchor_embedding, negative_embedding)

        print(f"Mean positive similarity: {np.mean(pos_sim.numpy())}")
        print(f"Mean negative similarity: {np.mean(neg_sim.numpy())}")

        self.assertTrue(np.mean(pos_sim.numpy()) > np.mean(neg_sim.numpy()))

    @staticmethod
    def create_embedding_model(input_shape):
        inputs = layers.Input(input_shape)
        x = layers.Conv1D(64, 3, activation='relu')(inputs)
        x = layers.MaxPooling1D(2)(x)
        x = layers.Conv1D(128, 3, activation='relu')(x)
        x = layers.GlobalAveragePooling1D()(x)
        x = layers.Dense(256, activation='relu')(x)
        x = layers.BatchNormalization()(x)
        x = layers.Dense(128)(x)
        # Add L2 normalization to the embeddings
        outputs = layers.Lambda(lambda x: tf.math.l2_normalize(x, axis=-1))(x)
        return Model(inputs, outputs)


class DistanceLayer(layers.Layer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def call(self, anchor, positive, negative):
        ap_distance = K.sum(tf.square(anchor - positive), axis=-1)
        an_distance = K.sum(tf.square(anchor - negative), axis=-1)
        # Return distances as a single tensor with shape [batch_size, 2]
        return tf.stack([ap_distance, an_distance], axis=1)


class SiameseModel(Model):
    def __init__(self, siamese_network, margin=0.5):
        super().__init__()
        self.siamese_network = siamese_network
        self.margin = margin
        self.loss_tracker = metrics.Mean(name="loss")

    def call(self, inputs):
        return self.siamese_network(inputs)

    def train_step(self, data):
        with tf.GradientTape() as tape:
            loss = self._compute_loss(data)
        gradients = tape.gradient(loss, self.siamese_network.trainable_weights)
        self.optimizer.apply_gradients(zip(gradients, self.siamese_network.trainable_weights))
        self.loss_tracker.update_state(loss)
        return {"loss": self.loss_tracker.result()}

    def test_step(self, data):
        loss = self._compute_loss(data)
        self.loss_tracker.update_state(loss)
        return {"loss": self.loss_tracker.result()}

    def _compute_loss(self, data):
        distances = self.siamese_network(data)
        ap_distance = distances[:, 0]  # Get positive distances
        an_distance = distances[:, 1]  # Get negative distances
        loss = ap_distance - an_distance
        loss = tf.maximum(loss + self.margin, 0.0)
        return tf.reduce_mean(loss)  # Return mean loss as a scalar

    @property
    def metrics(self):
        return [self.loss_tracker]


if __name__ == '__main__':
    unittest.main()