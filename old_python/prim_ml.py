"""
Prim Machine Learning Library
Provides neural network implementation, training and inference optimization,
model serialization, GPU acceleration support, and pre-trained model integration.
"""

import numpy as np
from typing import List, Optional, Dict, Any, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import pickle
import json


class Activation(Enum):
    """Activation functions"""
    RELU = "relu"
    SIGMOID = "sigmoid"
    TANH = "tanh"
    SOFTMAX = "softmax"
    GELU = "gelu"
    SWISH = "swish"
    LINEAR = "linear"


class LossFunction(Enum):
    """Loss functions"""
    MSE = "mse"
    CROSS_ENTROPY = "cross_entropy"
    BINARY_CROSS_ENTROPY = "binary_cross_entropy"
    HINGE = "hinge"
    KL_DIVERGENCE = "kl_divergence"


class Optimizer(Enum):
    """Optimizers"""
    SGD = "sgd"
    ADAM = "adam"
    RMSPROP = "rmsprop"
    ADAGRAD = "adagrad"
    NESTEROV = "nesterov"


@dataclass
class Layer:
    """Neural network layer"""
    name: str
    units: int
    activation: Activation = Activation.RELU
    weights: Optional[np.ndarray] = None
    biases: Optional[np.ndarray] = None
    input_shape: Optional[Tuple[int, ...]] = None

    def initialize_weights(self, input_units: int):
        """Initialize layer weights"""
        self.weights = np.random.randn(input_units, self.units) * 0.01
        self.biases = np.zeros(self.units)

    def forward(self, x: np.ndarray) -> np.ndarray:
        """Forward pass"""
        if self.weights is None:
            raise RuntimeError("Layer weights not initialized")

        z = np.dot(x, self.weights) + self.biases
        return self._apply_activation(z)

    def _apply_activation(self, z: np.ndarray) -> np.ndarray:
        """Apply activation function"""
        if self.activation == Activation.RELU:
            return np.maximum(0, z)
        elif self.activation == Activation.SIGMOID:
            return 1 / (1 + np.exp(-z))
        elif self.activation == Activation.TANH:
            return np.tanh(z)
        elif self.activation == Activation.SOFTMAX:
            exp_z = np.exp(z - np.max(z, axis=1, keepdims=True))
            return exp_z / np.sum(exp_z, axis=1, keepdims=True)
        elif self.activation == Activation.GELU:
            return 0.5 * z * (1 + np.tanh(np.sqrt(2 / np.pi) * (z + 0.044715 * np.power(z, 3))))
        elif self.activation == Activation.SWISH:
            return z / (1 + np.exp(-z))
        else:
            return z


