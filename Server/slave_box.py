import pandas as pd
import matplotlib.pyplot as plt

# Function to read the data from a file
def read_file_to_dataframe(file_path):
    df = pd.read_csv(file_path)
    return df

# Call the above function to read data from the file
file_path = "resultsEnergy2023-10-12-18:39:16.csv"  # Replace this with the path to your CSV file
df = read_file_to_dataframe(file_path)

# List of columns excluding the increment column
columns_to_plot = [col for col in df.columns if col != 'Increment']
print(columns_to_plot)

# Create a box plot for each column
for column in columns_to_plot:
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Group by increment value and get the values for box plotting
    grouped = [df[column][df['Increment'] == i].tolist() for i in range(1, 31)]
    
    ax.boxplot(grouped)  # Default is vert=True, vertical boxplots
    
    ax.set_title(f'{column} PLOT:')
    ax.set_xticks(range(1, 31))
    ax.set_xticklabels([f'{i}' for i in range(1, 31)])
    ax.set_ylabel(column)

    plt.show()
