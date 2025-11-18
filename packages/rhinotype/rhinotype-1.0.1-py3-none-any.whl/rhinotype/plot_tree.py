import numpy as np
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import squareform
import matplotlib.pyplot as plt
import os

def plot_tree(distance_matrix, region, output_dir=None):
    # Convert the data to a numpy array if it's not already
    distance_matrix = np.array(distance_matrix)

    # Convert the symmetric distance matrix to a condensed distance matrix
    condensed_distance_matrix = squareform(distance_matrix)

    # Perform hierarchical clustering using complete linkage
    hc = linkage(condensed_distance_matrix, method='complete')

    # Plot the dendrogram
    plt.figure(figsize=(15, 8))
    dendrogram(hc, leaf_rotation=90, leaf_font_size=8)
    plt.title(f"{region} simple tree")
    plt.xlabel("")
    plt.ylabel("Genetic distance")
    # Handle output directory
    if output_dir is None:
        output_dir = os.path.join(os.getcwd(), "figures")

    os.makedirs(output_dir, exist_ok=True)
    save_path = os.path.join(output_dir, "tree.png")

    plt.savefig(save_path)
    # plt.show()

    print(f"Figure saved at: {save_path}")

if __name__ == "__main__":
    plot_tree()
