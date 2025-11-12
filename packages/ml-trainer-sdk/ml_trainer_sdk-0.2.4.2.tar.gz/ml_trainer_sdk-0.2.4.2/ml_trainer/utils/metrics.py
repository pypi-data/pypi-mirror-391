import torch
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support,
    confusion_matrix, classification_report,
    mean_absolute_error, mean_squared_error, r2_score
    )

from typing import Dict, List, Optional, Union, Any
from abc import ABC, abstractmethod


class BaseMetrics(ABC):
    """Abstract base class for all metrics calculators."""
    
    def __init__(self):
        self.reset()
    
    @abstractmethod
    def reset(self) -> None:
        """Reset all stored metrics."""
        pass
    
    @abstractmethod
    def update(self, *args, **kwargs) -> None:
        """Update metrics with new batch of predictions and labels."""
        pass
    
    @abstractmethod
    def compute(self) -> Dict[str, Any]:
        """Compute and return all metrics."""
        pass
    
    @abstractmethod
    def get_summary(self) -> str:
        """Return a formatted summary of metrics."""
        pass


class ClassificationMetrics(BaseMetrics):
    """Metrics calculator for classification tasks."""
    
    def __init__(
        self,
        num_classes: int,
        class_names: Optional[List[str]] = None,
        task_type: str = 'multiclass',
        average_methods: Optional[List[str]] = None
    ):
        self.num_classes = num_classes
        self.class_names = class_names or [f"Class_{i}" for i in range(num_classes)]
        self.task_type = task_type
        self.average_methods = average_methods or ['macro', 'micro', 'weighted']
        
        if len(self.class_names) != num_classes:
            raise ValueError(f"Number of class names ({len(self.class_names)}) "
                           f"must match num_classes ({num_classes})")
        
        super().__init__()
    
    def reset(self) -> None:
        """Reset all stored predictions and labels."""
        self.all_predictions = []
        self.all_labels = []
        self.all_probabilities = []
    
    def update(
        self,
        predictions: torch.Tensor,
        labels: torch.Tensor,
        probabilities: Optional[torch.Tensor] = None
    ) -> None:
        """
        Update metrics with new batch of data.
        
        Args:
            predictions: Tensor of predicted class indices
            labels: Tensor of true class indices
            probabilities: Optional tensor of class probabilities
        """
        self.all_predictions.extend(predictions.cpu().numpy())
        self.all_labels.extend(labels.cpu().numpy())
        
        if probabilities is not None:
            self.all_probabilities.extend(probabilities.cpu().numpy())
    
    def compute(self) -> Dict[str, Any]:
        """Compute comprehensive classification metrics."""
        if not self.all_predictions:
            return {}
        
        predictions = np.array(self.all_predictions)
        labels = np.array(self.all_labels)
        
        metrics = {}
        
        # Basic accuracy
        metrics['accuracy'] = accuracy_score(labels, predictions)
        
        # Per-class metrics
        precision_per_class, recall_per_class, f1_per_class, support = \
            precision_recall_fscore_support(
                labels, predictions, average=None, zero_division=0
            )
        
        metrics['precision_per_class'] = precision_per_class.tolist()
        metrics['recall_per_class'] = recall_per_class.tolist()
        metrics['f1_per_class'] = f1_per_class.tolist()
        metrics['support_per_class'] = support.tolist()
        
        # Average metrics
        for avg_method in self.average_methods:
            precision, recall, f1, _ = precision_recall_fscore_support(
                labels, predictions, average=avg_method, zero_division=0
            )
            metrics[f'precision_{avg_method}'] = precision
            metrics[f'recall_{avg_method}'] = recall
            metrics[f'f1_{avg_method}'] = f1
        
        # Confusion matrix and per-class accuracy
        cm = confusion_matrix(labels, predictions)
        metrics['confusion_matrix'] = cm.tolist()
        
        with np.errstate(divide='ignore', invalid='ignore'):
            per_class_accuracy = np.divide(cm.diagonal(), cm.sum(axis=1))
            per_class_accuracy = np.nan_to_num(per_class_accuracy, nan=0.0)
        
        metrics['per_class_accuracy'] = per_class_accuracy.tolist()
        
        # Additional sklearn classification report
        metrics['classification_report'] = classification_report(
            labels, predictions, 
            target_names=self.class_names, 
            output_dict=True,
            zero_division=0
        )
        
        return metrics
    
    def get_summary(self, max_classes_for_detailed: int = 10) -> str:
        """Return a formatted summary of classification metrics."""
        metrics = self.compute()
        
        if not metrics:
            return "No metrics computed yet. Call update() with data first."
        
        summary_parts = []
        summary_parts.append("=" * 60)
        summary_parts.append("CLASSIFICATION METRICS SUMMARY")
        summary_parts.append("=" * 60)
        summary_parts.append(f"Overall Accuracy: {metrics['accuracy']:.4f}")
        summary_parts.append(f"Macro F1-Score: {metrics.get('f1_macro', 0):.4f}")
        summary_parts.append(f"Weighted F1-Score: {metrics.get('f1_weighted', 0):.4f}")
        summary_parts.append("")
        
        # Detailed per-class metrics for reasonable number of classes
        if self.num_classes <= max_classes_for_detailed:
            summary_parts.append("Per-Class Metrics:")
            summary_parts.append("-" * 40)
            
            for i, class_name in enumerate(self.class_names):
                summary_parts.append(
                    f"{class_name:<15}: "
                    f"Prec={metrics['precision_per_class'][i]:.3f}, "
                    f"Rec={metrics['recall_per_class'][i]:.3f}, "
                    f"F1={metrics['f1_per_class'][i]:.3f}, "
                    f"Acc={metrics['per_class_accuracy'][i]:.3f}"
                )
        else:
            summary_parts.append(
                f"Too many classes ({self.num_classes}) for detailed display. "
                f"Use compute() method to get full metrics."
            )
        
        summary_parts.append("=" * 60)
        
        return "\n".join(summary_parts)
    
    def __len__(self) -> int:
        """Return number of samples collected."""
        return len(self.all_predictions)

