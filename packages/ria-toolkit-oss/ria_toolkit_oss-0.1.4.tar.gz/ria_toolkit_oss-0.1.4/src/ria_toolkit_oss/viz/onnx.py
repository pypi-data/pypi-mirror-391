"""
ONNX model visualization utilities.

This module provides visualization functions for ONNX models following the same pattern
as other ria-toolkit-oss visualization modules.
"""

from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

try:
    import onnx
    import onnx.helper
    import onnx.numpy_helper

    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False


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


def graph_structure(file_path: Path) -> go.Figure:
    """
    Visualize the ONNX model graph structure showing nodes and connections.
    Matches layout ID: graph_structure
    """
    if not ONNX_AVAILABLE:
        return create_styled_error_figure(
            "ONNX Not Available", "ONNX library is required for model analysis.", "Install with: pip install onnx"
        )

    try:
        # Load ONNX model
        model = onnx.load(str(file_path))
        graph = model.graph
        nodes = graph.node

        if len(nodes) == 0:
            return create_styled_error_figure(
                "Empty Model", "This ONNX model contains no operators.", "Please check if the model file is valid."
            )

        # Create network diagram data
        node_info = []
        for i, node in enumerate(nodes):
            node_info.append(
                {
                    "id": i,
                    "name": node.name or f"{node.op_type}_{i}",
                    "op_type": node.op_type,
                    "inputs": len(node.input),
                    "outputs": len(node.output),
                }
            )

        # Create visualization
        fig = go.Figure()

        # Simple linear layout for now
        x_positions = list(range(len(node_info)))
        y_positions = [0] * len(node_info)

        # Add nodes as scatter points
        fig.add_trace(
            go.Scatter(
                x=x_positions,
                y=y_positions,
                mode="markers+text",
                marker=dict(
                    size=[min(max(info["inputs"] + info["outputs"] + 15, 20), 50) for info in node_info],
                    color=px.colors.qualitative.Set3[: len(node_info)],
                    opacity=0.8,
                    line=dict(width=2, color="white"),
                ),
                text=[f"{info['op_type']}" for info in node_info],
                textposition="middle center",
                textfont=dict(size=10, color="white"),
                hovertemplate="<b>%{text}</b><br>"
                + "Name: %{customdata[0]}<br>"
                + "Inputs: %{customdata[1]}<br>"
                + "Outputs: %{customdata[2]}<br>"
                + "<extra></extra>",
                customdata=[[info["name"], info["inputs"], info["outputs"]] for info in node_info],
                name="Operators",
            )
        )

        # Add connecting lines
        for i in range(len(node_info) - 1):
            fig.add_trace(
                go.Scatter(
                    x=[x_positions[i], x_positions[i + 1]],
                    y=[y_positions[i], y_positions[i + 1]],
                    mode="lines",
                    line=dict(color="gray", width=1, dash="dot"),
                    showlegend=False,
                    hoverinfo="skip",
                )
            )

        fig.update_layout(
            title={
                "text": (
                    "ONNX Graph Structure<br>"
                    f"<span style='font-size:14px; color:#a0a0a0;'>{len(nodes)} Operators</span>"
                ),
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 22},
            },
            xaxis_title="Execution Order",
            yaxis_title="",
            showlegend=False,
            height=500,
            template="plotly_dark",
            yaxis=dict(showticklabels=False, showgrid=False),
            xaxis=dict(showgrid=False),
            margin=dict(l=50, r=50, t=80, b=50),
        )

        return fig

    except Exception as e:
        return create_styled_error_figure(
            "Graph Analysis Error", "Could not analyze ONNX model structure.", f"Error: {str(e)}"
        )


def operator_analysis(file_path: Path) -> go.Figure:
    """
    Analyze the distribution and types of operators in the ONNX model.
    Matches layout ID: operator_analysis
    """
    if not ONNX_AVAILABLE:
        return create_styled_error_figure(
            "ONNX Not Available", "ONNX library is required for operator analysis.", "Install with: pip install onnx"
        )

    try:
        model = onnx.load(str(file_path))
        graph = model.graph

        # Count operators
        op_counts = {}
        for node in graph.node:
            op_type = node.op_type
            op_counts[op_type] = op_counts.get(op_type, 0) + 1

        if not op_counts:
            return create_styled_error_figure(
                "No Operators",
                "This ONNX model contains no operators to analyze.",
                "Please verify the model file is valid.",
            )

        # Sort by frequency
        sorted_ops = sorted(op_counts.items(), key=lambda x: x[1], reverse=True)

        # Create pie chart and bar chart
        fig = make_subplots(
            rows=2,
            cols=1,
            subplot_titles=("Operator Distribution", "Operator Frequency"),
            specs=[[{"type": "pie"}], [{"type": "bar"}]],
        )

        # Pie chart for operator distribution
        op_names, op_values = zip(*sorted_ops) if sorted_ops else ([], [])

        fig.add_trace(
            go.Pie(
                labels=list(op_names),
                values=list(op_values),
                textinfo="label+percent",
                textposition="auto",
                showlegend=False,
            ),
            row=1,
            col=1,
        )

        # Bar chart for frequency
        fig.add_trace(
            go.Bar(
                x=list(op_names),
                y=list(op_values),
                marker_color=px.colors.qualitative.Set3[: len(op_names)],
                showlegend=False,
            ),
            row=2,
            col=1,
        )

        fig.update_layout(
            title={
                "text": (
                    "ONNX Operator Analysis<br>"
                    f"<span style='font-size:14px; color:#a0a0a0;'>{len(op_counts)} Unique Types</span>"
                ),
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 22},
            },
            height=700,
            template="plotly_dark",
        )

        return fig

    except Exception as e:
        return create_styled_error_figure(
            "Operator Analysis Error", "Could not analyze ONNX operators.", f"Error: {str(e)}"
        )


