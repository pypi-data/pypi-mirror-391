from typing import Any, Dict, Optional, Protocol, Tuple

from chalk.ml.utils import ModelClass, ModelEncoding, ModelType


class ModelInference(Protocol):
    """Abstract base class for model loading and inference."""

    def load_model(self, path: str) -> Any:
        """Load a model from the given path."""
        pass

    def predict(self, model: Any, X: Any) -> Any:
        """Run inference on the model with input X."""
        pass


class XGBoostClassifierInference(ModelInference):
    """Model inference for XGBoost classifiers."""

    def load_model(self, path: str) -> Any:
        import xgboost  # pyright: ignore[reportMissingImports]

        model = xgboost.XGBClassifier()
        model.load_model(path)
        return model

    def predict(self, model: Any, X: Any) -> Any:
        return model.predict(X)


class XGBoostRegressorInference(ModelInference):
    """Model inference for XGBoost regressors."""

    def load_model(self, path: str) -> Any:
        import xgboost  # pyright: ignore[reportMissingImports]

        model = xgboost.XGBRegressor()
        model.load_model(path)
        return model

    def predict(self, model: Any, X: Any) -> Any:
        return model.predict(X)


class PyTorchInference(ModelInference):
    """Model inference for PyTorch models."""

    def load_model(self, path: str) -> Any:
        import torch  # pyright: ignore[reportMissingImports]

        torch.set_grad_enabled(False)
        model = torch.jit.load(path)
        model.input_to_tensor = lambda X: torch.from_numpy(X).float()
        return model

    def predict(self, model: Any, X: Any) -> Any:
        outputs = model(model.input_to_tensor(X))
        result = outputs.detach().numpy().astype("float64")
        result = result.squeeze()

        # Convert 0-dimensional array to scalar, or ensure we have a proper 1D array
        if result.ndim == 0:
            return result.item()

        return result


class SklearnInference(ModelInference):
    """Model inference for scikit-learn models."""

    def load_model(self, path: str) -> Any:
        import joblib  # pyright: ignore[reportMissingImports]

        return joblib.load(path)

    def predict(self, model: Any, X: Any) -> Any:
        return model.predict(X)


class TensorFlowInference(ModelInference):
    """Model inference for TensorFlow models."""

    def load_model(self, path: str) -> Any:
        import tensorflow  # pyright: ignore[reportMissingImports]

        return tensorflow.keras.models.load_model(path)

    def predict(self, model: Any, X: Any) -> Any:
        return model.predict(X)


class LightGBMInference(ModelInference):
    """Model inference for LightGBM models."""

    def load_model(self, path: str) -> Any:
        import lightgbm  # pyright: ignore[reportMissingImports]

        return lightgbm.Booster(model_file=path)

    def predict(self, model: Any, X: Any) -> Any:
        return model.predict(X)


class CatBoostInference(ModelInference):
    """Model inference for CatBoost models."""

    def load_model(self, path: str) -> Any:
        import catboost  # pyright: ignore[reportMissingImports]

        return catboost.CatBoost().load_model(path)

    def predict(self, model: Any, X: Any) -> Any:
        return model.predict(X)


class ONNXInference(ModelInference):
    """Model inference for ONNX models."""

    def load_model(self, path: str) -> Any:
        import onnxruntime  # pyright: ignore[reportMissingImports]

        return onnxruntime.InferenceSession(path)

    def predict(self, model: Any, X: Any) -> Any:
        import numpy as np

        # Get input names from the model metadata
        input_names = [inp.name for inp in model.get_inputs()]

        # Convert X to float32 if needed
        X_float32 = X.astype("float32") if hasattr(X, "astype") else np.array(X, dtype="float32")

        # If there's only one input, use it directly
        if len(input_names) == 1:
            input_dict = {input_names[0]: X_float32}
        else:
            # For multiple inputs, we'd need additional logic
            # For now, assume the first input is the main one
            input_dict = {input_names[0]: X_float32}

        return model.run(None, input_dict)[0]


class ModelInferenceRegistry:
    """Registry for model inference implementations."""

    def __init__(self):
        super().__init__()
        self._registry: Dict[Tuple[ModelType, ModelEncoding, Optional[ModelClass]], ModelInference] = {}

    def register(
        self,
        model_type: ModelType,
        encoding: ModelEncoding,
        model_class: Optional[ModelClass],
        inference: ModelInference,
    ) -> None:
        """Register a model inference implementation."""
        self._registry[(model_type, encoding, model_class)] = inference

    def register_for_all_classes(
        self,
        model_type: ModelType,
        encoding: ModelEncoding,
        inference: ModelInference,
    ) -> None:
        """Register inference for None, CLASSIFICATION, and REGRESSION variants."""
        self.register(model_type, encoding, None, inference)
        self.register(model_type, encoding, ModelClass.CLASSIFICATION, inference)
        self.register(model_type, encoding, ModelClass.REGRESSION, inference)

    def get(
        self,
        model_type: ModelType,
        encoding: ModelEncoding,
        model_class: Optional[ModelClass] = None,
    ) -> Optional[ModelInference]:
        """Get a model inference implementation from the registry."""
        return self._registry.get((model_type, encoding, model_class), None)

    def get_loader(
        self,
        model_type: ModelType,
        encoding: ModelEncoding,
        model_class: Optional[ModelClass] = None,
    ):
        """Get the load_model function for a given configuration."""
        inference = self.get(model_type, encoding, model_class)
        return inference.load_model if inference else None

    def get_predictor(
        self,
        model_type: ModelType,
        encoding: ModelEncoding,
        model_class: Optional[ModelClass] = None,
    ):
        """Get the predict function for a given configuration."""
        inference = self.get(model_type, encoding, model_class)
        return inference.predict if inference else None


# Global registry instance
MODEL_REGISTRY = ModelInferenceRegistry()

# Register all model types
MODEL_REGISTRY.register_for_all_classes(ModelType.PYTORCH, ModelEncoding.PICKLE, PyTorchInference())
MODEL_REGISTRY.register_for_all_classes(ModelType.SKLEARN, ModelEncoding.PICKLE, SklearnInference())
MODEL_REGISTRY.register_for_all_classes(ModelType.TENSORFLOW, ModelEncoding.HDF5, TensorFlowInference())
MODEL_REGISTRY.register_for_all_classes(ModelType.LIGHTGBM, ModelEncoding.TEXT, LightGBMInference())
MODEL_REGISTRY.register_for_all_classes(ModelType.CATBOOST, ModelEncoding.CBM, CatBoostInference())
MODEL_REGISTRY.register_for_all_classes(ModelType.ONNX, ModelEncoding.PROTOBUF, ONNXInference())

# XGBoost requires different implementations for classification vs regression
MODEL_REGISTRY.register(ModelType.XGBOOST, ModelEncoding.JSON, None, XGBoostRegressorInference())
MODEL_REGISTRY.register(ModelType.XGBOOST, ModelEncoding.JSON, ModelClass.CLASSIFICATION, XGBoostClassifierInference())
MODEL_REGISTRY.register(ModelType.XGBOOST, ModelEncoding.JSON, ModelClass.REGRESSION, XGBoostRegressorInference())
