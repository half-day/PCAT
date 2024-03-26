import numpy as np


def load_data(filepath: str, format: str):
    """Load point cloud data in binary format.

        Args:
            filepath (str): Path to binary format point cloud data.

        Returns:
            tuple: A tuple containing two numpy arrays. The first array contains
                the (x, y, z) coordinates of the points in the point cloud, and the
                second array contains the RGB colors of the points.
        """

    points_cloud = np.load(filepath)
    points = points_cloud[:,:3]
    colors = points_cloud[:,3:6]
    sem_labels = None
    ins_labels = None
    if format == 'x y z r g b sem':
        sem_labels = points_cloud[:,6]
    elif format == 'x y z r g b sem ins':
        sem_labels = points_cloud[:,6]
        ins_labels = points_cloud[:,7]
    return points, colors, sem_labels, ins_labels


def load_label(filepath: str):
    labels = np.load(filepath).astype(np.int32)
    if labels.shape[0] != 2:
        print('Error: label file should contain two arrays')
    labels[0, labels[0] == -1] = 0
    unique_labels = np.unique(labels[1])
    for i, x in enumerate(unique_labels):
        labels[1, labels[1] == x] = i
    return labels


def save_label(filepath: str, labels):
    with open(filepath, 'wb') as f:
        labels[labels == 0] = -1
        np.save(f, labels.astype(np.int32))