def model_metadata(file_path: Path) -> go.Figure:
    """
    Display comprehensive metadata about the ONNX model.
    Matches layout ID: model_metadata
    """
    if not ONNX_AVAILABLE:
        return create_styled_error_figure(
            "ONNX Not Available", "ONNX library is required for metadata analysis.", "Install with: pip install onnx"
        )

    try:
        model = onnx.load(str(file_path))
        graph = model.graph

        # Calculate basic statistics
        total_nodes = len(graph.node)
        total_inputs = len(graph.input)
        total_outputs = len(graph.output)
        total_initializers = len(graph.initializer)

        # Calculate parameter count
        total_params = 0
        for initializer in graph.initializer:
            try:
                tensor = onnx.numpy_helper.to_array(initializer)
                total_params += tensor.size
            except Exception:
                pass  # Skip if tensor can't be loaded

        # Get model file size
        file_size_mb = file_path.stat().st_size / (1024 * 1024)

        # Create metadata display
        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=("Model Size", "Architecture", "Inputs/Outputs", "Parameters"),
            specs=[[{"type": "indicator"}, {"type": "bar"}], [{"type": "table"}, {"type": "indicator"}]],
        )

        # Model size indicator
        fig.add_trace(
            go.Indicator(
                mode="number+gauge",
                value=file_size_mb,
                title={"text": "Model Size (MB)"},
                number={"suffix": " MB", "valueformat": ".2f"},
                gauge={
                    "axis": {"range": [0, max(100, file_size_mb * 1.5)]},
                    "bar": {"color": "darkblue"},
                    "steps": [
                        {"range": [0, 10], "color": "lightgreen"},
                        {"range": [10, 50], "color": "yellow"},
                        {"range": [50, 100], "color": "orange"},
                    ],
                },
            ),
            row=1,
            col=1,
        )

        # Architecture components
        arch_data = ["Nodes", "Inputs", "Outputs", "Initializers"]
        arch_values = [total_nodes, total_inputs, total_outputs, total_initializers]

        fig.add_trace(
            go.Bar(x=arch_data, y=arch_values, marker_color=["blue", "green", "orange", "red"], showlegend=False),
            row=1,
            col=2,
        )

        # I/O Table
        io_data = []

        # Add input info
        for inp in graph.input[:5]:  # Limit to first 5
            shape = "Unknown"
            dtype = "Unknown"
            if inp.type and inp.type.tensor_type:
                # Get shape
                if inp.type.tensor_type.shape:
                    dims = [str(d.dim_value) if d.dim_value > 0 else "?" for d in inp.type.tensor_type.shape.dim]
                    shape = f"[{', '.join(dims)}]"

                # Get data type
                elem_type = inp.type.tensor_type.elem_type
                type_map = {
                    1: "float32",
                    2: "uint8",
                    3: "int8",
                    6: "int32",
                    7: "int64",
                    9: "bool",
                    10: "float16",
                    11: "double",
                }
                dtype = type_map.get(elem_type, f"type_{elem_type}")

            io_data.append(["Input", inp.name[:20], shape, dtype])

        # Add output info
        for out in graph.output[:5]:  # Limit to first 5
            shape = "Unknown"
            dtype = "Unknown"
            if out.type and out.type.tensor_type:
                if out.type.tensor_type.shape:
                    dims = [str(d.dim_value) if d.dim_value > 0 else "?" for d in out.type.tensor_type.shape.dim]
                    shape = f"[{', '.join(dims)}]"

                elem_type = out.type.tensor_type.elem_type
                type_map = {
                    1: "float32",
                    2: "uint8",
                    3: "int8",
                    6: "int32",
                    7: "int64",
                    9: "bool",
                    10: "float16",
                    11: "double",
                }
                dtype = type_map.get(elem_type, f"type_{elem_type}")

            io_data.append(["Output", out.name[:20], shape, dtype])

        if io_data:
            fig.add_trace(
                go.Table(
                    header=dict(values=["Type", "Name", "Shape", "Data Type"], fill_color="lightblue", align="left"),
                    cells=dict(values=list(zip(*io_data)), fill_color="white", align="left"),
                ),
                row=2,
                col=1,
            )

        # Parameters indicator
        fig.add_trace(
            go.Indicator(
                mode="number",
                value=total_params,
                title={"text": "Total Parameters"},
                number={"suffix": "M", "valueformat": ".2f"},
                number_font_size=30,
            ),
            row=2,
            col=2,
        )

        fig.update_layout(
            title={
                "text": (
                    "ONNX Model Metadata<br>"
                    f"<span style='font-size:14px; color:#a0a0a0;'>{total_params/1e6:.2f}M Parameters</span>"
                ),
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 22},
            },
            height=600,
            template="plotly_dark",
            showlegend=False,
        )

        return fig

    except Exception as e:
        return create_styled_error_figure(
            "Metadata Analysis Error", "Could not extract ONNX model metadata.", f"Error: {str(e)}"
        )


