import numpy as np
import pandas as pd
from .readfasta import read_fasta
import math
from .distance_helpers import ( _count_substitutions_k2p, _count_substitutions_tn93)

def delete_missing_data_sites(seqs):
    # Convert list of sequences into a matrix where each sequence is a row
    seq_matrix = np.array([list(seq) for seq in seqs])

    # Find columns that do not contain gaps (assuming "-" as the gap symbol)
    valid_columns = np.all(seq_matrix != '-', axis=0)

    # Extract these columns to create a cleaned matrix
    cleaned_matrix = seq_matrix[:, valid_columns]

    # Convert cleaned matrix back to a list of sequences
    cleaned_seqs = [''.join(row) for row in cleaned_matrix]

    return cleaned_seqs

def count_snps_helper(fasta_data, gap_deletion=True):
    refs = fasta_data['sequences']
    ref_headers = fasta_data['headers']

    # Optionally remove sites with missing data
    if gap_deletion:
        refs = delete_missing_data_sites(refs)

    # Convert all cleaned sequences to a matrix of character vectors
    seq_matrix = np.array([list(seq) for seq in refs])

    # Initialize the SNP matrix
    n = len(seq_matrix)
    snp_matrix = np.full((n, n), np.nan)

    # Loop over all pairs of sequences using matrix indices
    for i in range(n):
        for j in range(i, n):
            seq1 = seq_matrix[i, :]
            seq2 = seq_matrix[j, :]

            # Calculate SNPs
            if len(seq1) == len(seq2) and len(seq1) > 0:
                snps = np.sum(seq1 != seq2)
                snp_matrix[i, j] = snp_matrix[j, i] = snps
            else:
                snp_matrix[i, j] = snp_matrix[j, i] = np.nan

    return snp_matrix

def calc_p_distance(fasta_data, gap_deletion=True):
    # Count the SNPs between each query and each reference sequence
    snp_counts = count_snps_helper(fasta_data, gap_deletion=gap_deletion)

    # Extract query headers
    query_headers = ref_headers = fasta_data['headers']

    # Directly calculate reference sequence lengths
    refs = fasta_data['sequences']

    # Optionally remove sites with missing data
    if gap_deletion:
        refs = delete_missing_data_sites(refs)

    ref_lengths = np.array([len(seq) for seq in refs])

    # Prepare a matrix for p-distances with appropriate dimensions and names
    p_distances_matrix = np.empty((len(query_headers), len(ref_lengths)))
    p_distances_matrix[:] = np.nan
    p_distances_matrix = pd.DataFrame(p_distances_matrix, index=query_headers, columns=ref_headers)

    # Calculate p-distance for each query-reference pair
    for q in range(len(snp_counts)):
        for i in range(len(ref_lengths)):
            if not np.isnan(snp_counts[q, i]):
                if ref_lengths[i] == 0:
                    p_distances_matrix.iloc[q, i] = np.nan # Avoid division by zero
                else:
                    p_distances_matrix.iloc[q, i] = snp_counts[q, i] / ref_lengths[i]

    return p_distances_matrix

def calc_jukes_cantor_distance(fasta_data, gap_deletion=True):
    # Calculate p-distance for multiple queries
    p_dist = calc_p_distance(fasta_data, gap_deletion=gap_deletion)

    # Initialize a matrix to store Jukes-Cantor distances
    jc_dist = np.zeros_like(p_dist)

    # Apply the Jukes-Cantor formula to each element in the p-distance matrix
    jc_dist = -3/4 * np.log(1 - 4/3 * p_dist)

    # Handling cases where p_dist >= 0.75, setting JC distance to Inf
    jc_dist[p_dist >= 0.749999] = np.inf # Use a buffer for float precision

    # Return the Jukes-Cantor genetic distance matrix
    return jc_dist

