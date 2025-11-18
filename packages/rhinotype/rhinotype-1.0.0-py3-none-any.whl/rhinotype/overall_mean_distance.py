import numpy as np
import math
from Bio import SeqIO
from .genetic_distances import delete_missing_data_sites

# Import the ROBUST PAIRWISE functions we created
# This ensures the logic is 100% consistent with the matrix calculation
try:
    from .distance_helpers import (
        calculate_p_distance, 
        jukes_cantor_distance, 
        kimura_distance, 
        tamura_nei_distance
    )
except ImportError:
    print("Error: Could not import from distance_helpers.py.")
    print("Please ensure distance_helpers.py exists in your modules directory.")
    # This will stop the script if helpers are missing
    raise

# Calculate overall mean distance using p-distance
def overall_p_distance(fasta_data, gap_deletion=True):
    sequences = fasta_data['sequences']

    if gap_deletion:
        sequences = delete_missing_data_sites(sequences)

    num_sequences = len(sequences)
    total_distance = 0
    num_comparisons = 0

    for i in range(num_sequences - 1):
        for j in range(i + 1, num_sequences):
            seq_i = sequences[i]
            seq_j = sequences[j]
            
            # Use the robust pairwise helper function
            distance = calculate_p_distance(seq_i, seq_j)
            
            if not np.isnan(distance):
                total_distance += distance
                num_comparisons += 1

    overall_p_distance = total_distance / num_comparisons if num_comparisons > 0 else np.nan
    return overall_p_distance

# Calculate overall mean distance using Jukes-Cantor model
def overall_jc_distance(fasta_data, gap_deletion=True):
    sequences = fasta_data['sequences']

    if gap_deletion:
        sequences = delete_missing_data_sites(sequences)

    num_sequences = len(sequences)
    total_jc_distance = 0
    num_comparisons = 0
    
    for i in range(num_sequences - 1):
        for j in range(i + 1, num_sequences):
            seq_i = sequences[i]
            seq_j = sequences[j]

            # Use the robust pairwise helper functions
            p_dist = calculate_p_distance(seq_i, seq_j)
            jc_distance = jukes_cantor_distance(p_dist)

            # Check if distance is valid (not infinite or NaN)
            if not np.isinf(jc_distance) and not np.isnan(jc_distance):
                total_jc_distance += jc_distance
                num_comparisons += 1

    overall_mean_jc_distance = total_jc_distance / num_comparisons if num_comparisons > 0 else np.nan
    return overall_mean_jc_distance

# Calculate overall mean distance using Kimura 2 parameter model
def overall_k2p_distance(fasta_data, gap_deletion=True):
    sequences = fasta_data['sequences']

    if gap_deletion:
        sequences = delete_missing_data_sites(sequences)

    num_sequences = len(sequences)
    total_distance = 0
    num_comparisons = 0

    for i in range(num_sequences - 1):
        for j in range(i + 1, num_sequences):
            seq_i = sequences[i]
            seq_j = sequences[j]
            
            # Use the robust pairwise helper function
            k2p_distance = kimura_distance(seq_i, seq_j)

            # Check if distance is valid (not infinite or NaN)
            if not np.isinf(k2p_distance) and not np.isnan(k2p_distance):
                total_distance += k2p_distance
                num_comparisons += 1

    overall_mean_distance = total_distance / num_comparisons if num_comparisons > 0 else np.nan
    return overall_mean_distance

# Calculate overall mean distance using Tamura-Nei 93 model
def overall_tn93_distance(fasta_data, gap_deletion=True):
    sequences = fasta_data['sequences']

    if gap_deletion:
        sequences = delete_missing_data_sites(sequences)

    num_sequences = len(sequences)
    total_distance = 0
    num_comparisons = 0

    for i in range(num_sequences - 1):
        for j in range(i + 1, num_sequences):
            seq_i = sequences[i]
            seq_j = sequences[j]
            
            # Use the robust pairwise helper function
            tn93_distance = tamura_nei_distance(seq_i, seq_j)

            # Check if distance is valid (not infinite or NaN)
            if not np.isinf(tn93_distance) and not np.isnan(tn93_distance):
                total_distance += tn93_distance
                num_comparisons += 1

    overall_mean_distance = total_distance / num_comparisons if num_comparisons > 0 else np.nan
    return overall_mean_distance


# Main function to calculate overall mean distance based on the chosen model
def overall_mean_distance(fasta_data, model='p-distance', gap_deletion=True):
    if model == "p-distance":
        result = overall_p_distance(fasta_data, gap_deletion)
    elif model == "jc69":
        result = overall_jc_distance(fasta_data, gap_deletion)
    elif model == "k2p":
        result = overall_k2p_distance(fasta_data, gap_deletion)
    elif model == "tn93":
        result = overall_tn93_distance(fasta_data, gap_deletion)
    else:
        raise ValueError(f"Unknown model specified: '{model}'. "
                         "Choose from 'p-distance', 'jc69', 'k2p', or 'tn93'")

    print(f"Overall mean genetic distance ({model}): {result:.4f}")
    return result

if __name__ == "__main__":
    print("This module provides the overall_mean_distance() function.")
