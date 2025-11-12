"""Minimal Typer application that wraps the typed inference helpers.

The CLI is intentionally slim so tutorial readers can focus on how annotated
functions and docstrings translate into generated documentation.
"""

from __future__ import annotations

from pathlib import Path

import typer

from mirabest_identifier.inference import (
    CLASSES,
    InferenceError,
    ModelPrediction,
    discover_weight_files,
    run_predictions,
)

app = typer.Typer(help="Run MiraBest morphology classifiers from the command line.")


def _print_predictions(predictions: list[ModelPrediction]) -> None:
    """Emit formatted prediction output for the CLI.

    Args:
        predictions: Prediction objects produced by run_predictions.

    Examples:
        >>> from mirabest_identifier.inference import Architecture
        >>> _print_predictions([
        ...     ModelPrediction(
        ...         weights_path=Path("model.pth"),
        ...         architecture=Architecture.RADIO_CNN,
        ...         top_classes=[("FRI", 0.9)],
        ...     )
        ... ])
        model.pth [radio_cnn] -> FRI (0.900)
    """

    for prediction in predictions:
        typer.echo(prediction.summary_line())
        for line in prediction.detail_lines():
            typer.echo(line)


@app.command()
def predict(
    image_path: Path,
    weights: list[Path] | None = None,
    device: str = "auto",
    top_k: int = 1,
) -> None:
    """Run inference against one or more trained MiraBest classifiers.

    Args:
        image_path: Path to the radio galaxy image.
        weights: Optional list of weight files to evaluate. Defaults to None,
            which triggers automatic discovery.
        device: Preferred device specifier passed to torch.device. Choices are
            "auto", "cpu", "cuda", "cuda:0", "mps". Defaults to "auto".
        top_k: Positive number of classes to report for each model. Defaults to 1.

    Raises:
        typer.BadParameter: If weight resolution or inference fails.

    Examples:
        Run against the default weights discovered in the project:

       $ mirabest-identifier predict ./example.png

        Supply an explicit weight file and show top-2 predictions:

       $ mirabest-identifier predict example.png --weights best_simple_model.pth --weights pretrained_radio_galaxy_cnn.pth --top-k 2
    """

    try:
        predictions = run_predictions(image_path, weights, device, top_k)
    except (FileNotFoundError, InferenceError) as exc:
        raise typer.BadParameter(str(exc)) from exc

    _print_predictions(predictions)


@app.command()
def list_weights() -> None:
    """List discovered model weight files.

    Raises:
        typer.Exit: If no weight files are found.

    Examples:
        $ mirabest-identifier list-weights
        /abs/path/to/best_simple_model.pth
        /abs/path/to/pretrained_radio_galaxy_cnn.pth
    """

    discovered = discover_weight_files()
    if not discovered:
        typer.echo(
            "No .pth files found. Place your trained weights in src/mirabest_identifier/weights or the project root."
        )
        raise typer.Exit(code=1)

    for path in discovered:
        typer.echo(str(path))


@app.command()
def gui(
    weights: list[Path] | None = None,
    device: str = "auto",
    top_k: int = 2,
    share: bool = False,
    server_name: str | None = None,
    server_port: int | None = None,
) -> None:
    """Launch the Gradio interface for interactive predictions.

    Args:
        weights: Optional custom list of weight files to expose.
        device: Preferred device specifier passed to torch.device.
        top_k: Default number of classes to display in the GUI.
        share: Whether to request a temporary public Gradio share link.
        server_name: Optional hostname for the local Gradio server.
        server_port: Optional port for the local Gradio server.

    Raises:
        typer.BadParameter: If the interface cannot be constructed.

    Examples:
        Launch the GUI with default settings:

        $ mirabest-identifier gui

        Launch the GUI with a specific weight file and share link:

        $ mirabest-identifier gui --weights best_simple_model.pth --share
    """

    from mirabest_identifier.gradio_app import launch_gradio

    adjusted_top_k = max(1, min(top_k, len(CLASSES)))
    weight_list = weights

    try:
        launch_gradio(
            weight_paths=weight_list,
            device_option=device,
            default_top_k=adjusted_top_k,
            share=share,
            server_name=server_name,
            server_port=server_port,
        )
    except (FileNotFoundError, InferenceError) as exc:
        raise typer.BadParameter(str(exc)) from exc


def main() -> None:
    """Entrypoint used by the console script."""

    app()
