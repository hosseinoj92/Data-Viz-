# plots/plotting.py

import matplotlib.pyplot as plt
import pandas as pd
import os
from utils import read_numeric_data  # Ensure this import is present

def plot_data(figure, data_files, plot_details, axis_details, plot_visuals, is_3d=False, parent=None):
    """
    Plots data from multiple CSV files onto the provided matplotlib figure.

    Parameters:
        figure (matplotlib.figure.Figure): The figure to plot on.
        data_files (list): List of file paths to CSV files.
        plot_details (dict): Dictionary containing plot-specific details like axis columns, line styles, etc.
        axis_details (dict): Dictionary containing axis labels, title, font sizes, etc.
        plot_visuals (dict): Dictionary containing visual settings like grid, legends, etc.
        is_3d (bool): Whether to plot in 3D.
        parent (QWidget): Parent widget for QMessageBox (optional).
    """
    # Clear the figure
    figure.clear()

    # Apply plot style
    plot_style = plot_visuals.get('plot_style', 'default').lower()
    if plot_style == "full_grid":
        plt.style.use('default')
        plt.rcParams['grid.color'] = 'black'
        plt.rcParams['grid.linestyle'] = '-'
        plt.rcParams['grid.linewidth'] = 0.7
        plt.rcParams['axes.grid.which'] = 'both'
        plt.rcParams['xtick.minor.visible'] = True
        plt.rcParams['ytick.minor.visible'] = True
    else:
        try:
            plt.style.use(plot_style)
        except Exception as e:
            print(f"Error applying style '{plot_style}': {e}")
            plt.style.use('default')

    # Prepare the axis
    ax = figure.add_subplot(111, projection='3d' if is_3d else None)

    # Plot each data file
    for i, file_path in enumerate(data_files):
        try:
            # Use read_numeric_data to read and clean data
            df, x, y = read_numeric_data(file_path, parent=parent)
            if df is None:
                print(f"Skipping file {file_path} due to insufficient data.")
                continue

            # Retrieve column indices from plot_details
            x_col = int(plot_details.get('x_axis_col', 1)) - 1  # Default to first column
            y_col = int(plot_details.get('y_axis_col', 2)) - 1  # Default to second column

            # Validate column indices
            if x_col >= df.shape[1] or y_col >= df.shape[1]:
                print(f"Selected columns do not exist in {file_path}.")
                continue

            # Extract selected columns
            x = df.iloc[:, x_col].values
            y = df.iloc[:, y_col].values
            z = i if is_3d else None
        except Exception as e:
            print(f"Error loading file {file_path}: {e}")
            continue

        label = os.path.splitext(os.path.basename(file_path))[0]
        line_style = {'Solid': '-', 'Dashed': '--', 'Dash-Dot': '-.'}.get(plot_details.get('line_style', 'Solid'), '-')
        point_style = {
            "None": "",
            "Circle": "o",
            "Square": "s",
            "Triangle Up": "^",
            "Triangle Down": "v",
            "Star": "*",
            "Plus": "+",
            "Cross": "x"
        }.get(plot_details.get('point_style', 'None'), "")
        line_thickness = int(plot_details.get('line_thickness', 1))

        plot_type = plot_visuals.get('plot_type', 'line').lower()

        if plot_type == "line":
            if is_3d:
                ax.plot(x, [z]*len(x), y, label=label, linestyle=line_style, marker=point_style, linewidth=line_thickness)
            else:
                ax.plot(x, y, label=label, linestyle=line_style, marker=point_style, linewidth=line_thickness)
        elif plot_type == "bar":
            if is_3d:
                ax.bar(x, y, zs=z, zdir='y', label=label)
            else:
                ax.bar(x, y, label=label)
        elif plot_type == "scatter":
            if is_3d:
                ax.scatter(x, [z]*len(x), y, label=label)
            else:
                ax.scatter(x, y, label=label)
        elif plot_type == "histogram":
            if is_3d:
                ax.hist(y, zs=z, zdir='y', label=label)
            else:
                ax.hist(y, label=label)
        elif plot_type == "pie":
            if is_3d:
                pass  # Pie chart in 3D doesn't make sense
            else:
                ax.pie(y, labels=x)

    # Set axis labels and title with adjusted padding
    ax.set_title(axis_details.get('title', 'Data Plot'), fontsize=axis_details.get('title_font_size', 12), pad=20)
    ax.set_xlabel(axis_details.get('x_label', 'X-axis'), fontsize=axis_details.get('axis_font_size', 10))
    if is_3d:
        ax.set_ylabel('Offset', fontsize=axis_details.get('axis_font_size', 10))
        ax.set_zlabel(axis_details.get('y_label', 'Y-axis'), fontsize=axis_details.get('axis_font_size', 10))
    else:
        ax.set_ylabel(axis_details.get('y_label', 'Y-axis'), fontsize=axis_details.get('axis_font_size', 10))

    # Apply axis ranges
    try:
        x_min = float(axis_details.get('x_min')) if axis_details.get('x_min') else None
        x_max = float(axis_details.get('x_max')) if axis_details.get('x_max') else None
        y_min = float(axis_details.get('y_min')) if axis_details.get('y_min') else None
        y_max = float(axis_details.get('y_max')) if axis_details.get('y_max') else None

        if x_min is not None and x_max is not None:
            ax.set_xlim(x_min, x_max)
        if y_min is not None and y_max is not None:
            ax.set_ylim(y_min, y_max)
    except ValueError:
        print("Invalid axis range values.")

    # Apply scales
    scale_type = plot_details.get('scale_type', 'linear').lower()
    x_scale = 'linear'
    y_scale = 'linear'
    if 'logarithmic x-axis' in scale_type:
        x_scale = 'log'
    if 'logarithmic y-axis' in scale_type:
        y_scale = 'log'
    if 'logarithmic both axes' in scale_type:
        x_scale = y_scale = 'log'
    ax.set_xscale(x_scale)
    ax.set_yscale(y_scale)

    # Apply grid settings
    if plot_visuals.get('add_grid', False):
        ax.grid(True)
    if plot_visuals.get('add_sub_grid', False):
        ax.minorticks_on()
        ax.grid(which='minor', linestyle=':', linewidth='0.5')

    # Add legend if required
    if plot_visuals.get('apply_legends', False):
        ax.legend(fontsize=axis_details.get('legend_font_size', 10))

    # Redraw the figure
    figure.canvas.draw_idle()
