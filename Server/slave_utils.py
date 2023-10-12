import pandas as pd

def get_box_graph_params(file_name):
    data = pd.read_csv(file_name, sep=';')
    num_increments = 30

    # These are the base statistics columns for each measurement
    stats_columns = ["Minimum", "Q1", "Median", "Q3", "Maximum", "Mean", "Std"]

    # Set up our results DataFrame with an initial column for the incrementx
    results = pd.DataFrame(columns=["Increment"])

    # For each column in our input data (skipping the increment column)
    for column in data.columns[1:]:
        # Calculate stats for this column
        current_stats = {}
        for i in range(1, num_increments + 1):
            subset = data[data['Increment'] == i]
            
            current_stats["Increment"] = i
            current_stats[column + "_Minimum"] = subset[column].min()
            current_stats[column + "_Q1"] = subset[column].quantile(0.25)
            current_stats[column + "_Median"] = subset[column].median()
            current_stats[column + "_Q3"] = subset[column].quantile(0.75)
            current_stats[column + "_Maximum"] = subset[column].max()
            current_stats[column + "_Mean"] = subset[column].mean()
            current_stats[column + "_Std"] = subset[column].std()
            
            # Append this row of stats to our results DataFrame
            results = results.append(current_stats, ignore_index=True)

    # Save results to a new CSV
    results_filename = file_name
    results.to_csv(results_filename, index=False)

