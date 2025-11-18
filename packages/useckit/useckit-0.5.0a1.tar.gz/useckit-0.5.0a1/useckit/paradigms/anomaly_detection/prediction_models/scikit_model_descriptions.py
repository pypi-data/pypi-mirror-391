from abc import ABC, abstractmethod

from sklearn.ensemble import RandomForestRegressor


class ScikitBaseDescription(ABC):

    @abstractmethod
    def build_model(self):
        pass


class ScikitRegressor(ScikitBaseDescription):

    def __init__(self, scikit_regressor_class=RandomForestRegressor, regressor_kwargs: dict = None):
        self.regressor_class = scikit_regressor_class
        self.regressor_kwargs = dict() if regressor_kwargs is None else regressor_kwargs

    def build_model(self):
        return self.regressor_class(**self.regressor_kwargs)
