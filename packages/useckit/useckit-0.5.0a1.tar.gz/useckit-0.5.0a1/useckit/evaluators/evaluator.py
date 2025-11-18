from useckit.models import ModelBuilder, ModelArchitecture,  Paradigm
from useckit.util.dataset import Dataset
import numpy as np
import keras

class Evaluator:
    def __init__(self, dataset: Dataset, architecture: ModelArchitecture, paradigm: Paradigm, threshold: list[float] | float | None = None, threshold_scope = None, classification_strategy  = None):
        self._architecture, self._paradigm = ModelBuilder.check_valid(architecture, paradigm)
        
        self._data = dataset
        self._classification_strategy = classification_strategy
        self._model_builder = ModelBuilder(dataset)
        self.models: dict[int, keras.Model] = self.generate_models()
    
    def generate_models(self):
        models = None
        
        if self._paradigm in [Paradigm.TSC]:
            models.append(self._model_builder.create_model(self._architecture, self._paradigm))
        
        if self._paradigm in [Paradigm.BV, Paradigm.AD]:
            models = {}
            labels = self._data.get_unique_labels()
            
            if self._classification_strategy == "ovr":
                for key in labels:
                    models.update({key: self._model_builder.create_model(self._architecture, self._paradigm)})
            
            if self._classification_strategy == "ovo":
                for num, key1 in enumerate(labels[:-1]):
                    for key2 in labels[num + 1:]:
                        models.update({(key1, key2): self._model_builder.create_model(self._architecture, self._paradigm)})
        
        return models
    
    def fit(self):
        if self._paradigm in [Paradigm.BV]:
            if self._classification_strategy == "ovr":
                for key, model in self.models.items():
                    y_true = (self._data.trainset_labels == key).astype(int)
                    
                    model.fit(
                        self._data.trainset_data,
                        y_true,
                        epochs=1,
                        batch_size=32,
                        verbose=1
                    )
            
            if self._classification_strategy == "ovo":
                for (key1, key2), model in self.models.items():
                    data_mask = (self._data.trainset_labels == key1) | (self._data.trainset_labels == key2)
                    selected_data = self._data.trainset_data[data_mask]
                    selected_labels = self._data.trainset_labels[data_mask]
                    
                    y_true = (selected_labels == key1).astype(int)
                    
                    model.fit(
                        selected_data,
                        y_true,
                        epochs=1,
                        batch_size=32,
                        verbose=1
                    )
                    print(model.predict_proba(self._data.trainset_data))
    
    def evaluate(self):
        for keys, model in self.models.items():
            pass

if __name__ == "__main__":
    # Example usage
    (trainset_data, trainset_labels), (testset_data, testset_labels) = keras.datasets.fashion_mnist.load_data()
    trainset_data = (trainset_data / 255).astype(np.float16)
    testset_data = (testset_data / 255).astype(np.float16)
    dataset = Dataset(
        trainset_data=trainset_data,
        trainset_labels=trainset_labels,
        testset_enrollment_data=trainset_data,
        testset_enrollment_labels=trainset_labels,
        testset_matching_data=testset_data,
        testset_matching_labels=testset_labels
    )
    architecture = ModelArchitecture.RESNET
    paradigm = Paradigm.BV
    
    evaluator = Evaluator(dataset, architecture, paradigm, classification_strategy="ovo")
    evaluator.fit()
    evaluator.evaluate()