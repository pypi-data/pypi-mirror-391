import re
import unittest
import os
import shutil
import urllib.request
import hashlib
import subprocess
from glob import glob
from statistics import median

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from keras import Sequential
from keras.src.layers import Dense
from keras.src.optimizers import Adam
from keras.src.utils import pad_sequences
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import LabelBinarizer

import useckit


class TestModelBuilder_TSC(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up the test class and download the dataset if needed."""
        cls.dataset_dir = os.path.join(os.path.dirname(__file__), "resources", "pychi-2021")
        try:
            cls.download_tsc_dataset()
        except AssertionError:
            cls.download_tsc_dataset(reinstall=True)

    @classmethod
    def download_tsc_dataset(cls, dataset_path=None, reinstall=False):
        """Download and extract the dataset to the temporary directory.
        Download only happens if dataset path is set to None"""
        
        if dataset_path is None and reinstall:
            shutil.rmtree(cls.dataset_dir)

        if dataset_path is not None:
            cls.dataset_dir = dataset_path  # Set dataset directory manually if provided
            print(f"Using provided dataset {cls.dataset_dir} ...")
        elif not os.path.exists(cls.dataset_dir):
            os.mkdir(cls.dataset_dir)
            
            print("Using temporary directory:", cls.dataset_dir)

            # The dataset is a split archive of two files
            file1 = "Data_Set_for_Understanding_User_Identification_in_Virtual_Reality_Through_Behavioral_Biometrics_and_the_Effect_of_Body_Normalization.7z.001"
            file2 = "Data_Set_for_Understanding_User_Identification_in_Virtual_Reality_Through_Behavioral_Biometrics_and_the_Effect_of_Body_Normalization.7z.002"

            print("Testing for files and deciding whether to download and extract dataset ...")

            dataset_zip_path1 = os.path.join(cls.dataset_dir, file1)
            dataset_zip_path2 = os.path.join(cls.dataset_dir, file2)

            print(f"Downloading dataset to {cls.dataset_dir} ...")
            urllib.request.urlretrieve(
                "https://hci.informatik.uni-due.de/fileadmin/fileupload/I-HCI/Paper/Data_Set_for_Understanding_User_Identification_in_Virtual_Reality_Through_Behavioral_Biometrics_and_the_Effect_of_Body_Normalization.7z.001",
                dataset_zip_path1)
            urllib.request.urlretrieve(
                "https://hci.informatik.uni-due.de/fileadmin/fileupload/I-HCI/Paper/Data_Set_for_Understanding_User_Identification_in_Virtual_Reality_Through_Behavioral_Biometrics_and_the_Effect_of_Body_Normalization.7z.002",
                dataset_zip_path2)

            print("Checking hashsum ...")
            with open(dataset_zip_path1, "rb") as f:
                bytes = f.read()
                readable_hash = hashlib.sha256(bytes).hexdigest()
                print(f"sha256sum of {dataset_zip_path1} is", readable_hash)
                assert readable_hash == "1235b224ba131c36fc70a29a2e381f8ec0f5d7aa51c6ad09e576068c2c1c8d7d", \
                    'hashsum did not match expectation. Please try the download again.'

            with open(dataset_zip_path2, "rb") as f:
                bytes = f.read()
                readable_hash = hashlib.sha256(bytes).hexdigest()
                print(f"sha256sum of {dataset_zip_path2} is", readable_hash)
                assert readable_hash == "3110f9603a07a0259eabff73c399ebb679880f28390d48ca6480623e2c79bda2", \
                    'hashsum did not match expectation. Please try the download again.'

            print("sha256sum is ok.")

            print("Unzipping dataset ...")
            subprocess.run([
                    "7z", "x", dataset_zip_path1, "-o" + cls.dataset_dir, "-y"
            ], check=True)
            print(f"Finished extracting dataset to `{cls.dataset_dir}`.")
            os.remove(os.path.join(cls.dataset_dir, file1))
            os.remove(os.path.join(cls.dataset_dir, file2))

            assert len(glob(os.path.join(f"{cls.dataset_dir}/*csv"))) == 3072  # assert correct number of files
            print("Verified the extraction of 3072 csv files.")
        else:
            print(f"Using already installed dataset {cls.dataset_dir} ...")

    @classmethod
    def load_dataset(cls, n_jobs=-1):
        filename_pattern = r'(?P<activity>\w+)_p(?P<pid>\d+)_(?P<condition>\w+)_session(?P<session>\d+)_repetition(?P<rep>\d+)\.csv'

        file_paths = glob(f"{cls.dataset_dir}/*.csv")

        def process_single_file(g):
            filename = os.path.basename(g)
            match = re.match(filename_pattern, filename)

            assert match, f"Did not find a match for file {filename}"
            parsed_data = match.groupdict()

            df = pd.read_csv(g)

            # remove extra columns
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

            cols_to_drop = [
                "ParticipantID", "study_session", "repetition", "timestamp_ms", "phase",
                "HeightNormalization", "ArmLengthNormalization"
            ]
            cols_to_drop += [col for col in df.columns if
                             col.lower().startswith(("ball",
                                                     "arrow",
                                                     "rightcontrolleranchor",
                                                     "leftcontrolleranchor",
                                                     "scenario"))]
            df.drop(columns=cols_to_drop, inplace=True, errors='raise')

            return {
                'df': df,
                'pid': f"P{parsed_data['pid']}",
                'condition': parsed_data['condition'],
                'session': int(parsed_data['session']),
                'rep': int(parsed_data['rep']),
                'activity': parsed_data['activity']
            }

        DATASET = Parallel(n_jobs=n_jobs)(delayed(process_single_file)(g) for g in file_paths)
        return DATASET

    @classmethod
    def preprocess_sample(cls, df) -> pd.DataFrame:
        from sklearn.preprocessing import MinMaxScaler

        # local vectors head -> virt. hands
        for lr in ["Left", "Right"]:
            for XYZ in ["X", "Y", "Z"]:
                df[f"{lr}VirtualHand_pos_{XYZ}"] -= df[f"CenterEyeAnchor_pos_{XYZ}"]

        df.drop(columns=['CenterEyeAnchor_pos_X', 'CenterEyeAnchor_pos_Y', 'CenterEyeAnchor_pos_Z',
                         'CenterEyeAnchor_euler_X', 'CenterEyeAnchor_euler_Y', 'CenterEyeAnchor_euler_Z'], inplace=True)

        # iloc zero method to make everything relative to the beginning
        for c in df.columns:
            df[c] -= df[c].iloc[0]

        # Min Max Scaling
        cols = df.columns
        arr = MinMaxScaler().fit_transform(df)
        df = pd.DataFrame(arr, columns=cols)

        return df


    def test_modelbuilder_tsc(self):
        DATASET = self.load_dataset()

        # remove all but Bowling from loaded dataset
        DATASET = [d for d in DATASET if d['activity'].lower() == "bowling"]

        assert len(DATASET) == 1536, f"Expected dataset to have length 1536, but found {len(DATASET)} entries."

        # apply preprocessing to every sample
        for d in DATASET:
            d['df'] = self.preprocess_sample(d['df'])

        # pad length of all samples to median length
        med_len = int(median(len(d['df']) for d in DATASET))
        cols = DATASET[0]['df'].columns

        for d, d_padded in zip(DATASET, pad_sequences([d['df'] for d in DATASET], maxlen=med_len, dtype='float32')):
            d['df'] = pd.DataFrame(d_padded, columns=cols)

        x_train = np.array([d['df'].to_numpy() for d in DATASET if d['session'] == 1])
        y_train = np.array([d['pid'] for d in DATASET if d['session'] == 1])

        x_test = np.array([d['df'].to_numpy() for d in DATASET if d['session'] == 2])
        y_test = np.array([d['pid'] for d in DATASET if d['session'] == 2])

        # Flatten for model training
        x_train = x_train.reshape(x_train.shape[0], -1)
        x_test = x_test.reshape(x_test.shape[0], -1)

        # OHC labels
        lb = LabelBinarizer()
        y_train_ohc = lb.fit_transform(y_train)
        y_test_ohc = lb.transform(y_test)

        useckit_dataset = useckit.Dataset(trainset_data=x_train,
                                          trainset_labels=y_train,
                                          validationset_data=x_train,
                                          validationset_labels=y_train,
                                          testset_matching_data=x_test,
                                          testset_matching_labels=y_test)

        num_classes = y_train_ohc.shape[1]

        def make_model_regular():
            # start simple keras mlp (to be exchanged against model builder)
            model = Sequential([
                Dense(64, activation='relu'), #, input_shape=(num_features,)),
                Dense(32, activation='relu'),
                Dense(num_classes, activation='softmax')  # Softmax for multiclass classification
            ])
            optimizer = Adam(learning_rate=0.001)
            model.compile(optimizer=optimizer, loss='categorical_crossentropy', metrics=['accuracy'])
            return model

        def make_model_modelbuilder():
            from useckit.models.model_builder import ModelBuilder
            mb = ModelBuilder(useckit_dataset)
            model = mb.create_model("mlp", "time_series_classification")
            return model

        use_model_builder = True

        if use_model_builder:
            model = make_model_modelbuilder()
        else:
            model = make_model_regular()

        # Train model
        model.fit(x_train, y_train_ohc, epochs=50, batch_size=16, validation_data=(x_test, y_test_ohc), verbose=1)

        loss, accuracy = model.evaluate(x_test, y_test_ohc, verbose=1)

        # do prediction for test accuracy and CM
        y_pred_ohc = model.predict(x_test)
        y_pred = lb.inverse_transform(y_pred_ohc)

        cm = confusion_matrix(y_test, y_pred)
        print("Confusion Matrix:\n", cm)
        print(f"Test Accuracy: {accuracy:.4f}")



if __name__ == '__main__':
    unittest.main()
