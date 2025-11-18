
from useckit.tests.test_utils import make_some_intelligent_noise
from useckit.util.dataset import Dataset
from useckit.models.model_builder import ModelBuilder
from useckit.models.model_architectures import ModelArchitecture, Paradigm


x_train, y_train = make_some_intelligent_noise(shape=(100, 100, 100))
x_val, y_val = make_some_intelligent_noise(shape=(110, 100, 100))
x_enroll, y_enroll = make_some_intelligent_noise(shape=(120, 100, 100))
x_test, y_test = make_some_intelligent_noise(shape=(130, 100, 100))
dataset = Dataset(x_train, y_train, x_val, y_val, x_enroll, y_enroll, x_test, y_test)

builder = ModelBuilder(dataset)

twiesn = builder.create_model(ModelArchitecture.TWIESN, Paradigm.TSC)

twiesn.fit(dataset)

df_metrics, train_acc, ridge_classifier = twiesn.train()
print(df_metrics, train_acc)