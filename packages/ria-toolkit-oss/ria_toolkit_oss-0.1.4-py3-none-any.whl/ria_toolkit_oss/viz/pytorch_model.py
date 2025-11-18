"""Visualization functions for PyTorch model (.py) files.

This module provides visualization capabilities for PyTorch model Python files,
extracting architectural information through AST parsing and static analysis.
"""

import ast
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

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


def _parse_model_file(file_path: Path) -> Tuple[Optional[ast.Module], Optional[str]]:
    """Parse a Python model file and return the AST and any error message."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
        tree = ast.parse(code, filename=str(file_path))
        return tree, None
    except SyntaxError as e:
        return None, f"Syntax error in file: {e}"
    except Exception as e:
        return None, f"Failed to parse file: {e}"


def _find_model_class(tree: ast.Module) -> Optional[ast.ClassDef]:
    """Find the main model class (subclass of nn.Module) in the AST."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            # Check if it inherits from nn.Module or torch.nn.Module
            for base in node.bases:
                base_name = ""
                if isinstance(base, ast.Name):
                    base_name = base.id
                elif isinstance(base, ast.Attribute):
                    if isinstance(base.value, ast.Name):
                        base_name = f"{base.value.id}.{base.attr}"

                if "Module" in base_name or "nn.Module" in base_name:
                    return node
    return None


def _extract_layer_info(model_class: ast.ClassDef) -> List[Dict[str, Any]]:
    """Extract layer information from the model's __init__ method."""
    layers = []

    # Find __init__ method
    init_method = None
    for node in model_class.body:
        if isinstance(node, ast.FunctionDef) and node.name == "__init__":
            init_method = node
            break

    if not init_method:
        return layers

    # Parse assignments in __init__
    for node in ast.walk(init_method):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Attribute):
                    layer_name = target.attr
                    layer_type = _extract_layer_type(node.value)
                    if layer_type:
                        layers.append(
                            {"name": layer_name, "type": layer_type, "details": _extract_layer_params(node.value)}
                        )

    return layers


def _extract_layer_type(node: ast.expr) -> Optional[str]:
    """Extract the layer type from an AST node."""
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            return node.func.attr
    return None


def _extract_layer_params(node: ast.Call) -> str:
    """Extract layer parameters as a string."""
    params = []

    # Extract positional arguments
    for arg in node.args:
        if isinstance(arg, ast.Constant):
            params.append(str(arg.value))
        elif isinstance(arg, ast.Name):
            params.append(arg.id)

    # Extract keyword arguments
    for keyword in node.keywords:
        if isinstance(keyword.value, ast.Constant):
            params.append(f"{keyword.arg}={keyword.value.value}")
        elif isinstance(keyword.value, ast.Name):
            params.append(f"{keyword.arg}={keyword.value.id}")

    return ", ".join(params)


def _count_parameters(layers: List[Dict[str, Any]]) -> int:
    """Estimate parameter count from layer definitions (rough estimate)."""
    # This is a very rough estimate - actual counts would require instantiating the model
    param_estimates = {
        "Linear": 1000,
        "Conv1d": 500,
        "Conv2d": 5000,
        "Conv3d": 10000,
        "LSTM": 4000,
        "GRU": 3000,
        "TransformerEncoder": 50000,
        "Embedding": 10000,
    }

    total = 0
    for layer in layers:
        layer_type = layer["type"]
        total += param_estimates.get(layer_type, 100)

    return total