def performance_metrics(file_path: Path) -> go.Figure:
    """
    Display performance and computational metrics for the ONNX model.
    Matches layout ID: performance_metrics
    """
    if not ONNX_AVAILABLE:
        return create_styled_error_figure(
            "ONNX Not Available",
            "ONNX library is required for performance analysis.",
            "Install with: pip install onnx",
        )

    try:
        model = onnx.load(str(file_path))
        graph = model.graph

        # Calculate metrics
        model_size_bytes = file_path.stat().st_size
        model_size_mb = model_size_bytes / (1024 * 1024)

        # Count parameters
        total_params = 0
        for initializer in graph.initializer:
            try:
                tensor = onnx.numpy_helper.to_array(initializer)
                total_params += tensor.size
            except Exception:
                pass

        # Estimate memory usage (rough approximation)
        param_memory_mb = (total_params * 4) / (1024 * 1024)  # Assume float32

        # Count operations by complexity
        compute_ops = ["Conv", "MatMul", "Gemm", "LSTM", "GRU"]
        efficient_ops = ["Relu", "Add", "Mul", "BatchNormalization", "Dropout"]

        compute_count = sum(1 for node in graph.node if any(op in node.op_type for op in compute_ops))
        efficient_count = sum(1 for node in graph.node if any(op in node.op_type for op in efficient_ops))
        total_ops = len(graph.node)
        other_count = total_ops - compute_count - efficient_count

        # Create performance dashboard
        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=("Model Efficiency", "Memory Usage", "Operation Types", "Complexity Score"),
            specs=[[{"type": "bar"}, {"type": "bar"}], [{"type": "pie"}, {"type": "indicator"}]],
        )

        # Model efficiency metrics
        efficiency_metrics = ["Model Size (MB)", "Parameters (M)", "Total Ops"]
        efficiency_values = [model_size_mb, total_params / 1e6, total_ops]

        fig.add_trace(
            go.Bar(
                x=efficiency_metrics, y=efficiency_values, marker_color=["blue", "green", "orange"], showlegend=False
            ),
            row=1,
            col=1,
        )

        # Memory usage
        memory_types = ["Parameters", "Est. Inference"]
        memory_values = [param_memory_mb, param_memory_mb * 2]  # Rough estimate

        fig.add_trace(
            go.Bar(x=memory_types, y=memory_values, marker_color=["purple", "red"], showlegend=False),
            row=1,
            col=2,
        )

        # Operation types pie chart
        fig.add_trace(
            go.Pie(
                labels=["Compute Ops", "Efficient Ops", "Other Ops"],
                values=[compute_count, efficient_count, other_count],
                marker_colors=["red", "green", "gray"],
            ),
            row=2,
            col=1,
        )

        # Complexity score (simple heuristic)
        complexity_score = min(100, (model_size_mb * 10 + total_params / 1e6 * 20 + compute_count))

        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=complexity_score,
                title={"text": "Complexity Score"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {
                        "color": "darkred" if complexity_score > 70 else "orange" if complexity_score > 40 else "green"
                    },
                    "steps": [
                        {"range": [0, 40], "color": "lightgreen"},
                        {"range": [40, 70], "color": "yellow"},
                        {"range": [70, 100], "color": "lightcoral"},
                    ],
                },
            ),
            row=2,
            col=2,
        )

        fig.update_layout(
            title={
                "text": (
                    "ONNX Performance Metrics<br>"
                    f"<span style='font-size:14px; color:#a0a0a0;'>"
                    f"Complexity Score: {complexity_score:.0f}/100</span>"
                ),
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 22},
            },
            height=600,
            template="plotly_dark",
            showlegend=False,
        )

        return fig

    except Exception as e:
        return create_styled_error_figure(
            "Performance Analysis Error", "Could not analyze ONNX model performance.", f"Error: {str(e)}"
        )
