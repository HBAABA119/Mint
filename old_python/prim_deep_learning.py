"""
Prim Deep Learning Framework
Provides deep learning architectures, CNN, RNN, Transformers, attention mechanisms,
and model composition.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum


class LayerType(Enum):
    """Layer types"""
    DENSE = "dense"
    CONV2D = "conv2d"
    MAX_POOL2D = "max_pool2d"
    LSTM = "lstm"
    GRU = "gru"
    TRANSFORMER = "transformer"
    ATTENTION = "attention"
    DROPOUT = "dropout"
    BATCH_NORM = "batch_norm"
    EMBEDDING = "embedding"


class Activation(Enum):
    """Activation functions"""
    RELU = "relu"
    GELU = "gelu"
    SWISH = "swish"
    TANH = "tanh"
    SIGMOID = "sigmoid"
    SOFTMAX = "softmax"


@dataclass
class Layer:
    """Neural network layer"""
    name: str
    layer_type: LayerType
    units: int = 0
    activation: Activation = Activation.RELU
    kernel_size: Optional[Tuple[int, int]] = None
    pool_size: Optional[Tuple[int, int]] = None
    dropout_rate: float = 0.0
    weights: Optional[np.ndarray] = None
    biases: Optional[np.ndarray] = None
    trainable: bool = True


class Conv2DLayer(Layer):
    """2D Convolutional layer"""

    def __init__(self, filters: int, kernel_size: Tuple[int, int], activation: Activation = Activation.RELU):
        super().__init__(
            name="conv2d",
            layer_type=LayerType.CONV2D,
            units=filters,
            activation=activation,
            kernel_size=kernel_size
        )
        self.filters = filters
        self.kernel_size = kernel_size

    def initialize_weights(self, input_channels: int):
        """Initialize convolutional weights"""
        kh, kw = self.kernel_size
        self.weights = np.random.randn(kh, kw, input_channels, self.filters) * 0.01
        self.biases = np.zeros(self.filters)


class MaxPool2DLayer(Layer):
    """2D Max pooling layer"""

    def __init__(self, pool_size: Tuple[int, int] = (2, 2)):
        super().__init__(
            name="max_pool2d",
            layer_type=LayerType.MAX_POOL2D,
            pool_size=pool_size
        )
        self.pool_size = pool_size


class LSTMLayer(Layer):
    """LSTM layer"""

    def __init__(self, units: int, return_sequences: bool = True):
        super().__init__(
            name="lstm",
            layer_type=LayerType.LSTM,
            units=units
        )
        self.return_sequences = return_sequences
        self.input_weights = None
        self.recurrent_weights = None
        self.bias = None

    def initialize_weights(self, input_size: int):
        """Initialize LSTM weights"""
        # Simplified LSTM weight initialization
        self.input_weights = np.random.randn(input_size, self.units * 4) * 0.01
        self.recurrent_weights = np.random.randn(self.units, self.units * 4) * 0.01
        self.bias = np.zeros(self.units * 4)


class AttentionLayer(Layer):
    """Attention layer"""

    def __init__(self, num_heads: int = 8, key_dim: int = 64):
        super().__init__(
            name="attention",
            layer_type=LayerType.ATTENTION
        )
        self.num_heads = num_heads
        self.key_dim = key_dim
        self.query_weights = None
        self.key_weights = None
        self.value_weights = None

    def initialize_weights(self, input_dim: int):
        """Initialize attention weights"""
        self.query_weights = np.random.randn(input_dim, self.key_dim) * 0.01
        self.key_weights = np.random.randn(input_dim, self.key_dim) * 0.01
        self.value_weights = np.random.randn(input_dim, self.key_dim) * 0.01


class TransformerLayer(Layer):
    """Transformer layer"""

    def __init__(self, num_heads: int = 8, key_dim: int = 64, ff_dim: int = 256):
        super().__init__(
            name="transformer",
            layer_type=LayerType.TRANSFORMER
        )
        self.num_heads = num_heads
        self.key_dim = key_dim
        self.ff_dim = ff_dim
        self.attention = AttentionLayer(num_heads, key_dim)
        self.feedforward_weights = None

    def initialize_weights(self, input_dim: int):
        """Initialize transformer weights"""
        self.attention.initialize_weights(input_dim)
        self.feedforward_weights = np.random.randn(input_dim, self.ff_dim) * 0.01


class NeuralNetwork:
    """Deep neural network"""

    def __init__(self, name: str = "model"):
        self.name = name
        self.layers: List[Layer] = []
        self.compiled = False
        self.optimizer = "adam"
        self.learning_rate = 0.001
        self.loss_function = "categorical_crossentropy"

    def add_layer(self, layer: Layer):
        """Add layer to network"""
        self.layers.append(layer)

    def compile(self, optimizer: str = "adam", learning_rate: float = 0.001,
                loss: str = "categorical_crossentropy"):
        """Compile the model"""
        self.optimizer = optimizer
        self.learning_rate = learning_rate
        self.loss_function = loss

        # Initialize weights
        input_dim = 784  # Default for MNIST
        for i, layer in enumerate(self.layers):
            if hasattr(layer, 'initialize_weights'):
                if isinstance(layer, Conv2DLayer):
                    layer.initialize_weights(input_dim)
                elif isinstance(layer, LSTMLayer):
                    layer.initialize_weights(input_dim)
                elif isinstance(layer, AttentionLayer):
                    layer.initialize_weights(input_dim)
                elif isinstance(layer, TransformerLayer):
                    layer.initialize_weights(input_dim)

            # Update input_dim for next layer
            if layer.layer_type in [LayerType.DENSE]:
                input_dim = layer.units

        self.compiled = True

    def forward(self, x: np.ndarray) -> np.ndarray:
        """Forward pass"""
        if not self.compiled:
            raise RuntimeError("Model not compiled")

        activations = x
        for layer in self.layers:
            activations = self._apply_layer(layer, activations)
        return activations

    def _apply_layer(self, layer: Layer, x: np.ndarray) -> np.ndarray:
        """Apply layer to input"""
        if layer.layer_type == LayerType.DENSE:
            if layer.weights is None:
                raise RuntimeError("Layer weights not initialized")
            z = np.dot(x, layer.weights) + layer.biases
            return self._apply_activation(layer.activation, z)

        elif layer.layer_type == LayerType.CONV2D:
            if layer.weights is None:
                raise RuntimeError("Layer weights not initialized")
            # Simplified 2D convolution
            return self._conv2d(x, layer.weights, layer.biases, layer.activation)

        elif layer.layer_type == LayerType.MAX_POOL2D:
            return self._max_pool2d(x, layer.pool_size)

        elif layer.layer_type == LayerType.LSTM:
            return self._lstm_forward(x, layer)

        elif layer.layer_type == LayerType.ATTENTION:
            return self._attention_forward(x, layer)

        elif layer.layer_type == LayerType.TRANSFORMER:
            return self._transformer_forward(x, layer)

        else:
            return x

    def _apply_activation(self, activation: Activation, x: np.ndarray) -> np.ndarray:
        """Apply activation function"""
        if activation == Activation.RELU:
            return np.maximum(0, x)
        elif activation == Activation.GELU:
            return 0.5 * x * (1 + np.tanh(np.sqrt(2 / np.pi) * (x + 0.044715 * np.power(x, 3))))
        elif activation == Activation.SWISH:
            return x / (1 + np.exp(-x))
        elif activation == Activation.TANH:
            return np.tanh(x)
        elif activation == Activation.SIGMOID:
            return 1 / (1 + np.exp(-x))
        elif activation == Activation.SOFTMAX:
            exp_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
            return exp_x / np.sum(exp_x, axis=-1, keepdims=True)
        return x

    def _conv2d(self, x: np.ndarray, weights: np.ndarray, biases: np.ndarray,
                activation: Activation) -> np.ndarray:
        """2D convolution (simplified)"""
        # This is a simplified convolution implementation
        # In practice, this would use optimized libraries
        batch_size, height, width, channels = x.shape
        kh, kw, in_channels, out_channels = weights.shape

        output = np.zeros((batch_size, height - kh + 1, width - kw + 1, out_channels))

        for b in range(batch_size):
            for i in range(height - kh + 1):
                for j in range(width - kw + 1):
                    for o in range(out_channels):
                        patch = x[b, i:i+kh, j:j+kw, :]
                        output[b, i, j, o] = np.sum(patch * weights[:, :, :, o]) + biases[o]

        return self._apply_activation(activation, output)

    def _max_pool2d(self, x: np.ndarray, pool_size: Tuple[int, int]) -> np.ndarray:
        """2D max pooling"""
        batch_size, height, width, channels = x.shape
        ph, pw = pool_size

        output = np.zeros((batch_size, height // ph, width // pw, channels))

        for b in range(batch_size):
            for i in range(0, height, ph):
                for j in range(0, width, pw):
                    for c in range(channels):
                        patch = x[b, i:i+ph, j:j+pw, c]
                        output[b, i//ph, j//pw, c] = np.max(patch)

        return output

    def _lstm_forward(self, x: np.ndarray, layer: LSTMLayer) -> np.ndarray:
        """LSTM forward pass (simplified)"""
        batch_size, seq_len, input_size = x.shape
        units = layer.units

        # Simplified LSTM cell computation
        h = np.zeros((batch_size, units))
        c = np.zeros((batch_size, units))
        outputs = []

        for t in range(seq_len):
            x_t = x[:, t, :]
            # Simplified LSTM computation
            h = np.tanh(np.dot(x_t, layer.input_weights[:, :units]))
            outputs.append(h)

        return np.stack(outputs, axis=1)

    def _attention_forward(self, x: np.ndarray, layer: AttentionLayer) -> np.ndarray:
        """Attention forward pass"""
        # Simplified attention mechanism
        queries = np.dot(x, layer.query_weights)
        keys = np.dot(x, layer.key_weights)
        values = np.dot(x, layer.value_weights)

        # Scaled dot-product attention
        scores = np.dot(queries, keys.T) / np.sqrt(layer.key_dim)
        attention_weights = np.exp(scores) / np.sum(np.exp(scores), axis=-1, keepdims=True)
        output = np.dot(attention_weights, values)

        return output

    def _transformer_forward(self, x: np.ndarray, layer: TransformerLayer) -> np.ndarray:
        """Transformer forward pass"""
        # Multi-head attention
        attention_output = self._attention_forward(x, layer.attention)

        # Feed-forward
        ff_output = np.dot(attention_output, layer.feedforward_weights)

        return ff_output

    def predict(self, x: np.ndarray) -> np.ndarray:
        """Make predictions"""
        return self.forward(x)

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
                predictions = self.forward(x_batch)

                # Compute loss
                loss = self._compute_loss(predictions, y_batch)
                epoch_loss += loss

                # Backward pass (simplified)
                self._backward_pass(x_batch, y_batch, predictions)

            avg_loss = epoch_loss / n_batches
            history["loss"].append(avg_loss)

            if validation_data:
                x_val, y_val = validation_data
                val_predictions = self.forward(x_val)
                val_loss = self._compute_loss(val_predictions, y_val)
                history["val_loss"].append(val_loss)

            print(f"Epoch {epoch + 1}/{epochs}, Loss: {avg_loss:.4f}")

        return history

    def _compute_loss(self, predictions: np.ndarray, targets: np.ndarray) -> float:
        """Compute loss"""
        if self.loss_function == "categorical_crossentropy":
            return -np.mean(targets * np.log(predictions + 1e-10))
        elif self.loss_function == "mse":
            return np.mean(np.square(predictions - targets))
        return 0.0

    def _backward_pass(self, x: np.ndarray, y: np.ndarray, predictions: np.ndarray):
        """Backward pass (simplified)"""
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
        return np.ones_like(output)

    def evaluate(self, x: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """Evaluate the model"""
        predictions = self.forward(x)
        loss = self._compute_loss(predictions, y)

        results = {"loss": loss}

        # Calculate accuracy for classification
        if self.loss_function == "categorical_crossentropy":
            accuracy = np.mean(np.argmax(predictions, axis=1) == np.argmax(y, axis=1))
            results["accuracy"] = accuracy

        return results

    def save(self, filepath: str):
        """Save the model"""
        import pickle
        model_data = {
            "name": self.name,
            "layers": [
                {
                    "name": layer.name,
                    "layer_type": layer.layer_type.value,
                    "units": layer.units,
                    "activation": layer.activation.value,
                    "kernel_size": layer.kernel_size,
                    "pool_size": layer.pool_size,
                    "dropout_rate": layer.dropout_rate,
                    "weights": layer.weights.tolist() if layer.weights is not None else None,
                    "biases": layer.biases.tolist() if layer.biases is not None else None,
                }
                for layer in self.layers
            ],
            "optimizer": self.optimizer,
            "learning_rate": self.learning_rate,
            "loss_function": self.loss_function
        }

        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)

    @classmethod
    def load(cls, filepath: str) -> 'NeuralNetwork':
        """Load a model"""
        import pickle
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)

        model = cls(model_data["name"])
        model.optimizer = model_data["optimizer"]
        model.learning_rate = model_data["learning_rate"]
        model.loss_function = model_data["loss_function"]

        for layer_data in model_data["layers"]:
            layer_type = LayerType(layer_data["layer_type"])
            activation = Activation(layer_data["activation"])

            if layer_type == LayerType.CONV2D:
                layer = Conv2DLayer(
                    filters=layer_data["units"],
                    kernel_size=layer_data["kernel_size"],
                    activation=activation
                )
            elif layer_type == LayerType.LSTM:
                layer = LSTMLayer(units=layer_data["units"])
            elif layer_type == LayerType.ATTENTION:
                layer = AttentionLayer()
            elif layer_type == LayerType.TRANSFORMER:
                layer = TransformerLayer()
            else:
                layer = Layer(
                    name=layer_data["name"],
                    layer_type=layer_type,
                    units=layer_data["units"],
                    activation=activation
                )

            if layer_data["weights"]:
                layer.weights = np.array(layer_data["weights"])
            if layer_data["biases"]:
                layer.biases = np.array(layer_data["biases"])

            model.add_layer(layer)

        model.compiled = True
        return model


def create_sequential(name: str = "sequential") -> NeuralNetwork:
    """Create a sequential neural network"""
    return NeuralNetwork(name)


def main():
    """Main entry point for testing"""
    print("Testing Deep Learning Framework...")

    # Create a CNN model
    model = create_sequential("cnn_model")

    # Add layers
    model.add_layer(Conv2DLayer(filters=32, kernel_size=(3, 3), activation=Activation.RELU))
    model.add_layer(MaxPool2DLayer(pool_size=(2, 2)))
    model.add_layer(Layer(name="flatten", layer_type=LayerType.DENSE, units=128, activation=Activation.RELU))
    model.add_layer(Layer(name="output", layer_type=LayerType.DENSE, units=10, activation=Activation.SOFTMAX))

    # Compile model
    model.compile(optimizer="adam", learning_rate=0.001, loss="categorical_crossentropy")

    print(f"Model created with {len(model.layers)} layers")

    # Test prediction
    x_test = np.random.randn(10, 28, 28, 1)
    predictions = model.predict(x_test)
    print(f"Predictions shape: {predictions.shape}")

    # Test save/load
    model.save("test_model.pkl")
    loaded_model = NeuralNetwork.load("test_model.pkl")
    print(f"Loaded model: {loaded_model.name}")

    print("\nDeep Learning Framework initialized successfully")


if __name__ == "__main__":
    main()
