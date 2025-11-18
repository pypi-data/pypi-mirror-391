import os
import pandas as pd
import numpy as np
import datetime
from .pairwise_distances import pairwise_distances
import importlib.resources

def assign_types(fasta_data, user_input, model='p-distance', gap_deletion=True, threshold=0.405, 
                 save_report=True, output_dir='reports', user_seq_names=None, distances_matrix=None):
    """
    Assigns types to query sequences based on p-distance to known prototypes.

    Args:
        fasta_data (pd.DataFrame): DataFrame from pairwise_distances input.
        model (str): Distance model (default 'p-distance').
        gap_deletion (bool): Whether to delete gaps (default True).
        threshold (float): Max p-distance for assignment (default 0.105).
        save_report (bool): If True, saves the output DataFrame to a CSV file.
        output_dir (str): Directory to save the report (default 'reports').

    Returns:
        pd.DataFrame: A DataFrame with query, assignedType, distance, and reference.
    """

    # Read prototype sequences
    try:
        # Determine the correct prototype CSV file
        user_input_cap = user_input.capitalize()
        if user_input_cap == 'Vp1':
            prototype_filename = 'vp1_test.csv'
        elif user_input_cap == 'Vp4/2':
            prototype_filename = 'prototypes.csv'
        else:
            raise ValueError("Invalid input. Please specify either 'Vp1' or 'Vp4/2'.")

        # Use importlib.resources to access the data file
        path_obj = importlib.resources.files('rhinotype.data').joinpath(prototype_filename)
        with importlib.resources.as_file(path_obj) as path:
            prototypes_df = pd.read_csv(path)
            
    except FileNotFoundError:
        raise Exception("Error: Failed during genotype assignment. Prototypes file not found. Please check the file path.")
    
    names_to_keep = prototypes_df['Accession'].tolist()

    # Run pairwiseDistances to calculate distances
    if distances_matrix is not None:
        print("Using pre-calculated distance matrix.")
        distances = distances_matrix.copy() # Use the provided matrix
    else:
        print("Calculating pairwise distances for assign_types...")
        # Run pairwiseDistances to calculate distances
        distances = pairwise_distances(fasta_data, model=model, gap_deletion=gap_deletion)

    # Filter columns based on the prototypes
    distances = distances.loc[:, distances.columns.isin(names_to_keep)]

    if user_seq_names is not None:
        # We *only* want to classify the user's sequences.
        print(f"Attempting to filter for {len(user_seq_names)} user-provided sequence names...")

        # Get all valid names from the distance matrix (i.e., not prototypes)
        all_mafft_names = [
            idx_name for idx_name in distances.index 
            if idx_name not in names_to_keep
        ]

        names_to_classify = []

        # Loop through each of the user's original names
        for original_name in user_seq_names:
            found_match = False
            # Loop through all the (potentially truncated) names from the MAFFT alignment
            for mafft_name in all_mafft_names:
                # Check if the MAFFT name *starts with* the user's original name
                if mafft_name.startswith(original_name):
                    names_to_classify.append(mafft_name)
                    found_match = True
                    break # Found a match, go to the next original_name

            if not found_match:
                print(f"Warning: Could not find a match for original name: {original_name}")

        distances = distances.loc[names_to_classify, :]
        print(f"Report filtered for {len(names_to_classify)} user-provided sequences.")

    else:
        # Fallback to old behavior if user_seq_names is not provided
        print("Warning: No user_seq_names provided. Classifying all non-prototypes.")
        distances = distances.loc[~distances.index.isin(names_to_keep), :]

    # Initialize lists to store output data
    query_vec = []
    assigned_type_vec = []
    distance_vec = []
    ref_seq_vec = []

    # Iterate over each row (query) in the distances DataFrame
    for i, row in distances.iterrows():
        query_header = i
        valid_cols = row[row < threshold].index

        if len(valid_cols) == 0:
            # If no valid columns found, mark as "unassigned"
            assigned_type_vec.append("unassigned")
            distance_vec.append(np.nan)
            # Find the column with the minimum distance
            min_dist_col = row.idxmin()
            ref_seq_vec.append(min_dist_col)
        else:
            # Choose the one with the minimum distance
            min_distance_col = row[valid_cols].idxmin()
            assigned_type = min_distance_col
            assigned_type_vec.append(assigned_type.replace("RV", "").split("_")[-1])
            distance_vec.append(row[min_distance_col])
            ref_seq_vec.append(assigned_type)

        query_vec.append(query_header)

    # Create a DataFrame from the results
    output_df = pd.DataFrame({
        'query': query_vec,
        'assignedType': assigned_type_vec,
        'distance': distance_vec,
        'reference': ref_seq_vec
    })

    # --- Save Report ---
    if save_report:
        try:
            # Create the output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            # Sanitize the region name for the filename (replaces '/' with '_')
            region_name = user_input.capitalize().replace('/', '_')
            # Create a timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            # Define the filename
            filename = f"classification_report_{region_name}_{timestamp}.csv"
            # Define the full save path
            save_path = os.path.join(output_dir, filename)
            # Save the DataFrame to a CSV file
            output_df.to_csv(save_path, index=False)
            print(f"Classification report successfully saved to: {save_path}")
        except Exception as e:
            print(f"Error saving report: {e}")

    return output_df

if __name__ == "__main__":
    assign_types() 