def model_architecture_plot(file_path: Path) -> Figure:
    """Visualize the architecture of a PyTorch model from its .py file.

    Parses the model file using AST to extract layers and their connections.
    """
    tree, error = _parse_model_file(file_path)

    if error:
        return create_styled_error_figure(
            "Parse Error", error, "Ensure the .py file contains valid Python code with a PyTorch nn.Module class"
        )

    model_class = _find_model_class(tree)
    if not model_class:
        return create_styled_error_figure(
            "No Model Found",
            "Could not find a PyTorch nn.Module class in the file",
            "Ensure your model class inherits from torch.nn.Module or nn.Module",
        )

    layers = _extract_layer_info(model_class)

    if not layers:
        return create_styled_error_figure(
            "No Layers Found",
            "Could not extract layer information from the model",
            "Ensure your model defines layers in the __init__ method",
        )

    # Create a hierarchical visualization
    layer_names = [f"{i+1}. {layer['name']}" for i, layer in enumerate(layers)]
    layer_types = [layer["type"] for layer in layers]
    layer_details = [layer["details"] for layer in layers]

    # Create a bar chart showing layers
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            y=layer_names,
            x=[1] * len(layer_names),
            orientation="h",
            text=layer_types,
            textposition="inside",
            hovertext=[
                f"{name}<br>Type: {type_}<br>Params: {details}"
                for name, type_, details in zip(layer_names, layer_types, layer_details)
            ],
            hoverinfo="text",
            marker=dict(color="rgba(99, 179, 237, 0.8)", line=dict(color="rgba(99, 179, 237, 1.0)", width=2)),
        )
    )

    fig.update_layout(
        title=f"Model Architecture: {model_class.name}",
        xaxis=dict(visible=False),
        yaxis=dict(title="Layers", autorange="reversed"),
        template="plotly_dark",
        height=max(400, len(layers) * 40),
        showlegend=False,
        margin=dict(l=200, r=40, t=60, b=40),
    )

    return fig


def model_complexity_plot(file_path: Path) -> Figure:
    """Analyze and visualize model complexity metrics."""
    tree, error = _parse_model_file(file_path)

    if error:
        return create_styled_error_figure("Parse Error", error, "Ensure the .py file contains valid Python code")

    model_class = _find_model_class(tree)
    if not model_class:
        return create_styled_error_figure("No Model Found", "Could not find a PyTorch nn.Module class in the file")

    layers = _extract_layer_info(model_class)

    if not layers:
        return create_styled_error_figure("No Layers Found", "Could not extract layer information from the model")

    # Count layer types
    layer_type_counts = {}
    for layer in layers:
        layer_type = layer["type"]
        layer_type_counts[layer_type] = layer_type_counts.get(layer_type, 0) + 1

    # Create pie chart of layer types
    fig = go.Figure(
        data=[
            go.Pie(
                labels=list(layer_type_counts.keys()),
                values=list(layer_type_counts.values()),
                hole=0.3,
                marker=dict(colors=["#5c79ff", "#63b3ed", "#48bb78", "#f6ad55", "#fc8181"]),
            )
        ]
    )

    fig.update_layout(
        title="Layer Type Distribution",
        template="plotly_dark",
        height=400,
    )

    return fig


