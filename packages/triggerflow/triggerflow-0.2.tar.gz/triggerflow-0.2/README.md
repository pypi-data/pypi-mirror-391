# Machine Learning for Hardware Triggers

`triggerflow` provides a set of utilities for Machine Learning models targeting FPGA deployment. 
The `TriggerModel` class consolidates several Machine Learning frontends and compiler backends to construct a "trigger model". MLflow utilities are for logging, versioning, and loading of trigger models.

## Installation

```bash
pip install triggerflow
```

## Usage

```python

from triggerflow.core import TriggerModel

triggerflow = TriggerModel(name="my-trigger-model", ml_backend="Keras", compiler="hls4ml", model, compiler_config or None)
triggerflow() # call the constructor

# then:
output_software = triggerflow.software_predict(input_data)
output_firmware = triggerflow.firmware_predict(input_data)
output_qonnx = triggerflow.qonnx_predict(input_data)

# save and load trigger models:
triggerflow.save("triggerflow.tar.xz")

# in a separate session:
from triggerflow.core import TriggerModel
triggerflow = TriggerModel.load("triggerflow.tar.xz")
```

## Logging with MLflow

```python
# logging with MLFlow:
import mlflow
from triggerflow.mlflow_wrapper import log_model

mlflow.set_tracking_uri("https://ngt.cern.ch/models")
experiment_id = mlflow.create_experiment("example-experiment")

with mlflow.start_run(run_name="trial-v1", experiment_id=experiment_id):
    log_model(triggerflow, registered_model_name="TriggerModel")
```

### Note: This package doesn't install dependencies so it won't disrupt specific training environments or custom compilers. For a reference environment, see `environment.yml`.


# Creating a kedro pipeline

This repository also comes with a default pipeline for trigger models based on kedro.
One can create a new pipeline via:

NOTE: no "-" and upper cases!

```bash
# Create a conda environment & activate it
conda create -n triggerflow python=3.11
conda activate triggerflow

# install triggerflow
pip install triggerflow

# Create a pipeline
triggerflow new demo_pipeline

# NOTE: since we dont install dependency one has to create a
# conda env based on the environment.yml file of the pipeline
# this file can be changed to the needs of the indiviual project
cd demo_pipeline
conda env update -n triggerflow --file environment.yml

# Run Kedro
kedro run
```