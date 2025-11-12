"""Typed inference helpers used by the MiraBest CLI.

The module exposes strongly typed wrappers around the PyTorch models trained in
train.py.  The functions intentionally lean on Python type hints to make it
easy for doc generators (such as pdoc) to surface argument and return types.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
from torchvision import models, transforms


class InferenceError(RuntimeError):
    """Raised when inference preparation or execution fails."""


class Architecture(str, Enum):
    """Supported neural network architectures."""

    RADIO_CNN = "radio_cnn"
    RESNET50 = "resnet50"


CLASSES: tuple[str, str] = ("FRI", "FRII")
DEFAULT_WEIGHT_SEARCH_DIRS: tuple[Path, ...] = (
    Path(__file__).resolve().parent / "weights",
    Path(__file__).resolve().parent.parent,
    Path(__file__).resolve().parent.parent.parent,
)


class RadioGalaxyCNN(nn.Module):
    """Baseline CNN architecture used for MiraBest classification."""

    def __init__(self, num_classes: int = len(CLASSES)) -> None:
        """Initialize the CNN with three convolutional blocks.

        Args:
            num_classes: Number of output classes for the classifier.
        """

        super().__init__()
        self.conv1 = nn.Conv2d(1, 16, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(16)
        self.pool1 = nn.MaxPool2d(2, 2)

        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(32)
        self.pool2 = nn.MaxPool2d(2, 2)

        self.conv3 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(64)
        self.pool3 = nn.MaxPool2d(2, 2)

        self.fc1 = nn.Linear(64 * 18 * 18, 128)
        self.fc2 = nn.Linear(128, num_classes)

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        """Forward pass for the baseline CNN.

        Args:
            inputs: Batched tensor of grayscale images.

        Returns:
            torch.Tensor: Raw logits for each class.
        """

        x = self.pool1(F.relu(self.bn1(self.conv1(inputs))))
        x = self.pool2(F.relu(self.bn2(self.conv2(x))))
        x = self.pool3(F.relu(self.bn3(self.conv3(x))))
        x = x.view(x.size(0), -1)
        x = F.relu(self.fc1(x))
        return self.fc2(x)


@dataclass(frozen=True)
class ModelPrediction:
    """Container for a single model's prediction results.

    Attributes:
        weights_path: Path to the weight file used for inference.
        architecture: Architecture inferred from the weight file.
        top_classes: Ranked class predictions and probabilities.

    Examples:
        >>> prediction = ModelPrediction(
        ...     weights_path=Path("model.pth"),
        ...     architecture=Architecture.RADIO_CNN,
        ...     top_classes=[("FRI", 0.87), ("FRII", 0.13)],
        ... )
        >>> prediction.summary_line()
        'model.pth [radio_cnn] -> FRI (0.870)'
    """

    weights_path: Path
    architecture: Architecture
    top_classes: list[tuple[str, float]]

    def summary_line(self) -> str:
        """Return a one-line summary highlighting the top prediction.

        Returns:
            str: Summary showing the best class and probability.

        Examples:
            >>> prediction = ModelPrediction(
            ...     weights_path=Path("weights.pth"),
            ...     architecture=Architecture.RESNET50,
            ...     top_classes=[("FRII", 0.65)],
            ... )
            >>> prediction.summary_line()
            'weights.pth [resnet50] -> FRII (0.650)'
        """

        label, score = self.top_classes[0]
        return f"{self.weights_path.name} [{self.architecture.value}] -> {label} ({score:.3f})"

    def detail_lines(self) -> list[str]:
        """Return formatted detail lines for secondary predictions.

        Returns:
            list[str]: Formatted lines for classes beyond the top prediction.

        Examples:
            >>> prediction = ModelPrediction(
            ...     weights_path=Path("weights.pth"),
            ...     architecture=Architecture.RESNET50,
            ...     top_classes=[("FRII", 0.65), ("FRI", 0.35)],
            ... )
            >>> prediction.detail_lines()
            ['  FRI: 0.350']
        """

        return [f"  {label}: {score:.3f}" for label, score in self.top_classes[1:]]


def discover_weight_files(search_dirs: Iterable[Path] | None = None) -> list[Path]:
    """Return a sorted list of discovered weight files.

    Args:
        search_dirs: Optional iterable of directories to scan for weights.

    Returns:
        list[Path]: Sorted list of discovered `.pth` files.

    Examples:
        >>> discover_weight_files(search_dirs=[Path("weights")])
        [Path('weights/best_simple_model.pth')]
    """

    directories = (
        tuple(search_dirs) if search_dirs is not None else DEFAULT_WEIGHT_SEARCH_DIRS
    )
    discovered: list[Path] = []
    seen: set[Path] = set()
    for directory in directories:
        if not directory.exists():
            continue
        for candidate in sorted(directory.glob("*.pth")):
            resolved = candidate.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            discovered.append(resolved)
    return discovered


def resolve_weight_paths(user_paths: list[Path] | None) -> list[Path]:
    """Resolve user-supplied or discovered weight paths.

    Args:
        user_paths: Optional list of weight files provided by the caller.

    Returns:
        list[Path]: Validated weight file paths.

    Raises:
        FileNotFoundError: If any supplied weight path is missing.
        InferenceError: If no weight files are discovered.

    Examples:
        >>> resolve_weight_paths([Path("best_simple_model.pth")])
        [Path('best_simple_model.pth')]
    """

    if user_paths:
        resolved = [path.expanduser().resolve() for path in user_paths]
    else:
        resolved = discover_weight_files()

    missing = [path for path in resolved if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "Weight file(s) not found: " + ", ".join(str(path) for path in missing)
        )

    if not resolved:
        raise InferenceError(
            "No weight files found. Provide --weights or place .pth files in the repository root or weights directory."
        )

    return resolved


def resolve_device(device_option: str) -> torch.device:
    """Resolve the torch device requested by the caller.

    Args:
        device_option: Desired device specifier such as auto, cpu, or cuda:0.

    Returns:
        torch.device: Device ready for inference.

    Raises:
        InferenceError: If the device specifier is invalid.

    Examples:
        >>> resolve_device("cpu")
        device(type='cpu')
        >>> resolve_device("auto") in {torch.device("cpu"), torch.device("cuda")}
        True
    """

    if device_option == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    try:
        return torch.device(device_option)
    except Exception as exc:  # pragma: no cover - pass through to caller
        raise InferenceError(f"Invalid device requested: {device_option}") from exc


def load_image(image_path: Path) -> Image.Image:
    """Load an image as grayscale for inference.

    Args:
        image_path: Path to the input image.

    Returns:
        Image.Image: Grayscale image ready for transformation.

    Examples:
        >>> image = load_image(Path("example.png"))
        >>> image.mode
        'L'
    """

    with Image.open(image_path) as handle:
        return handle.convert("L")


def _strip_module_prefix(
    state_dict: dict[str, torch.Tensor],
) -> dict[str, torch.Tensor]:
    """Remove leading module prefixes from state dictionary keys.

    Args:
        state_dict: Loaded state dictionary that may contain module prefixes.

    Returns:
        dict[str, torch.Tensor]: State dictionary without module prefixes.
    """

    if not any(key.startswith("module.") for key in state_dict):
        return state_dict
    return {key.replace("module.", "", 1): value for key, value in state_dict.items()}


def _load_state_dict(path: Path) -> dict[str, torch.Tensor]:
    """Load a state dictionary from disk.

    Args:
        path: Path to the serialized weight file.

    Returns:
        dict[str, torch.Tensor]: Model state dictionary.

    Raises:
        InferenceError: If the saved object is not a compatible state dictionary.
    """

    obj = torch.load(path, map_location="cpu")
    if (
        isinstance(obj, dict)
        and "state_dict" in obj
        and isinstance(obj["state_dict"], dict)
    ):
        raw_state = obj["state_dict"]
    elif isinstance(obj, dict):
        raw_state = obj
    else:
        raise InferenceError(f"Unsupported state dictionary format in {path}")

    return _strip_module_prefix({str(key): value for key, value in raw_state.items()})


def _infer_architecture(state_dict: dict[str, torch.Tensor]) -> Architecture:
    """Infer the architecture from state dictionary keys.

    Args:
        state_dict: State dictionary produced by `_load_state_dict`.

    Returns:
        Architecture: Detected architecture for the state dictionary.

    Raises:
        InferenceError: If the architecture cannot be determined.
    """

    if any(key.startswith("fc2") for key in state_dict):
        return Architecture.RADIO_CNN
    if "fc.weight" in state_dict:
        return Architecture.RESNET50
    raise InferenceError("Could not infer architecture from state dictionary")


def _build_model(architecture: Architecture) -> nn.Module:
    """Instantiate a model that matches the inferred architecture.

    Args:
        architecture: Architecture enumerator returned by `_infer_architecture`.

    Returns:
        nn.Module: Initialized model that matches the architecture.

    Raises:
        InferenceError: If the architecture is unsupported.
    """

    if architecture is Architecture.RADIO_CNN:
        return RadioGalaxyCNN(num_classes=len(CLASSES))
    if architecture is Architecture.RESNET50:
        model = models.resnet50(weights=None)
        model.conv1 = nn.Conv2d(1, 64, kernel_size=7, stride=2, padding=3, bias=False)
        model.fc = nn.Linear(model.fc.in_features, len(CLASSES))
        return model
    raise InferenceError(f"Unsupported architecture: {architecture}")


def _transform_for(architecture: Architecture) -> transforms.Compose:
    """Return an image transform pipeline for the requested architecture.

    Args:
        architecture: Architecture enumerator returned by `_infer_architecture`.

    Returns:
        transforms.Compose: Transform pipeline appropriate for the architecture.

    Raises:
        InferenceError: If the architecture is unsupported.
    """

    if architecture is Architecture.RADIO_CNN:
        return transforms.Compose(
            [transforms.ToTensor(), transforms.Normalize(mean=[0.0031], std=[0.0352])]
        )
    if architecture is Architecture.RESNET50:
        return transforms.Compose(
            [
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.0031], std=[0.0352]),
            ]
        )
    raise InferenceError(f"Unsupported architecture: {architecture}")


def predict_with_weights(
    image: Image.Image,
    weights_path: Path,
    device: torch.device,
    top_k: int,
) -> ModelPrediction:
    """Run inference for a single weight file.

    Args:
        image: Grayscale image ready for transformation.
        weights_path: Path to the model weights.
        device: Device where inference will run.
        top_k: Number of top classes to include in results.

    Returns:
        ModelPrediction: Structured prediction result for the weight file.

    Raises:
        InferenceError: If transforms or model preparation fail.

    Examples:
        >>> image = load_image(Path("example.png"))
        >>> device = resolve_device("cpu")
        >>> prediction = predict_with_weights(image, Path("best_simple_model.pth"), device, 1)
        >>> prediction.architecture
        <Architecture.RADIO_CNN: 'radio_cnn'>
    """

    state_dict = _load_state_dict(weights_path)
    architecture = _infer_architecture(state_dict)
    model = _build_model(architecture)
    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()

    transform = _transform_for(architecture)
    transformed = transform(image)
    if not isinstance(transformed, torch.Tensor):
        raise InferenceError("Expected transform to return a torch.Tensor")

    tensor = transformed.unsqueeze(0).to(device)
    with torch.no_grad():
        logits = model(tensor)
        probabilities = torch.softmax(logits, dim=1)[0]

    adjusted_top_k = max(1, min(top_k, len(CLASSES)))
    values, indices = torch.topk(probabilities, adjusted_top_k)
    results = [(CLASSES[int(idx)], float(val)) for idx, val in zip(indices, values)]
    return ModelPrediction(
        weights_path=weights_path, architecture=architecture, top_classes=results
    )


def run_predictions(
    image_path: Path,
    weight_paths: list[Path] | None = None,
    device_option: str = "auto",
    top_k: int = 1,
) -> list[ModelPrediction]:
    """Run inference for an image against one or more weight files.

    Args:
        image_path: Path to the input image.
        weight_paths: Optional explicit list of weight files to evaluate.
        device_option: Preferred device specifier such as auto, cpu, or cuda.
        top_k: Number of top classes to include in each result.

    Returns:
        list[ModelPrediction]: Prediction results for each weight file.

    Raises:
        FileNotFoundError: If any requested weight path is missing.
        InferenceError: If weight discovery or inference preparation fails.

    Examples:
        >>> run_predictions(Path("example.png"), [Path("best_simple_model.pth")])
        [ModelPrediction(weights_path=Path('best_simple_model.pth'), architecture=<Architecture.RADIO_CNN: 'radio_cnn'>, top_classes=[('FRI', 0.87)])]
    """

    resolved_weights = resolve_weight_paths(weight_paths)
    image = load_image(image_path)
    device = resolve_device(device_option)

    return [
        predict_with_weights(image, weights_path, device, top_k)
        for weights_path in resolved_weights
    ]
