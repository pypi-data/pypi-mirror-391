import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os
import pandas as pd

def plot_distances(distances_matrix, region, output_dir=None):
    # Ensure the input is a DataFrame to leverage labels
    if not isinstance(distances_matrix, pd.DataFrame):
        distances_matrix = pd.DataFrame(distances_matrix)

    # Plotting the heatmap
    plt.figure(figsize=(18, 14))
    sns.heatmap(distances_matrix, cmap='YlOrRd', cbar=True, xticklabels=True, yticklabels=True)
    plt.title(f"{region} genetic distances between sequences")

    # Rotate the labels and adjust the font size for better readability
    plt.xticks(rotation=90, fontsize=4)
    plt.yticks(rotation=0, fontsize=4)

    # Handle output directory
    if output_dir is None:
        output_dir = os.path.join(os.getcwd(), "figures")

    os.makedirs(output_dir, exist_ok=True)
    save_path = os.path.join(output_dir, "distances.png")

    plt.savefig(save_path)
    # plt.show()

    print(f"Figure saved at: {save_path}")

if __name__ == "__main__":
    plot_distances()
