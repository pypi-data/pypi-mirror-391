import inspect
from abc import ABC, abstractmethod

from sklearn.svm import SVC


class ScikitBaseDescription(ABC):

    @abstractmethod
    def build_model(self):
        pass


class ScikitClassif(ScikitBaseDescription):
    def __init__(self, scikit_classif_class=SVC, classif_kwargs: dict = None):
        self.classif_class = scikit_classif_class
        # Check if 'probability' is a valid parameter for the classifier
        if 'probability' in inspect.signature(self.classif_class.__init__).parameters:
            # Add 'probability: True' only if it's a valid parameter
            default_kwargs = {'probability': True}
        else:
            default_kwargs = {}
        # Update default_kwargs with user provided classif_kwargs
        self.classif_kwargs = default_kwargs if classif_kwargs is None else {**default_kwargs, **classif_kwargs}

    def build_model(self):
        # Create an instance of the classifier with the appropriate kwargs
        return self.classif_class(**self.classif_kwargs)