def model_metadata_plot(file_path: Path) -> Figure:
    """Display model metadata and information extracted from the Python file (clean, aligned layout)."""
    import textwrap

    tree, error = _parse_model_file(file_path)
    if error:
        return create_styled_error_figure("Parse Error", error, "Ensure the .py file contains valid Python code")

    model_class = _find_model_class(tree)
    if not model_class:
        return create_styled_error_figure("No Model Found", "Could not find a PyTorch nn.Module class in the file")

    layers = _extract_layer_info(model_class)

    # Extract imports
    imports = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)

    # Get docstring and wrap it
    docstring = ast.get_docstring(model_class) or "No docstring available"
    wrapped_doc = "<br>".join(textwrap.wrap(docstring, width=70))

    relevant_imports = [imp for imp in imports if "torch" in imp or "nn" in imp][:4]
    param_count = _count_parameters(layers)

    # Define card grid (aligned 2x2)
    cards = [
        {"x": 0.05, "y": 0.93, "width": 0.43, "height": 0.38, "title": "📦 Model Overview", "color": "#2d5f8d"},
        {"x": 0.52, "y": 0.93, "width": 0.43, "height": 0.38, "title": "🔢 Statistics", "color": "#2d6b5f"},
        {"x": 0.05, "y": 0.46, "width": 0.43, "height": 0.38, "title": "📝 Description", "color": "#5d4b7a"},
        {"x": 0.52, "y": 0.46, "width": 0.43, "height": 0.38, "title": "📚 Dependencies", "color": "#7a5b3d"},
    ]

    fig = go.Figure()

    # Draw background cards with consistent opacity
    for card in cards:
        fig.add_shape(
            type="rect",
            xref="paper",
            yref="paper",
            x0=card["x"],
            y0=card["y"] - card["height"],
            x1=card["x"] + card["width"],
            y1=card["y"],
            fillcolor=card["color"],
            line=dict(color="#4a5568", width=2),
            opacity=0.3,
            layer="below",
        )
        # Header bar
        fig.add_shape(
            type="rect",
            xref="paper",
            yref="paper",
            x0=card["x"],
            y0=card["y"] - 0.07,
            x1=card["x"] + card["width"],
            y1=card["y"],
            fillcolor=card["color"],
            line=dict(width=0),
            opacity=0.45,
            layer="below",
        )

    # --- CARD 1: Model Overview ---
    card = cards[0]
    fig.add_annotation(
        text=f"<b>{card['title']}</b>",
        xref="paper",
        yref="paper",
        x=card["x"] + 0.03,
        y=card["y"] - 0.02,
        xanchor="left",
        yanchor="middle",
        showarrow=False,
        align="left",
        font=dict(size=15, color="#ffffff", family="Inter, Arial, sans-serif"),
    )
    fig.add_annotation(
        text=f"<b style='font-size:26px;color:#ffffff'>{model_class.name}</b><br>"
        f"<span style='color:#94a3b8;font-size:15px'>PyTorch Neural Network</span>",
        xref="paper",
        yref="paper",
        x=card["x"] + 0.04,
        y=card["y"] - 0.13,
        xanchor="left",
        yanchor="top",
        showarrow=False,
        align="left",
        font=dict(size=15, color="#cbd5e0", family="Inter, Arial, sans-serif"),
    )

    # --- CARD 2: Statistics ---
    card = cards[1]
    y_center = card["y"] - card["height"] / 2
    fig.add_annotation(
        text=f"<b>{card['title']}</b>",
        xref="paper",
        yref="paper",
        x=card["x"] + 0.03,
        y=card["y"] - 0.02,
        xanchor="left",
        yanchor="middle",
        showarrow=False,
        font=dict(size=15, color="#ffffff", family="Inter, Arial, sans-serif"),
    )
    fig.add_annotation(
        text=f"<b style='font-size:44px;color:#63b3ed'>{len(layers)}</b><br>"
        f"<span style='color:#94a3b8;font-size:13px;letter-spacing:1.5px'>LAYERS</span>",
        xref="paper",
        yref="paper",
        x=card["x"] + card["width"] / 2,
        y=y_center + 0.07,
        xanchor="center",
        yanchor="middle",
        showarrow=False,
        align="center",
    )
    fig.add_annotation(
        text=f"<b style='font-size:36px;color:#48bb78'>~{param_count:,}</b><br>"
        f"<span style='color:#94a3b8;font-size:13px;letter-spacing:1.5px'>PARAMETERS</span>",
        xref="paper",
        yref="paper",
        x=card["x"] + card["width"] / 2,
        y=y_center - 0.10,
        xanchor="center",
        yanchor="middle",
        showarrow=False,
        align="center",
    )

    # --- CARD 3: Description ---
    card = cards[2]
    fig.add_annotation(
        text=f"<b>{card['title']}</b>",
        xref="paper",
        yref="paper",
        x=card["x"] + 0.03,
        y=card["y"] - 0.02,
        xanchor="left",
        yanchor="middle",
        showarrow=False,
        font=dict(size=15, color="#ffffff", family="Inter, Arial, sans-serif"),
    )
    fig.add_annotation(
        text=f"<span style='color:#cbd5e0;font-size:14px;line-height:1.5'>{wrapped_doc}</span>",
        xref="paper",
        yref="paper",
        x=card["x"] + 0.04,
        y=card["y"] - 0.13,
        xanchor="left",
        yanchor="top",
        showarrow=False,
        align="left",
    )

    # --- CARD 4: Dependencies ---
    card = cards[3]
    fig.add_annotation(
        text=f"<b>{card['title']}</b>",
        xref="paper",
        yref="paper",
        x=card["x"] + 0.03,
        y=card["y"] - 0.02,
        xanchor="left",
        yanchor="middle",
        showarrow=False,
        font=dict(size=15, color="#ffffff", family="Inter, Arial, sans-serif"),
    )
    imports_text = (
        "<br>".join(
            [
                f"<span style='color:#48bb78;font-size:16px'>▸</span> "
                f"<span style='color:#e2e8f0;font-family:\"Courier New\",monospace;font-size:14px'>{imp}</span>"
                for imp in relevant_imports
            ]
        )
        if relevant_imports
        else "<span style='color:#94a3b8;font-style:italic;font-size:14px'>No torch imports detected</span>"
    )
    fig.add_annotation(
        text=imports_text,
        xref="paper",
        yref="paper",
        x=card["x"] + 0.04,
        y=card["y"] - 0.13,
        xanchor="left",
        yanchor="top",
        showarrow=False,
        align="left",
    )

    # Layout polish
    fig.update_layout(
        title=dict(
            text="<b>Model Metadata</b>",
            font=dict(size=20, color="#e2e8f0", family="Inter, Arial, sans-serif"),
            x=0.5,
            xanchor="center",
        ),
        template="plotly_dark",
        height=500,
        margin=dict(l=20, r=20, t=70, b=20),
        plot_bgcolor="#1a202c",
        paper_bgcolor="#1a202c",
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig


def code_structure_plot(file_path: Path) -> Figure:
    """Visualize the code structure and method definitions in the model."""
    tree, error = _parse_model_file(file_path)

    if error:
        return create_styled_error_figure("Parse Error", error, "Ensure the .py file contains valid Python code")

    model_class = _find_model_class(tree)
    if not model_class:
        return create_styled_error_figure("No Model Found", "Could not find a PyTorch nn.Module class in the file")

    # Extract methods
    methods = []
    for node in model_class.body:
        if isinstance(node, ast.FunctionDef):
            # Count lines in method
            if hasattr(node, "end_lineno") and hasattr(node, "lineno"):
                lines = node.end_lineno - node.lineno + 1
            else:
                lines = 1

            methods.append({"name": node.name, "lines": lines, "args": len(node.args.args) - 1})  # Exclude self

    if not methods:
        return create_styled_error_figure(
            "No Methods Found", "Could not extract method information from the model class"
        )

    # Create visualization of methods
    method_names = [m["name"] for m in methods]
    method_lines = [m["lines"] for m in methods]
    method_args = [m["args"] for m in methods]

    fig = go.Figure()

    # Bar chart for method complexity (lines of code)
    fig.add_trace(
        go.Bar(
            x=method_names,
            y=method_lines,
            name="Lines of Code",
            marker=dict(color="rgba(99, 179, 237, 0.8)"),
            hovertext=[
                f"{name}<br>Lines: {lines}<br>Arguments: {args}"
                for name, lines, args in zip(method_names, method_lines, method_args)
            ],
            hoverinfo="text",
        )
    )

    fig.update_layout(
        title=f"Method Complexity - {model_class.name}",
        xaxis_title="Methods",
        yaxis_title="Lines of Code",
        template="plotly_dark",
        height=400,
        showlegend=False,
    )

    return fig
