import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

def plot_vertical_boxplots(file_path):
    # Try reading data with both delimiters
    try:
        data = pd.read_csv(file_path, sep=',')
        if len(data.columns) == 1:
            # If only one column, try semicolon
            data = pd.read_csv(file_path, sep=';')
    except:
        print("Failed to read the file with both , and ; delimiters.")
        return

    # Replacing special values with NaN
    data.replace('<not-counted>', np.nan, inplace=True)

    # Convert to float type
    for col in data.columns:
        data[col] = pd.to_numeric(data[col], errors='coerce')

    data_columns = [col for col in data.columns if col != 'Increment']
    output_file_name = "boxplots_output.pdf"

    with PdfPages(output_file_name) as pdf:
        for col in data_columns:
            fig, ax = plt.subplots(figsize=(12, 8))

            # Extract the box data for each increment
            box_data = [data[data['Increment'] == increment][col].dropna().values for increment in data['Increment'].unique()]
            
            # Create the box and whisker plot
            ax.boxplot(box_data, whis=1.5, vert=True, patch_artist=True)
            
            ax.set_title(col)
            ax.set_xlabel('Increment')
            ax.set_ylabel('Value')
            
            # Setting x ticks labels as Increment values
            ax.set_xticks(np.arange(1, len(data['Increment'].unique()) + 1))
            ax.set_xticklabels(data['Increment'].unique())

            plt.tight_layout()
            pdf.savefig(fig) # saves the current figure into the pdf file
            plt.close() # close the figure to free up memory

    print(f"All plots saved in {output_file_name}")

if __name__ == "__main__":
    file_path = "resultsEnergy2023-10-12-18:39:16.csv"
    plot_vertical_boxplots(file_path)
