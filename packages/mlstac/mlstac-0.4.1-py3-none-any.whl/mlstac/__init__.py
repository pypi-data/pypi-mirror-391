"""
MLSTAC: A machine learning model-sharing specification based on STAC MLM and Safetensors.

MLSTAC is a Python package designed for seamless machine learning model sharing and loading.
It builds on the STAC MLM specification for standardized model metadata and utilizes Safetensors
for secure and efficient model storage.

With MLSTAC, you can discover, download, and load ML models with a single line of code from various
data repositories, making model deployment and integration easier than ever.

Example:
    >>> import mlstac
    >>>
    >>> # Download a model from remote JSON
    >>> model = mlstac.download(
    ...     file="https://example.com/model.json",
    ...     output_dir="./models/mymodel"
    ... )
    >>>
    >>> # Or load from local path
    >>> model = mlstac.ModelLoader("./models/mymodel")
    >>>
    >>> # View model metadata
    >>> model.print_schema()
    >>>
    >>> # Load for inference
    >>> compiled_model = model.compiled_model()
    >>>
    >>> # Predict on large arrays
    >>> result = model.predict_large(image, model=compiled_model, device="cuda")
    >>>
    >>> # Load for training
    >>> trainable_model = model.trainable_model()
"""

from mlstac.main import ModelLoader, download, load


__all__ = ["ModelLoader", "download", "load"]


# Dynamic version import
import importlib.metadata

__version__ = importlib.metadata.version("mlstac")