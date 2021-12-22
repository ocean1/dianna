from unittest import TestCase
import numpy as np
import dianna
import dianna.visualization
from dianna.methods import LIME
from tests.test_onnx_runner import generate_data
from tests.utils import ModelRunner, run_model


class LimeOnImages(TestCase):

    def test_lime_function(self):
        np.random.seed(42)
        input_data = np.random.random((1, 224, 224, 3))
        labels = ('batch', 'y', 'x', 'channels')

        explainer = LIME(random_state=42, axes_labels=labels)
        heatmap = explainer.explain_image(run_model, input_data, num_samples=100)
        heatmap_expected = np.load('tests/test_data/heatmap_lime_function.npy')
        assert heatmap.shape == input_data[0].shape[:2]
        assert np.allclose(heatmap, heatmap_expected, atol=.01)

    def test_lime_filename(self):
        np.random.seed(42)
        model_filename = 'tests/test_data/mnist_model.onnx'

        black_and_white = generate_data(batch_size=1)
        # Make data 3-channel instead of 1-channel
        input_data = np.zeros([1, 3] + list(black_and_white.shape[2:])) + black_and_white
        input_data = input_data.astype(np.float32)
        labels = ('batch', 'channels', 'y', 'x')

        def preprocess(data):
            # select single channel out of 3, but keep the channel axis
            return data[:, [0], ...]

        heatmap = dianna.explain_image(model_filename, input_data, method="LIME", preprocess_function=preprocess, random_state=42,
                                       axes_labels=labels)

        heatmap_expected = np.load('tests/test_data/heatmap_lime_filename.npy')
        assert heatmap.shape == input_data[0, 0].shape
        assert np.allclose(heatmap, heatmap_expected, atol=.01)


def test_lime_text():
    model_path = 'tests/test_data/movie_review_model.onnx'
    word_vector_file = 'tests/test_data/word_vectors.txt'
    runner = ModelRunner(model_path, word_vector_file, max_filter_size=5)

    review = 'such a bad movie'

    explanation = dianna.explain_text(runner, review, labels=[0], method='LIME', random_state=42)[0]
    words = [element[0] for element in explanation]
    word_indices = [element[1] for element in explanation]
    scores = [element[2] for element in explanation]

    expected_words = ['bad', 'such', 'movie', 'a']
    expected_word_indices = [7, 0, 11, 5]
    expected_scores = [.492, -.046, .036, -.008]
    assert words == expected_words
    assert word_indices == expected_word_indices
    assert np.allclose(scores, expected_scores, atol=.01)
