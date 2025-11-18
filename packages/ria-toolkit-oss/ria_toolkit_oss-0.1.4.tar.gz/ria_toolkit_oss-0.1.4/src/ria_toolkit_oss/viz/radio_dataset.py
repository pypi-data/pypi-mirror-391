"""
Simple, clean visualization utilities for RadioDataset analysis.
"""

import random
from typing import Optional

import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objects import Figure
from plotly.subplots import make_subplots


def create_styled_error_figure(title: str, message: str, suggestion: str = None) -> Figure:
    """Create a professional error figure with Qoherent dark theme styling."""
    fig = go.Figure()

    # Create a clean, centered text display using Plotly's text formatting
    main_text = f"<b style='color:#f56565;font-size:18px'>⚠️ {title}</b><br><br>"
    main_text += f"<span style='color:#e2e8f0;font-size:14px'>{message}</span>"

    if suggestion:
        main_text += "<br><br><span style='color:#63b3ed;font-size:13px'>💡 <b>Suggestion:</b></span><br>"
        main_text += f"<span style='color:#cbd5e0;font-size:12px'>{suggestion}</span>"

    # Add the main text annotation
    fig.add_annotation(
        text=main_text,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        xanchor="center",
        yanchor="middle",
        showarrow=False,
        align="center",
        borderwidth=2,
        bordercolor="#4a5568",
        bgcolor="#2d3748",
        font=dict(family="Arial, sans-serif", size=14, color="#e2e8f0"),
    )

    # Update layout with dark theme
    fig.update_layout(
        title="",
        height=400,
        template="plotly_dark",
        margin=dict(l=40, r=40, t=40, b=40),
        plot_bgcolor="#1a202c",
        paper_bgcolor="#1a202c",
        font=dict(color="#e2e8f0"),
    )

    # Remove axes and grid
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)

    return fig


def _check_dataset_compatibility(dataset, plot_type: str) -> tuple[bool, str]:
    """Check if dataset is compatible with a specific plot type.
    Returns (is_compatible, error_message)
    """
    try:
        metadata = dataset.metadata

        if len(metadata) == 0:
            return False, "Dataset is empty"

        if plot_type == "class_distribution":
            # Check if we have any categorical columns
            categorical_cols = [col for col in metadata.columns if metadata[col].dtype == "object"]
            alternatives = ["class", "label", "modulation", "impairment", "use_case", "category", "labels"]

            has_class_col = any(alt in metadata.columns for alt in alternatives)
            has_categorical = len(categorical_cols) > 0

            if not has_class_col and not has_categorical:
                return False, "No categorical columns found for class distribution"

        elif plot_type == "sample_spectrogram":
            # Check if we can generate a valid spectrogram
            if len(metadata) < 1:
                return False, "No samples available for spectrogram"

            # Check if we can access sample data (basic test)
            try:
                sample_data = dataset[0] if hasattr(dataset, "__getitem__") else None
                if sample_data is None or len(sample_data) < 32:
                    return False, "Insufficient sample data for spectrogram (need at least 32 points)"
            except Exception:
                # If we can't access data, we'll rely on synthetic data generation
                pass

        return True, ""

    except Exception as e:
        return False, f"Dataset compatibility check failed: {str(e)}"


def class_distribution_plot(dataset, class_key: str = "modulation") -> Figure:
    """Generate a bar plot showing the distribution of examples across classes."""
    try:
        # Check dataset compatibility first
        is_compatible, error_msg = _check_dataset_compatibility(dataset, "class_distribution")
        if not is_compatible:
            return create_styled_error_figure(
                "Dataset Not Compatible",
                "This dataset doesn't have categorical labels needed for class distribution analysis.",
                "Try using the Dataset Overview widget to explore the available data columns.",
            )

        metadata = dataset.metadata

        # Find the class column
        if class_key not in metadata.columns:
            # Try common alternatives
            alternatives = ["class", "label", "modulation", "impairment", "use_case", "category", "labels"]
            for alt in alternatives:
                if alt in metadata.columns:
                    class_key = alt
                    break
            else:
                # Use first categorical column
                for col in metadata.columns:
                    if metadata[col].dtype == "object" or metadata[col].nunique() < 50:
                        class_key = col
                        break

        if class_key not in metadata.columns:
            return create_styled_error_figure(
                "No Class Labels Found",
                "This dataset contains numerical data without categorical labels.",
                (
                    "Try using the Dataset Overview widget for data analysis, "
                    "or check if your dataset has hidden categorical columns."
                ),
            )

        # Count examples per class (limit to top 20 for performance)
        class_counts = metadata[class_key].value_counts()
        if len(class_counts) > 20:
            class_counts = class_counts.head(20)

        class_counts = class_counts.sort_index()

        # Create simple bar plot
        fig = px.bar(x=class_counts.index, y=class_counts.values, title=f"Class Distribution: {class_key.title()}")

        fig.update_traces(texttemplate="%{y}", textposition="outside")
        fig.update_layout(
            xaxis_title=class_key.title(),
            yaxis_title="Number of Examples",
            showlegend=False,
            height=400,
            template="plotly_dark",
        )

        return fig

    except Exception as e:
        return create_styled_error_figure(
            "Class Distribution Error",
            "An error occurred while generating the class distribution plot.",
            f"Technical details: {str(e)}",
        )


