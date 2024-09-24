# plots/plotting.py

import matplotlib.pyplot as plt
import pandas as pd
import os

def plot_data(figure, data_files, plot_details, axis_details, plot_visuals, is_3d=False):
    # Clear the figure
    figure.clear()

    # Apply plot style
    plot_style = plot_visuals['plot_style'].lower()
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
            df = pd.read_csv(file_path)
            x_col = int(plot_details['x_axis_col']) - 1
            y_col = int(plot_details['y_axis_col']) - 1
            x = df.iloc[:, x_col]
            y = df.iloc[:, y_col]
            z = i if is_3d else None
        except Exception as e:
            print(f"Error loading file {file_path}: {e}")
            continue

        label = os.path.splitext(os.path.basename(file_path))[0]
        line_style = {'Solid': '-', 'Dashed': '--', 'Dash-Dot': '-.'}[plot_details['line_style']]
        point_style = {
            "None": "",
            "Circle": "o",
            "Square": "s",
            "Triangle Up": "^",
            "Triangle Down": "v",
            "Star": "*",
            "Plus": "+",
            "Cross": "x"
        }[plot_details['point_style']]
        line_thickness = int(plot_details['line_thickness'])

        plot_type = plot_visuals['plot_type'].lower()

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
                # Pie chart in 3D doesn't make sense; placeholder
                pass
            else:
                ax.pie(y, labels=x)

    # Set axis labels and title
    ax.set_title(axis_details['title'], fontsize=axis_details['title_font_size'], pad=20)
    ax.set_xlabel(axis_details['x_label'], fontsize=axis_details['axis_font_size'])
    if is_3d:
        ax.set_ylabel('Offset', fontsize=axis_details['axis_font_size'])
        ax.set_zlabel(axis_details['y_label'], fontsize=axis_details['axis_font_size'])
    else:
        ax.set_ylabel(axis_details['y_label'], fontsize=axis_details['axis_font_size'])

    # Apply axis ranges
    try:
        x_min = float(axis_details['x_min']) if axis_details['x_min'] else None
        x_max = float(axis_details['x_max']) if axis_details['x_max'] else None
        y_min = float(axis_details['y_min']) if axis_details['y_min'] else None
        y_max = float(axis_details['y_max']) if axis_details['y_max'] else None

        if x_min is not None and x_max is not None:
            ax.set_xlim(x_min, x_max)
        if y_min is not None and y_max is not None:
            ax.set_ylim(y_min, y_max)
    except ValueError:
        print("Invalid axis range values.")

    # Apply scales
    scale_type = plot_details['scale_type'].lower()
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
    if plot_visuals['add_grid']:
        ax.grid(True)
    if plot_visuals['add_sub_grid']:
        ax.minorticks_on()
        ax.grid(which='minor', linestyle=':', linewidth='0.5')

    # Add legend if required
    if plot_visuals['apply_legends']:
        ax.legend(fontsize=axis_details['legend_font_size'])

    # Redraw the figure
    figure.canvas.draw_idle()
