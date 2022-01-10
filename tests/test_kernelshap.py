from unittest import TestCase

import dianna
import numpy as np
from dianna.methods import KernelSHAP


class ShapOnImages(TestCase):
    def test_shap_segment_image(self):
        input_data = np.random.random((28, 28, 1))

        explainer = dianna.methods.KernelSHAP()
        # most arguments are chosen by default
        # https://scikit-image.org/docs/dev/api/skimage.segmentation.html#skimage.segmentation.slic
        n_segments = 50
        compactness = 10.0
        sigma = 0
        channel_axis_first = False
        image_segments = explainer._segment_image(
            input_data,
            n_segments,
            compactness,
            sigma,
            channel_axis_first
        )
        # check segments index
        assert np.amax(image_segments) <= n_segments
        # check image shape after segmentation
        assert image_segments.shape == input_data[:, :, 0].shape

    def test_shap_mask_image(self):
        # check image with channel axis = -1
        input_data = np.random.random((28, 28, 1))
        explainer = dianna.methods.KernelSHAP()
        n_segments = 50
        compactness = 10.0
        sigma = 0
        channel_axis_first = False
        segments_slic = explainer._segment_image(
            input_data,
            n_segments,
            compactness,
            sigma,
            channel_axis_first
        )
        masked_image = explainer._mask_image(
            np.zeros((1, n_segments)), segments_slic, input_data, 0, False
        )
        # check if all points are masked
        assert np.array_equal(masked_image[0], np.zeros(input_data.shape))

        # check image with channel axis = 0
        input_data = np.random.random((1, 28, 28))
        channel_axis_first = True
        segments_slic = explainer._segment_image(
            input_data,
            n_segments,
            compactness,
            sigma,
            channel_axis_first
        )
        masked_image = explainer._mask_image(
            np.zeros((1, n_segments)), segments_slic, input_data, 0, True
        )
        # check if all points are masked
        assert np.array_equal(masked_image[0], np.zeros(input_data.shape))

    def test_shap_explain_image(self):
        input_data = np.random.random((1, 28, 28))
        onnx_model_path = "./tests/test_data/mnist_model.onnx"
        n_segments = 50
        explainer = KernelSHAP()
        shap_values, segments_slic = explainer.explain_image(
            onnx_model_path,
            input_data,
            nsamples=1000,
            background=0,
            n_segments=n_segments,
            compactness=10.0,
            sigma=0,
            channel_axis_first=True,
        )

        assert shap_values[0].shape == np.zeros((1, n_segments)).shape

