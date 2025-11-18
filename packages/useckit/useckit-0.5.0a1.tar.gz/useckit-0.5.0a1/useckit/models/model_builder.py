from useckit.models.model_architectures import *
from useckit.util.dataset import Dataset
import keras
from .model_architectures import ModelArchitecture, Paradigm, mb_dl4tsc, mb_dl4tsc_lower

class ModelBuilder:
    def __init__(self, useckit_dataset: Dataset):
        self.data = useckit_dataset

    @staticmethod
    def check_valid(architecture, paradigm):
        if isinstance(architecture, str):
            architecture = ModelArchitecture.get_by_string(architecture)
        if isinstance(paradigm, str):
            paradigm = Paradigm.get_by_string(paradigm)

        # Check architecture and paradigm validity
        if not isinstance(architecture, ModelArchitecture):
            raise "architecture has to be a valid ModelArchitecture or name"
        if not isinstance(paradigm, Paradigm):
            raise "paradigm has to be a valid Paradigm or name"

        return architecture, paradigm

    def create_model(self, architecture: ModelArchitecture, paradigm: Paradigm,
                     pool_factor=None, kernel_size=None):
        """Central builder method to create a model.

        Expects a 
            1) architecture (e.g., 'resnet', 'mlp', ...), and 
            2) a paradigm (e.g., 'tsc', 'distancelearning', 'binaryverification', 'anomaly_detection').

        This method then returns a model that can be trained. The model that is returned has a distinct input and output.
        For input, the `uscekit_dataset` that is based via __init__ is used.
        For output, the respective returned model has a last layer and produces return-values that are subject to the paradigm.
        It is as follows:
        - for DistanceLearning, the model has a single output unit at the end which yields a distance obtained from the input-samples.
        - for BinaryVerification, the model has two output units that predict the probability if input falls into the trained class (= first neuron output),
            or any other class (= second neuron output). Therefore, [1, 0] would mean that the sample belongs to the trained class for 100%. The output is softmaxed.
        - for TimeSeriesClassification, the model returns a one-hot encoded vector from [0, ..., N] for N clsases. The output is softmaxed.
        """
        # Convert argument strings into enum
        architecture, paradigm = self.check_valid(architecture, paradigm)


        input_shape = self.data.trainset_data.shape[1:]
        output_size = len(self.data.get_unique_labels())
        
        input_layer, mid = mb_dl4tsc(architecture, input_shape, pool_factor, kernel_size)
        
        if paradigm == Paradigm.TSC:
            output_layer, args = mb_dl4tsc_lower(architecture, mid, output_size)
        if paradigm == Paradigm.BV:
            output_layer, args = mb_bv_lower(architecture, mid, output_size)
        if paradigm == Paradigm.AD:
            output_layer, args = mb_ad_lower(architecture, mid, output_size, input_shape)
        if paradigm == Paradigm.CL:
            output_layer, args = mb_dl4cl_lower(architecture, mid, output_size)
        if paradigm == Paradigm.TL:
            output_layer, args = mb_dl4tl_lower(architecture, mid, output_size) 
            
        
        model = keras.models.Model(inputs=input_layer, outputs=output_layer)

        model.compile(*args) # args = (optimizer, loss, metrics); this order is required
        
        return model
