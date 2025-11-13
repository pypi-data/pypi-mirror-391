import numpy as np
from keras.layers import Input
from keras.models import Model
from qkeras.qlayers import QActivation, QDense
from qkeras.quantizers import quantized_bits

from triggerflow.core import TriggerModel


def make_dummy_model():

    inputs = Input(shape=(57,))

    x = QDense(
        units=64,
        name='fc1',
        kernel_quantizer=quantized_bits(bits=6, alpha=1),
        bias_quantizer=quantized_bits(bits=6, alpha=1)
    )(inputs)

    x = QActivation("quantized_relu(3)")(x)

    outputs = QDense(
        units=1,
        name='last',
        kernel_quantizer=quantized_bits(bits=6, alpha=1),
        bias_quantizer=quantized_bits(bits=6, alpha=1)
    )(x)

    model = Model(inputs=inputs, outputs=outputs)
    return model



def test_predict():
    name = "Dummy"
    dummy_model = make_dummy_model()
    scales = {'offsets': np.array([18, 0, 72, 7, 0, 73, 4, 0, 73, 4, 0, 72, 3, 0, 72, 6, -0, 286, 3, -2, 285, 3, -2, 282, 3, -2, 286, 29, 0, 72, 22, 0, 72, 18, 0, 72, 14, 0, 72, 11, 0, 72, 10, 0, 72, 10, 0, 73, 9, 0, 73, 9, 0, 72, 8, -2, 72], dtype='int'),
          'shifts': np.array([3, 0, 6, 2, 5, 6, 0, 5, 6, 0, 5, 6, -1, 5, 6, 2, 7, 8, 0, 7, 8, 0, 7, 8, 0, 7, 8, 4, 6, 6, 3, 6, 6, 3, 6, 6, 3, 6, 6, 3, 6, 6, 3, 6, 6, 3, 6, 6, 3, 6, 6, 3, 6, 6, 2, 6, 6], dtype='int')}
    triggerflow = TriggerModel(
        name=name,
        scales=scales,
        ml_backend="Keras",
        n_outputs=1,
        compiler="hls4ml",
        native_model=dummy_model,
        compiler_config=None
    )
    triggerflow(project_name = name+"_project", namespace = name, write_weights_txt = False)
    input_data = np.ones((10,57))
    output = triggerflow.software_predict(input_data)
    output = triggerflow.firmware_predict(input_data)
    output = triggerflow.qonnx_predict(input_data)
    assert output is not None