def calc_kimura_2p_distance(fasta_data, gap_deletion=True):
    refs = queries = fasta_data['sequences']
    ref_headers = query_headers = fasta_data['headers']

    # Note: K2P and TN93 perform their own pairwise deletion via the
    # helper functions, so we pass the original (aligned) sequences.
    # We only apply gap_deletion if it's for p-distance or JC69,
    # which is handled in those functions.
    # If gap_deletion is True, it means complete deletion, which we
    # can do first.
    if gap_deletion:
        # This applies complete deletion *before* pairwise calculation
        all_seqs = delete_missing_data_sites(refs)
        refs = queries = all_seqs
    
    k2p_matrix = np.full((len(queries), len(refs)), np.nan)

    for q in range(len(queries)):
        seq1 = queries[q]
        for r in range(q, len(refs)):
            seq2 = refs[r]

            if q == r:
                k2p_matrix[q, r] = 0.0
                continue

            # Step 1: Get substitution counts using the robust counter
            # We pass the raw (or completely-deleted) sequences here
            L, S, V = _count_substitutions_k2p(seq1, seq2)

            if L == 0:
                k2p_matrix[q, r] = k2p_matrix[r, q] = 0.0
                continue

            # Step 2: Calculate proportions of transitions (P) and transversions (Q)
            P = S / L
            Q = V / L

            # Step 3: CRITICAL - Check for mathematical domain errors
            arg1 = 1 - 2 * P - Q
            arg2 = 1 - 2 * Q

            distance = np.nan # Default to nan

            if arg1 > 1e-9 and arg2 > 1e-9: # Use a small epsilon for float safety
                # Step 4: Apply the K2P formula
                distance = -0.5 * math.log(arg1) - 0.25 * math.log(arg2)
            else:
                distance = float('inf') # Return infinity if not computable

            k2p_matrix[q, r] = k2p_matrix[r, q] = distance

    k2p_dataframe = pd.DataFrame(k2p_matrix, index=query_headers, columns=ref_headers)
    return k2p_dataframe

def calc_tamura_nei_distance(fasta_data, gap_deletion=True):
    refs = queries = fasta_data['sequences']
    ref_headers = query_headers = fasta_data['headers']

    if gap_deletion:
        all_seqs = delete_missing_data_sites(refs)
        refs = queries = all_seqs

    tn93_matrix = np.full((len(queries), len(refs)), np.nan)

    for q in range(len(queries)):
        seq1 = queries[q]
        for r in range(q, len(refs)): # Optimized loop
            seq2 = refs[r]

            if q == r:
                tn93_matrix[q, r] = 0.0
                continue

            # Step 1: Get detailed counts and frequencies
            L, S1, S2, V, freqs = _count_substitutions_tn93(seq1, seq2)

            if L == 0:
                tn93_matrix[q, r] = tn93_matrix[r, q] = 0.0
                continue

            # Step 2: Calculate proportions P1, P2, and Q
            P1 = S1 / L  # Purine transitions
            P2 = S2 / L  # Pyrimidine transitions
            Q = V / L

            # Step 3: Calculate base frequencies (from 0.0 to 1.0)
            total_freq = sum(freqs.values())
            if total_freq == 0:
                 tn93_matrix[q, r] = tn93_matrix[r, q] = 0.0
                 continue

            gA = freqs['A'] / total_freq
            gC = freqs['C'] / total_freq
            gG = freqs['G'] / total_freq
            gT = freqs['T'] / total_freq

            gR = gA + gG  # Frequency of purines
            gY = gC + gT  # Frequency of pyrimidines

            distance = np.nan # Default

            # Step 4: CRITICAL - Handle potential division-by-zero errors
            if gR <= 1e-9 or gY <= 1e-9 or (gA * gG) <= 1e-9 or (gC * gT) <= 1e-9:
                # Model is not applicable if certain base types are missing
                distance = float('inf')
            else:
                # Step 5: Calculate terms for the TN93 formula
                k1 = (2 * gA * gG) / gR
                k2 = (2 * gC * gT) / gY
                k3 = 2 * gR * gY

                term1_arg = 1 - P1 / k1 - Q / (2 * gR)
                term2_arg = 1 - P2 / k2 - Q / (2 * gY)
                term3_arg = 1 - Q / k3

                # Step 6: CRITICAL - Check for mathematical domain errors
                if term1_arg <= 1e-9 or term2_arg <= 1e-9 or term3_arg <= 1e-9:
                    distance = float('inf')
                else:
                    # Step 7: Apply the full TN93 formula
                    term1 = -k1 * math.log(term1_arg)
                    term2 = -k2 * math.log(term2_arg)
                    term3 = -(k3 - k1 * gY - k2 * gR) * math.log(term3_arg)

                    distance = term1 + term2 + term3

            tn93_matrix[q, r] = tn93_matrix[r, q] = distance

    tn93_dataframe = pd.DataFrame(tn93_matrix, index=query_headers, columns=ref_headers)
    return tn93_dataframe


if __name__ == "__main__":
    # These functions can't be run directly without fasta_data
    print("This module provides genetic distance calculation functions.")
    delete_missing_data_sites()
    count_snps_helper()
    calc_jukes_cantor_distance()
    calc_kimura_2p_distance()
    calc_p_distance()
    calc_tamura_nei_distance()
