import numpy as np

from useckit.paradigms.distance_learning.prediction_models.distance_prediction_model_base import \
    DistanceBasePredictionModel


def _create_all_distance_pairs(p_array_1: np.ndarray, p_array_2: np.ndarray,
                               distance_metric: DistanceBasePredictionModel,
                               tradeoff_computation_speed_for_memory: bool):
    assert p_array_1[0].shape == p_array_2[0].shape  # beyond their length, the arrays need to have the same shape
    if tradeoff_computation_speed_for_memory:
        return _create_distance_pairs_iteration(p_array_1, p_array_2,
                                                distance_metric)
    else:
        return _create_distance_pairs_broadcasting(p_array_1, p_array_2,
                                                   distance_metric)


# This method creates all possible pairs between p1 and p2 and passes them as one to the distance metric. This avoids
# the inefficient streaming that occurs when passing the pairs individually to the distance metric, but it consumes a
# lot more memory.
def _create_distance_pairs_broadcasting(p_array_1: np.ndarray, p_array_2: np.ndarray,
                                        distance_metric: DistanceBasePredictionModel):
    # gather all pairs that have to be predicted before later splitting them back up into the predictions for the
    # individual p_array_1
    p1_broadcast_array_shape = [len(p_array_2) * len(p_array_1)]  # because we compare
    # each sample in p1 with every sample in p2, we need enough space to store as many p1 and p2 sample pairs
    for s in p_array_2.shape[1:]:  # each other dimension needs to be equivalent to a single sample
        p1_broadcast_array_shape.append(s)
    # p1_broadcast_array_shape and p2_broadcast_array hold the two sides of the pairs and thus have the same shape
    p1_broadcast_array = np.zeros(shape=tuple(p1_broadcast_array_shape), dtype=p_array_2.dtype)
    p2_broadcast_array = np.zeros(shape=tuple(p1_broadcast_array_shape), dtype=p_array_2.dtype)
    p1_original_indices = np.zeros(
        shape=(len(p_array_2) * len(p_array_1),), dtype=int)  # this will contain the original
    # indices of the broadcasted p_array_1
    broadcast_index = 0
    for index, sample in enumerate(p_array_1):
        sample_broadcast = np.broadcast_to(sample, shape=p_array_2.shape)
        indices = np.ones(shape=(len(p_array_2),)) * index
        from_i = broadcast_index
        to_i = broadcast_index + len(sample_broadcast)

        p1_broadcast_array[from_i:to_i] = sample_broadcast
        p2_broadcast_array[from_i:to_i] = p_array_2
        p1_original_indices[from_i:to_i] = indices

        broadcast_index = to_i
    distances = distance_metric.predict(p1_broadcast_array, p2_broadcast_array)
    return distances, p1_original_indices


# This method gathers batches of len(p_array_2) many pairs and calculates the distances between them. This strikes a
# balance between the computationally fastest method above and memory efficiency,
def _create_distance_pairs_iteration(p_array_1: np.ndarray, p_array_2: np.ndarray,
                                     distance_metric: DistanceBasePredictionModel):
    distances = np.zeros(
        shape=(len(p_array_2) * len(p_array_1),))  # result
    p1_original_indices = np.zeros(
        shape=(len(p_array_2) * len(p_array_1),), dtype=int)  # this will contain the original
    # indices of the broadcasted p_array_1
    broadcast_index = 0
    for index, sample in enumerate(p_array_1):
        sample_broadcast = np.broadcast_to(sample, shape=p_array_2.shape)
        indices = np.ones(shape=(len(p_array_2),)) * index
        from_i = broadcast_index
        to_i = broadcast_index + len(sample_broadcast)

        sample_distances = distance_metric.predict(sample_broadcast, p_array_2)
        distances[from_i:to_i] = sample_distances
        p1_original_indices[from_i:to_i] = indices

        broadcast_index = to_i
    return distances, p1_original_indices
