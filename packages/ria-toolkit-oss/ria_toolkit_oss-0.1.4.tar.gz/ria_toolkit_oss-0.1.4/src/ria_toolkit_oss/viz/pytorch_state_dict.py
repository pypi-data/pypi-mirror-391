import numpy as np
import plotly.graph_objects as go
from plotly.graph_objects import Figure


def create_styled_error_figure(title: str, message: str, suggestion: str = None) -> go.Figure:
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


def model_summary_plot(state_dict: dict) -> Figure:
    """Generate a summary plot of the PyTorch model state dict."""
    if not state_dict:
        return create_styled_error_figure(
            "Empty State Dict",
            "No parameters found in state dict",
            "Ensure the model state dictionary contains weight parameters",
        )
    # Count parameters by layer type
    layer_info = []
    for key, tensor in state_dict.items():
        if "weight" in key:
            try:
                layer_name = key.replace(".weight", "")
                param_count = (
                    tensor.numel()
                    if hasattr(tensor, "numel")
                    else len(tensor.flatten()) if hasattr(tensor, "flatten") else 0
                )
                shape = (
                    list(tensor.shape)
                    if hasattr(tensor, "shape")
                    else [len(tensor)] if hasattr(tensor, "__len__") else []
                )
                layer_info.append({"layer": layer_name, "parameters": param_count, "shape": shape})
            except Exception as e:
                print(f"Warning: Could not process layer {key}: {e}")
                continue
    if not layer_info:
        return create_styled_error_figure(
            "No Weight Layers Found",
            "No weight layers found in state dict",
            "Ensure the state dictionary contains layers with '.weight' parameters",
        )
    # Create bar chart of parameter counts
    fig = go.Figure(
        data=[
            go.Bar(
                x=[info["layer"] for info in layer_info],
                y=[info["parameters"] for info in layer_info],
                text=[f"Shape: {info['shape']}" for info in layer_info],
                textposition="auto",
            )
        ]
    )
    fig.update_layout(
        title="Model Layer Parameter Counts",
        xaxis_title="Layer",
        yaxis_title="Number of Parameters",
        template="plotly_dark",
    )
    return fig


def layer_weights_plot(state_dict: dict, layer_name: str = None) -> Figure:
    """Visualize weights for a specific layer."""
    if not state_dict:
        return create_styled_error_figure(
            "Empty State Dict", "No data in state dict", "Ensure the model state dictionary contains data"
        )
    if layer_name is None:
        # Get first weight tensor
        weight_keys = [k for k in state_dict.keys() if "weight" in k]
        if not weight_keys:
            return create_styled_error_figure(
                "No Weight Tensors Found",
                "No weight tensors found in state dict",
                "Ensure the state dictionary contains layers with '.weight' parameters",
            )
        layer_name = weight_keys[0]
    try:
        weights = state_dict[layer_name]
        # Convert to numpy if it's a torch tensor
        if hasattr(weights, "numpy"):
            weights_np = weights.detach().numpy() if hasattr(weights, "detach") else weights.numpy()
        elif hasattr(weights, "cpu"):
            weights_np = weights.cpu().detach().numpy()
        else:
            weights_np = np.array(weights)
        # For 2D weights, create heatmap
        if len(weights_np.shape) == 2:
            fig = go.Figure(data=go.Heatmap(z=weights_np, colorscale="RdBu", zmid=0))
            fig.update_layout(title=f"Weights Heatmap: {layer_name}", template="plotly_dark")
        else:
            # For other shapes, flatten and show histogram
            flat_weights = weights_np.flatten()
            fig = go.Figure(data=[go.Histogram(x=flat_weights, nbinsx=50)])
            fig.update_layout(title=f"Weight Distribution: {layer_name}", template="plotly_dark")

        return fig

    except Exception as e:
        return create_styled_error_figure(
            "Layer Processing Error",
            f"Error processing layer {layer_name}: {str(e)}",
            "Check that the layer name exists and contains valid tensor data",
        )


def weight_distribution_plot(state_dict: dict) -> Figure:
    """Show distribution of weights across all layers."""
    if not state_dict:
        return create_styled_error_figure(
            "Empty State Dict", "No data in state dict", "Ensure the model state dictionary contains data"
        )

    all_weights = []
    layer_names = []

    for key, tensor in state_dict.items():
        if "weight" in key:
            try:
                # Convert to numpy if it's a torch tensor
                if hasattr(tensor, "numpy"):
                    weights_np = tensor.detach().numpy() if hasattr(tensor, "detach") else tensor.numpy()
                elif hasattr(tensor, "cpu"):
                    weights_np = tensor.cpu().detach().numpy()
                else:
                    weights_np = np.array(tensor)
                flat_weights = weights_np.flatten()
                all_weights.extend(flat_weights)
                layer_names.extend([key] * len(flat_weights))
            except Exception as e:
                print(f"Warning: Could not process weights for layer {key}: {e}")
                continue

    if not all_weights:
        return create_styled_error_figure(
            "No Weight Data Found",
            "No weight data found in state dict",
            "Ensure the state dictionary contains layers with '.weight' parameters",
        )

    fig = go.Figure(data=[go.Histogram(x=all_weights, nbinsx=100, name="All Weights")])

    fig.update_layout(
        title="Overall Weight Distribution",
        xaxis_title="Weight Value",
        yaxis_title="Frequency",
        template="plotly_dark",
    )
    return fig