def dataset_overview_plot(dataset) -> Figure:
    """Generate an overview plot with key dataset statistics."""
    try:
        metadata = dataset.metadata
        total_examples = len(metadata)

        # Create subplot with multiple charts

        # Determine subplot titles based on data type
        categorical_cols = [col for col in metadata.columns if metadata[col].dtype == "object"]
        numeric_cols = [col for col in metadata.columns if metadata[col].dtype in ["int64", "float64"]]

        dist_title = "Value Distribution" if categorical_cols else "Data Distribution"

        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=("Dataset Size", "Data Types", dist_title, "Statistics Summary"),
            specs=[
                [{"type": "indicator"}, {"type": "bar"}],
                [{"type": "histogram" if not categorical_cols else "bar"}, {"type": "table"}],
            ],
        )

        # Top left: Dataset size indicator
        fig.add_trace(
            go.Indicator(
                mode="number", value=total_examples, title={"text": "Total Examples"}, number={"font": {"size": 40}}
            ),
            row=1,
            col=1,
        )

        # Top right: Data types distribution
        dtype_counts = metadata.dtypes.value_counts()
        fig.add_trace(
            go.Bar(
                x=[str(dt) for dt in dtype_counts.index], y=dtype_counts.values, name="Data Types", showlegend=False
            ),
            row=1,
            col=2,
        )

        # Bottom left: Show distribution of numeric columns or categorical if available
        categorical_cols = [col for col in metadata.columns if metadata[col].dtype == "object"]
        numeric_cols = [col for col in metadata.columns if metadata[col].dtype in ["int64", "float64"]]

        if categorical_cols:
            col = categorical_cols[0]  # Show first categorical column
            value_counts = metadata[col].value_counts().head(10)
            fig.add_trace(
                go.Bar(x=value_counts.index, y=value_counts.values, name=f"{col} Distribution", showlegend=False),
                row=2,
                col=1,
            )
        elif numeric_cols:
            # Show histogram of first numeric column
            col = numeric_cols[0]
            fig.add_trace(
                go.Histogram(x=metadata[col], name=f"{col} Distribution", showlegend=False, nbinsx=20), row=2, col=1
            )

        # Bottom right: Basic statistics table
        stats_data = []
        display_cols = numeric_cols[:5] if len(numeric_cols) > 0 else metadata.columns[:5]

        for col in display_cols:
            if metadata[col].dtype in ["int64", "float64"]:
                stats_data.append(
                    [
                        col[:15] + "..." if len(col) > 15 else col,  # Truncate long column names
                        f"{metadata[col].mean():.3f}",
                        f"{metadata[col].std():.3f}",
                        f"{metadata[col].min():.3f}",
                        f"{metadata[col].max():.3f}",
                    ]
                )
            else:
                unique_count = metadata[col].nunique()
                stats_data.append(
                    [col[:15] + "..." if len(col) > 15 else col, "N/A", "N/A", f"{unique_count} unique", "N/A"]
                )

        if stats_data:
            fig.add_trace(
                go.Table(
                    header=dict(
                        values=["Column", "Mean", "Std", "Min/Unique", "Max"],
                        fill_color="rgba(30, 30, 30, 0.8)",
                        align="center",
                        font=dict(color="white", size=12),
                    ),
                    cells=dict(
                        values=list(zip(*stats_data)),
                        fill_color="rgba(50, 50, 50, 0.6)",
                        align="center",
                        font=dict(color="white", size=11),
                    ),
                ),
                row=2,
                col=2,
            )

        # Create informative title
        total_cols = len(metadata.columns)
        title = f"Dataset Overview - {total_examples} samples, {total_cols} columns"
        if total_cols > 5:
            title += " (showing first 5)"

        fig.update_layout(title=title, height=600, showlegend=False, template="plotly_dark")

        return fig

    except Exception as e:
        return create_styled_error_figure(
            "Dataset Overview Error",
            "An error occurred while generating the dataset overview.",
            f"Technical details: {str(e)}",
        )


def _find_class_column(metadata, class_key: str) -> str:
    """Find the appropriate class column in metadata."""
    if class_key in metadata.columns:
        return class_key

    alternatives = ["class", "label", "modulation", "impairment", "use_case"]
    for alt in alternatives:
        if alt in metadata.columns:
            return alt
    return class_key


