from useckit.models.model_builder import ModelBuilder, ModelArchitecture, Paradigm
from useckit.util.dataset import Dataset
import unittest
import keras
import numpy
from sklearn.metrics import matthews_corrcoef, accuracy_score

class TestModelFactory(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.unittest_execution_counter = 1

    def load_prep_data(self):
        (trainset_data, trainset_labels), (testset_data, testset_labels) = keras.datasets.fashion_mnist.load_data()
        trainset_data = (trainset_data / 255).astype(numpy.float16)
        testset_data = (testset_data / 255).astype(numpy.float16)
        class_names = ["T-shirt/top", "Trouser", "Pullover", "Dress", "Coat", "Sandal", "Shirt", "Sneaker", "Bag", "Ankle boot"]
        return Dataset(
            trainset_data=trainset_data,
            trainset_labels=trainset_labels,
            testset_enrollment_data=trainset_data,
            testset_enrollment_labels=trainset_labels,
            testset_matching_data=testset_data,
            testset_matching_labels=testset_labels
        ), class_names

    def test_bv_one_one(self):
        dataset, class_names = self.load_prep_data()
        class_names = class_names[:2]
        train_indices = numpy.where(dataset.trainset_labels >= 2)
        test_indices = numpy.where(dataset.testset_matching_labels >= 2)
        
        dataset.trainset_labels = numpy.delete(dataset.trainset_labels, train_indices)
        dataset.testset_matching_labels = numpy.delete(dataset.testset_matching_labels, test_indices)
        dataset.trainset_data = numpy.delete(dataset.trainset_data, train_indices, axis=0)
        dataset.testset_matching_data = numpy.delete(dataset.testset_matching_data, test_indices, axis=0)
        
        builder = ModelBuilder(dataset)
        model = builder.create_model(ModelArchitecture.MLP, Paradigm.BV)
        
        model.fit(dataset.trainset_data, dataset.trainset_labels, verbose=2)
        
        y_pred = numpy.round(model.predict(dataset.testset_matching_data, verbose=2))
        y_true = dataset.testset_matching_labels
        
        mcc = matthews_corrcoef(y_true, y_pred)
        test_acc = accuracy_score(y_true, y_pred)

        print("Test accuracy:", test_acc, "Matthews Corrcoef:", mcc)
        
        assert mcc >= 0.85, f"Expected MCC to be >= .85, but encountered: {mcc}"

    def test_bv_one_multiple(self):
        dataset, class_names = self.load_prep_data()
        class_names = class_names[:1] + ["Other"]
        dataset.trainset_labels[dataset.trainset_labels > 0] = 1
        dataset.testset_matching_labels[dataset.testset_matching_labels > 0] = 1
        
        builder = ModelBuilder(dataset)
        model = builder.create_model(ModelArchitecture.RESNET, "binary_verification")
        
        model.fit(dataset.trainset_data, dataset.trainset_labels, verbose=2)
        
        y_pred = numpy.round(model.predict(dataset.testset_matching_data, verbose=2))
        y_true = dataset.testset_matching_labels
        
        mcc = matthews_corrcoef(y_true, y_pred)
        test_acc = accuracy_score(y_true, y_pred)

        print("Test accuracy:", test_acc, "Matthews Corrcoef:", mcc)
        
        assert mcc >= 0.65, f"Expected MCC to be >= .65, but encountered: {mcc}"


if __name__ == '__main__':
    unittest.main()
