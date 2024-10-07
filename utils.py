# utils.py

import os
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import QMessageBox

def read_numeric_data(file_path, parent=None, delimiter=',', max_lines=100):
    """
    Reads a CSV file and extracts numeric data, automatically detecting
    where data columns begin, regardless of metadata.

    Parameters:
        file_path (str): Path to the CSV file.
        parent (QWidget): Parent widget for QMessageBox.
        delimiter (str): Delimiter used in the CSV file.
        max_lines (int): Maximum number of lines to read while searching for data.

    Returns:
        tuple: (df, x, y) where df is the cleaned DataFrame, and x, y are numpy arrays.
               Returns (None, None, None) if reading fails.
    """
    import csv

    # Read the file line by line
    data_started = False
    header_line = None
    data_lines = []
    skiprows = 0

    with open(file_path, 'r') as f:
        reader = csv.reader(f, delimiter=delimiter)
        for i, row in enumerate(reader):
            if i >= max_lines:
                break  # Prevent infinite loops on large files with no data

            if not row or all(cell.strip() == '' for cell in row):
                skiprows += 1  # Empty line, skip
                continue

            # Try converting each cell to float
            numeric_cells = []
            non_numeric_cells = []
            for cell in row:
                try:
                    numeric_cells.append(float(cell))
                except ValueError:
                    non_numeric_cells.append(cell)

            if len(numeric_cells) >= 2:
                # Assume data starts here
                data_started = True
                data_lines.append(row)
                break
            else:
                skiprows += 1  # Not enough numeric data, continue

    if not data_started:
        if parent:
            QMessageBox.warning(parent, "Data Read Error",
                                f"Could not detect numeric data in {os.path.basename(file_path)}.")
        return None, None, None

    # Now read the data from the file starting from skiprows
    try:
        # Try reading with header
        df = pd.read_csv(file_path, delimiter=delimiter, skiprows=skiprows, engine='python')
        # Convert all columns to numeric, coercing errors to NaN
        df_numeric = df.apply(pd.to_numeric, errors='coerce')
        # Drop rows with any NaN values (removes non-numeric rows)
        df_numeric.dropna(inplace=True)

        # Ensure there are at least two columns for X and Y
        if df_numeric.shape[1] < 2:
            # Try reading without header
            df = pd.read_csv(file_path, delimiter=delimiter, skiprows=skiprows, header=None, engine='python')
            df_numeric = df.apply(pd.to_numeric, errors='coerce')
            df_numeric.dropna(inplace=True)
            if df_numeric.shape[1] < 2:
                if parent:
                    QMessageBox.warning(parent, "Insufficient Data",
                                        f"File {os.path.basename(file_path)} does not contain enough numeric columns.")
                return None, None, None
            else:
                # Assign default column names
                df_numeric.columns = [f"Column {i+1}" for i in range(df_numeric.shape[1])]

        x = df_numeric.iloc[:, 0].values
        y = df_numeric.iloc[:, 1].values
        return df_numeric, x, y

    except Exception as e:
        if parent:
            QMessageBox.warning(parent, "File Read Error",
                                f"An error occurred while reading {os.path.basename(file_path)}:\n{e}")
        return None, None, None
