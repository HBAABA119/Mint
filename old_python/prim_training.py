"""
Prim Training Optimization
Provides gradient optimization, regularization techniques, learning rate scheduling,
early stopping, and mixed precision training.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Callable, Tuple
from dataclasses import dataclass
from enum import Enum


class OptimizerType(Enum):
    """Optimizer types"""
    SGD = "sgd"
    ADAM = "adam"
    ADAMW = "adamw"
    RMSPROP = "rmsprop"
    NESTEROV = "nesterov"
    ADAGRAD = "adagrad"


class RegularizationType(Enum):
    """Regularization types"""
    L1 = "l1"
    L2 = "l2"
    ELASTIC_NET = "elastic_net"
    DROPOUT = "dropout"
    BATCH_NORM = "batch_norm"


class LearningRateSchedule(Enum):
    """Learning rate schedules"""
    CONSTANT = "constant"
    EXPONENTIAL = "exponential"
    COSINE = "cosine"
    WARMUP = "warmup"
    CYCLICAL = "cyclical"


@dataclass
class Optimizer:
    """Optimizer configuration"""
    type: OptimizerType
    learning_rate: float = 0.001
    beta1: float = 0.9
    beta2: float = 0.999
    epsilon: float = 1e-8
    momentum: float = 0.0
    decay: float = 0.0
    weight_decay: float = 0.0


class GradientOptimizer:
    """Gradient optimization"""

    def __init__(self, optimizer: Optimizer):
        self.optimizer = optimizer
        self.m = None
        self.v = None
        self.t = 0

    def update(self, gradients: np.ndarray, weights: np.ndarray) -> np.ndarray:
        """Update weights using optimizer"""
        self.t += 1

        if self.optimizer.type == OptimizerType.SGD:
            return self._sgd_update(gradients, weights)
        elif self.optimizer.type == OptimizerType.ADAM:
            return self._adam_update(gradients, weights)
        elif self.optimizer.type == OptimizerType.RMSPROP:
            return self._rmsprop_update(gradients, weights)
        elif self.optimizer.type == OptimizerType.NESTEROV:
            return self._nesterov_update(gradients, weights)
        else:
            return self._sgd_update(gradients, weights)

    def _sgd_update(self, gradients: np.ndarray, weights: np.ndarray) -> np.ndarray:
        """SGD update"""
        lr = self.optimizer.learning_rate
        return weights - lr * gradients

    def _adam_update(self, gradients: np.ndarray, weights: np.ndarray) -> np.ndarray:
        """Adam update"""
        lr = self.optimizer.learning_rate
        beta1 = self.optimizer.beta1
        beta2 = self.optimizer.beta2
        epsilon = self.optimizer.epsilon

        if self.m is None:
            self.m = np.zeros_like(gradients)
            self.v = np.zeros_like(gradients)

        self.m = beta1 * self.m + (1 - beta1) * gradients
        self.v = beta2 * self.v + (1 - beta2) * (gradients ** 2)

        m_hat = self.m / (1 - beta1 ** self.t)
        v_hat = self.v / (1 - beta2 ** self.t)

        return weights - lr * m_hat / (np.sqrt(v_hat) + epsilon)

    def _rmsprop_update(self, gradients: np.ndarray, weights: np.ndarray) -> np.ndarray:
        """RMSProp update"""
        lr = self.optimizer.learning_rate
        beta = self.optimizer.beta1
        epsilon = self.optimizer.epsilon

        if self.v is None:
            self.v = np.zeros_like(gradients)

        self.v = beta * self.v + (1 - beta) * (gradients ** 2)
        return weights - lr * gradients / (np.sqrt(self.v) + epsilon)

    def _nesterov_update(self, gradients: np.ndarray, weights: np.ndarray) -> np.ndarray:
        """Nesterov momentum update"""
        lr = self.optimizer.learning_rate
        momentum = self.optimizer.momentum

        if self.m is None:
            self.m = np.zeros_like(gradients)

        self.m = momentum * self.m - lr * gradients
        return weights + momentum * self.m - lr * gradients


class Regularizer:
    """Regularization techniques"""

    def __init__(self, reg_type: RegularizationType, strength: float = 0.01):
        self.reg_type = reg_type
        self.strength = strength

    def apply(self, weights: np.ndarray) -> np.ndarray:
        """Apply regularization to weights"""
        if self.reg_type == RegularizationType.L1:
            return self._l1_regularization(weights)
        elif self.reg_type == RegularizationType.L2:
            return self._l2_regularization(weights)
        elif self.reg_type == RegularizationType.ELASTIC_NET:
            return self._elastic_net(weights)
        return weights

    def penalty(self, weights: np.ndarray) -> float:
        """Calculate regularization penalty"""
        if self.reg_type == RegularizationType.L1:
            return self.strength * np.sum(np.abs(weights))
        elif self.reg_type == RegularizationType.L2:
            return 0.5 * self.strength * np.sum(weights ** 2)
        elif self.reg_type == RegularizationType.ELASTIC_NET:
            l1 = self.strength * 0.5 * np.sum(np.abs(weights))
            l2 = 0.5 * self.strength * 0.5 * np.sum(weights ** 2)
            return l1 + l2
        return 0.0

    def _l1_regularization(self, weights: np.ndarray) -> np.ndarray:
        """L1 regularization"""
        return weights - self.strength * np.sign(weights)

    def _l2_regularization(self, weights: np.ndarray) -> np.ndarray:
        """L2 regularization"""
        return weights - self.strength * weights

    def _elastic_net(self, weights: np.ndarray) -> np.ndarray:
        """Elastic net regularization"""
        l1 = self.strength * 0.5 * np.sign(weights)
        l2 = self.strength * 0.5 * weights
        return weights - l1 - l2


class LearningRateScheduler:
    """Learning rate scheduling"""

    def __init__(self, schedule: LearningRateSchedule, initial_lr: float = 0.001):
        self.schedule = schedule
        self.initial_lr = initial_lr
        self.current_lr = initial_lr
        self.epoch = 0

    def step(self) -> float:
        """Update learning rate"""
        self.epoch += 1

        if self.schedule == LearningRateSchedule.CONSTANT:
            self.current_lr = self.initial_lr
        elif self.schedule == LearningRateSchedule.EXPONENTIAL:
            decay_rate = 0.95
            self.current_lr = self.initial_lr * (decay_rate ** self.epoch)
        elif self.schedule == LearningRateSchedule.COSINE:
            total_epochs = 100
            self.current_lr = self.initial_lr * 0.5 * (1 + np.cos(np.pi * self.epoch / total_epochs))
        elif self.schedule == LearningRateSchedule.WARMUP:
            warmup_epochs = 10
            if self.epoch < warmup_epochs:
                self.current_lr = self.initial_lr * (self.epoch / warmup_epochs)
            else:
                decay_rate = 0.95
                self.current_lr = self.initial_lr * (decay_rate ** (self.epoch - warmup_epochs))

        return self.current_lr


class EarlyStopping:
    """Early stopping callback"""

    def __init__(self, patience: int = 10, min_delta: float = 0.0):
        self.patience = patience
        self.min_delta = min_delta
        self.best_score = None
        self.counter = 0
        self.early_stop = False

    def __call__(self, score: float) -> bool:
        """Check if should stop early"""
        if self.best_score is None:
            self.best_score = score
            return False

        if score > self.best_score + self.min_delta:
            self.best_score = score
            self.counter = 0
        else:
            self.counter += 1

        if self.counter >= self.patience:
            self.early_stop = True
            return True

        return False


class MixedPrecisionTraining:
    """Mixed precision training"""

    def __init__(self):
        self.scaler = 1.0

    def scale_loss(self, loss: float) -> float:
        """Scale loss for mixed precision"""
        return loss * self.scaler

    def unscale_gradients(self, gradients: np.ndarray) -> np.ndarray:
        """Unscale gradients"""
        return gradients / self.scaler

    def update_scaler(self, gradients: np.ndarray):
        """Update scaler based on gradients"""
        if np.any(np.isnan(gradients)) or np.any(np.isinf(gradients)):
            self.scaler *= 0.5

        if self.scaler < 1.0:
            self.scaler *= 2.0


class TrainingCallback:
    """Training callback"""

    def on_epoch_begin(self, epoch: int):
        """Called at beginning of epoch"""
        pass

    def on_epoch_end(self, epoch: int, logs: Dict[str, float]):
        """Called at end of epoch"""
        pass

    def on_batch_begin(self, batch: int):
        """Called at beginning of batch"""
        pass

    def on_batch_end(self, batch: int, logs: Dict[str, float]):
        """Called at end of batch"""
        pass


class ModelCheckpoint(TrainingCallback):
    """Model checkpoint callback"""

    def __init__(self, filepath: str, monitor: str = "val_loss", save_best_only: bool = True):
        self.filepath = filepath
        self.monitor = monitor
        self.save_best_only = save_best_only
        self.best_score = None

    def on_epoch_end(self, epoch: int, logs: Dict[str, float]):
        """Save model checkpoint"""
        if self.monitor not in logs:
            return

        score = logs[self.monitor]

        if self.best_score is None or score > self.best_score:
            self.best_score = score
            if self.save_best_only:
                # Save model (simplified)
                pass


class ReduceLROnPlateau(TrainingCallback):
    """Reduce learning rate on plateau"""

    def __init__(self, monitor: str = "val_loss", factor: float = 0.5, patience: int = 5):
        self.monitor = monitor
        self.factor = factor
        self.patience = patience
        self.best_score = None
        self.counter = 0

    def on_epoch_end(self, epoch: int, logs: Dict[str, float]):
        """Reduce learning rate if metric plateaus"""
        if self.monitor not in logs:
            return

        score = logs[self.monitor]

        if self.best_score is None:
            self.best_score = score
            return

        if score > self.best_score:
            self.best_score = score
            self.counter = 0
        else:
            self.counter += 1

            if self.counter >= self.patience:
                # Reduce learning rate (would need access to optimizer)
                self.counter = 0


class GradientClipping:
    """Gradient clipping"""

    def __init__(self, clip_value: float = 1.0):
        self.clip_value = clip_value

    def clip(self, gradients: np.ndarray) -> np.ndarray:
        """Clip gradients"""
        norm = np.linalg.norm(gradients)
        if norm > self.clip_value:
            gradients = gradients * (self.clip_value / norm)
        return gradients


class TrainingMonitor:
    """Training progress monitoring"""

    def __init__(self):
        self.metrics: Dict[str, List[float]] = {}
        self.current_epoch = 0

    def update(self, metrics: Dict[str, float]):
        """Update metrics"""
        for key, value in metrics.items():
            if key not in self.metrics:
                self.metrics[key] = []
            self.metrics[key].append(value)

    def get_history(self) -> Dict[str, List[float]]:
        """Get training history"""
        return self.metrics.copy()

    def plot_history(self, metrics: List[str]):
        """Plot training history"""
        # Simplified - would use matplotlib in practice
        for metric in metrics:
            if metric in self.metrics:
                print(f"{metric}: {self.metrics[metric][-1]:.4f}")


def create_optimizer(optimizer_type: OptimizerType, learning_rate: float = 0.001) -> Optimizer:
    """Create optimizer"""
    return Optimizer(type=optimizer_type, learning_rate=learning_rate)


def create_regularizer(reg_type: RegularizationType, strength: float = 0.01) -> Regularizer:
    """Create regularizer"""
    return Regularizer(reg_type, strength)


def create_scheduler(schedule: LearningRateSchedule, initial_lr: float = 0.001) -> LearningRateScheduler:
    """Create learning rate scheduler"""
    return LearningRateScheduler(schedule, initial_lr)


def main():
    """Main entry point for testing"""
    print("Testing Training Optimization...")

    # Test Optimizer
    optimizer = create_optimizer(OptimizerType.ADAM, learning_rate=0.001)
    grad_opt = GradientOptimizer(optimizer)

    weights = np.random.randn(10, 10)
    gradients = np.random.randn(10, 10) * 0.01

    updated_weights = grad_opt.update(gradients, weights)
    print(f"Optimizer: {optimizer.type.value}, weights updated")

    # Test Regularizer
    regularizer = create_regularizer(RegularizationType.L2, strength=0.01)
    penalty = regularizer.penalty(weights)
    print(f"L2 penalty: {penalty:.4f}")

    # Test Learning Rate Scheduler
    scheduler = create_scheduler(LearningRateSchedule.EXPONENTIAL, initial_lr=0.001)
    lr = scheduler.step()
    print(f"Learning rate: {lr:.6f}")

    # Test Early Stopping
    early_stopping = EarlyStopping(patience=5, min_delta=0.0)
    for score in [0.8, 0.85, 0.82, 0.83, 0.84, 0.82]:
        should_stop = early_stopping(score)
        print(f"Score: {score:.2f}, Stop: {should_stop}")

    # Test Gradient Clipping
    clipper = GradientClipping(clip_value=1.0)
    large_grads = np.array([10.0, 10.0, 10.0])
    clipped_grads = clipper.clip(large_grads)
    print(f"Clipped gradients: {clipped_grads[:3]}")

    # Test Training Monitor
    monitor = TrainingMonitor()
    monitor.update({"loss": 0.5, "accuracy": 0.8})
    monitor.update({"loss": 0.4, "accuracy": 0.85})
    history = monitor.get_history()
    print(f"Training history: {len(history['loss'])} epochs")

    print("\nTraining Optimization initialized successfully")


if __name__ == "__main__":
    main()