def _get_sample_data(dataset, sample_idx: int):
    """Get sample data from dataset, with synthetic fallback."""
    try:
        return dataset[sample_idx]
    except Exception:
        # Generate synthetic signal based on class
        n_samples = 1024
        t = np.linspace(0, 1, n_samples)
        freq = 0.1 + 0.05 * sample_idx % 5  # Vary frequency by sample
        sample_data = np.exp(1j * 2 * np.pi * freq * t)
        # Add some noise
        sample_data += 0.1 * (np.random.randn(n_samples) + 1j * np.random.randn(n_samples))
        return sample_data


def _calculate_spectrogram_params(n_samples: int) -> tuple[int, int, int, int]:
    """Calculate spectrogram parameters based on sample length."""
    if n_samples < 32:
        raise ValueError(f"Insufficient data: need at least 32 samples, got {n_samples}")

    nperseg = min(256, max(32, n_samples // 4))
    hop_length = max(1, nperseg // 2)

    # Adjust for very short signals
    if n_samples < nperseg:
        nperseg = n_samples
        hop_length = 1

    n_frames = max(1, (n_samples - nperseg) // hop_length + 1)
    freq_bins = max(1, nperseg // 2)

    return nperseg, hop_length, n_frames, freq_bins


def _compute_spectrogram(sample_data, nperseg: int, hop_length: int, n_frames: int, freq_bins: int):
    """Compute spectrogram using FFT."""
    n_samples = len(sample_data)
    Sxx = np.zeros((freq_bins, n_frames))

    for i in range(n_frames):
        start_idx = i * hop_length
        end_idx = min(start_idx + nperseg, n_samples)

        if end_idx > start_idx:
            windowed = sample_data[start_idx:end_idx]

            # Pad if necessary to maintain nperseg size
            if len(windowed) < nperseg:
                windowed = np.pad(windowed, (0, nperseg - len(windowed)), mode="constant")

            fft_result = np.fft.fft(windowed)
            Sxx[:, i] = np.abs(fft_result[:freq_bins]) ** 2

    return Sxx


def _create_spectrogram_figure(
    Sxx,
    n_frames: int,
    hop_length: int,
    n_samples: int,
    freq_bins: int,
    sample_idx: int,
    class_key: str,
    sample_metadata,
) -> Figure:
    """Create the plotly figure for the spectrogram."""
    # Convert to dB
    Sxx_db = 10 * np.log10(Sxx + 1e-10)

    # Create time and frequency vectors
    t = np.arange(n_frames) * hop_length / max(1, n_samples)
    f = np.linspace(0, 0.5, freq_bins)

    # Create plot
    fig = go.Figure(data=go.Heatmap(z=Sxx_db, x=t, y=f, colorscale="viridis", colorbar=dict(title="Power (dB)")))

    # Add title with metadata
    title = f"Sample Spectrogram (Index: {sample_idx})"
    if class_key in sample_metadata:
        title += f" - {class_key}: {sample_metadata[class_key]}"

    fig.update_layout(title=title, xaxis_title="Time", yaxis_title="Frequency", height=400, template="plotly_dark")
    return fig


def sample_spectrogram_plot(dataset, class_key: str = "modulation", sample_idx: Optional[int] = None) -> Figure:
    """Generate a spectrogram plot from a sample in the dataset."""
    try:
        # Check dataset compatibility first
        is_compatible, error_msg = _check_dataset_compatibility(dataset, "sample_spectrogram")
        if not is_compatible:
            return create_styled_error_figure(
                "Spectrogram Not Available",
                "This dataset doesn't have sufficient signal data for spectrogram visualization.",
                "Ensure your dataset contains complex-valued signal samples with at least 32 data points per sample.",
            )

        metadata = dataset.metadata
        if len(metadata) == 0:
            raise ValueError("Dataset is empty")

        # Find class column and select sample
        class_key = _find_class_column(metadata, class_key)
        if sample_idx is None:
            sample_idx = random.randint(0, len(metadata) - 1)
        sample_metadata = metadata.iloc[sample_idx]

        # Get sample data and ensure it's complex
        sample_data = _get_sample_data(dataset, sample_idx)
        if not np.iscomplexobj(sample_data):
            sample_data = sample_data.astype(complex)

        # Calculate spectrogram parameters and compute spectrogram
        n_samples = len(sample_data)
        nperseg, hop_length, n_frames, freq_bins = _calculate_spectrogram_params(n_samples)
        Sxx = _compute_spectrogram(sample_data, nperseg, hop_length, n_frames, freq_bins)

        # Create and return the figure
        return _create_spectrogram_figure(
            Sxx, n_frames, hop_length, n_samples, freq_bins, sample_idx, class_key, sample_metadata
        )

    except Exception as e:
        return create_styled_error_figure(
            "Spectrogram Error",
            "An error occurred while generating the spectrogram plot.",
            f"Technical details: {str(e)}",
        )