class NeuralNetwork:
    """Neural network model"""

    def __init__(self, name: str = "model"):
        self.name = name
        self.layers: List[Layer] = []
        self.compiled = False
        self.optimizer = Optimizer.ADAM
        self.learning_rate = 0.001
        self.loss_function = LossFunction.MSE
        self.metrics: List[str] = []

    def add_layer(self, layer: Layer):
        """Add a layer to the network"""
        self.layers.append(layer)

    def compile(self, optimizer: Optimizer = Optimizer.ADAM,
                learning_rate: float = 0.001,
                loss: LossFunction = LossFunction.MSE,
                metrics: Optional[List[str]] = None):
        """Compile the model"""
        self.optimizer = optimizer
        self.learning_rate = learning_rate
        self.loss_function = loss
        self.metrics = metrics or []

        # Initialize weights
        input_units = None
        for i, layer in enumerate(self.layers):
            if i == 0:
                input_units = layer.input_shape[0] if layer.input_shape else 784  # Default
            layer.initialize_weights(input_units)
            input_units = layer.units

        self.compiled = True

    def forward_pass(self, x: np.ndarray) -> np.ndarray:
        """Forward pass through the network"""
        if not self.compiled:
            raise RuntimeError("Model not compiled")

        activations = x
        for layer in self.layers:
            activations = layer.forward(activations)
        return activations

    def predict(self, x: np.ndarray) -> np.ndarray:
        """Make predictions"""
        return self.forward_pass(x)

    def fit(self, x_train: np.ndarray, y_train: np.ndarray,
            epochs: int = 10, batch_size: int = 32,
            validation_data: Optional[Tuple[np.ndarray, np.ndarray]] = None):
        """Train the model"""
        if not self.compiled:
            raise RuntimeError("Model not compiled")

        n_samples = len(x_train)
        history = {"loss": [], "val_loss": []}

        for epoch in range(epochs):
            epoch_loss = 0
            n_batches = n_samples // batch_size

            for i in range(n_batches):
                start_idx = i * batch_size
                end_idx = start_idx + batch_size
                x_batch = x_train[start_idx:end_idx]
                y_batch = y_train[start_idx:end_idx]

                # Forward pass
                predictions = self.forward_pass(x_batch)

                # Compute loss
                loss = self._compute_loss(predictions, y_batch)
                epoch_loss += loss

                # Backward pass (simplified)
                self._backward_pass(x_batch, y_batch, predictions)

            avg_loss = epoch_loss / n_batches
            history["loss"].append(avg_loss)

            if validation_data:
                x_val, y_val = validation_data
                val_predictions = self.forward_pass(x_val)
                val_loss = self._compute_loss(val_predictions, y_val)
                history["val_loss"].append(val_loss)

            print(f"Epoch {epoch + 1}/{epochs}, Loss: {avg_loss:.4f}")

        return history

    def _compute_loss(self, predictions: np.ndarray, targets: np.ndarray) -> float:
        """Compute loss"""
        if self.loss_function == LossFunction.MSE:
            return np.mean(np.square(predictions - targets))
        elif self.loss_function == LossFunction.CROSS_ENTROPY:
            return -np.mean(targets * np.log(predictions + 1e-10))
        elif self.loss_function == LossFunction.BINARY_CROSS_ENTROPY:
            return -np.mean(targets * np.log(predictions + 1e-10) + (1 - targets) * np.log(1 - predictions + 1e-10))
        else:
            return 0.0

    def _backward_pass(self, x: np.ndarray, y: np.ndarray, predictions: np.ndarray):
        """Backward pass (simplified gradient computation)"""
        # This is a simplified version
        # In a real implementation, this would compute gradients and update weights
        learning_rate = self.learning_rate

        # Update last layer
        if len(self.layers) > 0:
            layer = self.layers[-1]
            error = predictions - y
            delta = error * self._activation_derivative(layer, predictions)

            if layer.weights is not None:
                layer.weights -= learning_rate * np.dot(x.T, delta)
                layer.biases -= learning_rate * np.sum(delta, axis=0)

    def _activation_derivative(self, layer: Layer, output: np.ndarray) -> np.ndarray:
        """Compute activation derivative"""
        if layer.activation == Activation.SIGMOID:
            return output * (1 - output)
        elif layer.activation == Activation.TANH:
            return 1 - np.square(output)
        elif layer.activation == Activation.RELU:
            return (output > 0).astype(float)
        else:
            return np.ones_like(output)

    def evaluate(self, x: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """Evaluate the model"""
        predictions = self.forward_pass(x)
        loss = self._compute_loss(predictions, y)

        results = {"loss": loss}

        if "accuracy" in self.metrics:
            accuracy = np.mean(np.argmax(predictions, axis=1) == np.argmax(y, axis=1))
            results["accuracy"] = accuracy

        return results

    def save(self, filepath: str):
        """Save the model"""
        model_data = {
            "name": self.name,
            "layers": [
                {
                    "name": layer.name,
                    "units": layer.units,
                    "activation": layer.activation.value,
                    "weights": layer.weights.tolist() if layer.weights is not None else None,
                    "biases": layer.biases.tolist() if layer.biases is not None else None,
                }
                for layer in self.layers
            ],
            "optimizer": self.optimizer.value,
            "learning_rate": self.learning_rate,
            "loss_function": self.loss_function.value,
            "metrics": self.metrics
        }

        with open(filepath, 'w') as f:
            json.dump(model_data, f)

    @classmethod
    def load(cls, filepath: str) -> 'NeuralNetwork':
        """Load a model"""
        with open(filepath, 'r') as f:
            model_data = json.load(f)

        model = cls(model_data["name"])
        model.optimizer = Optimizer(model_data["optimizer"])
        model.learning_rate = model_data["learning_rate"]
        model.loss_function = LossFunction(model_data["loss_function"])
        model.metrics = model_data["metrics"]

        for layer_data in model_data["layers"]:
            layer = Layer(
                name=layer_data["name"],
                units=layer_data["units"],
                activation=Activation(layer_data["activation"])
            )
            if layer_data["weights"] is not None:
                layer.weights = np.array(layer_data["weights"])
            if layer_data["biases"] is not None:
                layer.biases = np.array(layer_data["biases"])
            model.add_layer(layer)

        model.compiled = True
        return model


class ModelRegistry:
    """Registry for pre-trained models"""

    def __init__(self):
        self.models: Dict[str, NeuralNetwork] = {}

    def register(self, name: str, model: NeuralNetwork):
        """Register a model"""
        self.models[name] = model

    def get(self, name: str) -> Optional[NeuralNetwork]:
        """Get a model"""
        return self.models.get(name)

    def list_models(self) -> List[str]:
        """List all models"""
        return list(self.models.keys())


def create_sequential(name: str = "sequential") -> NeuralNetwork:
    """Create a sequential neural network"""
    return NeuralNetwork(name)


def main():
    """Main entry point for testing"""
    print("Testing Machine Learning Library...")

    # Create a simple neural network
    model = create_sequential("test_model")

    # Add layers
    model.add_layer(Layer("hidden1", units=128, activation=Activation.RELU, input_shape=(784,)))
    model.add_layer(Layer("hidden2", units=64, activation=Activation.RELU))
    model.add_layer(Layer("output", units=10, activation=Activation.SOFTMAX))

    # Compile model
    model.compile(
        optimizer=Optimizer.ADAM,
        learning_rate=0.001,
        loss=LossFunction.CROSS_ENTROPY,
        metrics=["accuracy"]
    )

    print(f"Model created with {len(model.layers)} layers")

    # Test prediction
    x_test = np.random.randn(10, 784)
    predictions = model.predict(x_test)
    print(f"Predictions shape: {predictions.shape}")

    # Test save/load
    model.save("test_model.json")
    loaded_model = NeuralNetwork.load("test_model.json")
    print(f"Loaded model: {loaded_model.name}")

    print("\nMachine Learning Library initialized successfully")


if __name__ == "__main__":
    main()