class TimeSeriesMetrics(BaseMetrics):
    """Metrics calculator for Time Series Forecasting tasks (Regression-style)."""
    
    def __init__(self):
        super().__init__()
    
    def reset(self) -> None:
        """Reset all stored predictions and labels."""
        self.all_predictions = []
        self.all_labels = []
    
    def update(
        self,
        predictions: torch.Tensor,
        labels: torch.Tensor
    ) -> None:
        """
        Update metrics with new batch of data.
        
        Args:
            predictions: Tensor of predicted continuous values
            labels: Tensor of true continuous values
        """
        # Ensure Tensors are flattened and moved to CPU for NumPy conversion
        self.all_predictions.extend(predictions.detach().flatten().cpu().numpy())
        self.all_labels.extend(labels.detach().flatten().cpu().numpy())
    # Static method for calculating Mean Absolute Percentage Error (MAPE)
    @staticmethod
    def _mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculates MAPE, handling division by zero for y_true = 0."""
        # Note: This is a basic implementation. More robust versions exist.
        y_true, y_pred = np.array(y_true), np.array(y_pred)
        # Avoid division by zero by filtering out zero actual values or using a small epsilon
        nonzero_mask = y_true != 0
        
        if not np.any(nonzero_mask):
             return np.nan # Cannot compute MAPE if all true values are zero
        
        mape_value = np.mean(
            np.abs((y_true[nonzero_mask] - y_pred[nonzero_mask]) / y_true[nonzero_mask])
        ) * 100
        return mape_value

    def compute(self) -> Dict[str, Any]:
        """Compute comprehensive time series forecasting metrics."""
        if not self.all_predictions:
            return {}
        
        predictions = np.array(self.all_predictions)
        labels = np.array(self.all_labels)
        
        # Ensure predictions and labels have the same number of elements
        if len(predictions) != len(labels):
             raise ValueError("The number of predictions and labels must match.")
        
        metrics = {}
        
        # 1. Error-based metrics
        metrics['MAE'] = mean_absolute_error(labels, predictions)
        metrics['MSE'] = mean_squared_error(labels, predictions)
        metrics['RMSE'] = np.sqrt(metrics['MSE'])
        
        # 2. Percentage error (Scale-independent)
        metrics['MAPE'] = self._mape(labels, predictions)
        
        # 3. R-squared (Goodness of fit)
        metrics['R2'] = r2_score(labels, predictions)

        # 4. Bias Check (Mean Forecast Error)
        metrics['MFE'] = np.mean(labels - predictions) # Positive MFE means under-prediction
        
        return metrics
    
    def get_summary(self) -> str:
        """Return a formatted summary of time series metrics."""
        metrics = self.compute()
        
        if not metrics:
            return "No metrics computed yet. Call update() with data first."
        
        summary_parts = []
        summary_parts.append("=" * 60)
        summary_parts.append("TIME SERIES FORECASTING METRICS SUMMARY")
        summary_parts.append("=" * 60)
        
        summary_parts.append(f"Mean Absolute Error (MAE): {metrics['MAE']:.4f}")
        summary_parts.append(f"Root Mean Squared Error (RMSE): {metrics['RMSE']:.4f}")
        summary_parts.append(f"R-squared (R2): {metrics['R2']:.4f}")
        summary_parts.append(f"Mean Absolute Percentage Error (MAPE): {metrics['MAPE']:.4f}%")
        summary_parts.append(f"Mean Forecast Error (MFE / Bias): {metrics['MFE']:.4f}")
        
        summary_parts.append("=" * 60)
        
        return "\n".join(summary_parts)

    def __len__(self) -> int:
        """Return number of samples collected."""
        return len(self.all_predictions)

class MetricsFactory:
    """Factory class for creating appropriate metrics calculators."""
    
    _registry = {
        'classification': ClassificationMetrics,
        'image_classification': ClassificationMetrics,
        'timeseries': TimeSeriesMetrics,
        'regression': TimeSeriesMetrics
    }
    
    @classmethod
    def register_metrics(cls, task_type: str, metrics_class: type) -> None:
        """Register a new metrics class for a task type."""
        cls._registry[task_type.lower()] = metrics_class
    
    @staticmethod
    def create_metrics(task_type: str, **kwargs) -> BaseMetrics:
        """
        Create a metrics calculator for the specified task type.
        
        Args:
            task_type: Type of task ('classification', 'image_classification', etc.)
            **kwargs: Additional arguments passed to the metrics constructor
            
        Returns:
            Instance of appropriate metrics calculator
            
        Raises:
            ValueError: If task type is not supported
        """
        task_type = task_type.lower()
        
        if task_type not in MetricsFactory._registry:
            supported_types = list(MetricsFactory._registry.keys())
            raise ValueError(
                f"Unsupported task type: {task_type}. "
                f"Supported types: {supported_types}"
            )
        
        metrics_class = MetricsFactory._registry[task_type]
        return metrics_class(**kwargs)

