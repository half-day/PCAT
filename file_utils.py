import numpy as np


def load_data(filepath: str):
    """Load point cloud data in binary format.

        Args:
            filepath (str): Path to binary format point cloud data.

        Returns:
            tuple: A tuple containing two numpy arrays. The first array contains
                the (x, y, z) coordinates of the points in the point cloud, and the
                second array contains the RGB colors of the points.
        """
    # with open(filepath, 'rb') as f:
    #     buffer = f.read()
    # dtype = np.dtype([('x', '<f4'), ('y', '<f4'), ('z', '<f4'), ('r', 'u1'), ('g', 'u1'), ('b', 'u1'), ('_', 'u1')])
    # data = np.frombuffer(buffer, dtype=dtype)
    # points = np.vstack([data['x'], data['y'], data['z']]).T
    # colors = np.vstack([data['r'], data['g'], data['b']]).T / 255.0
    # data = np.hstack((points, colors))
    #print('reading..')
    #point_cloud=lp.read(filepath)
    points_cloud = np.load(filepath)
    #points = np.vstack((point_cloud.x, point_cloud.y, point_cloud.z)).transpose()
    #colors = np.vstack((point_cloud.red, point_cloud.green, point_cloud.blue)).transpose()
    points = points_cloud[:,:3]
    colors = points_cloud[:,3:6]
    #factor=10
    #points = points[::factor]
    #colors = colors[::factor] / 65535
    #print('Done.')
    return points, colors


def load_label(filepath: str):
    return np.load(filepath).astype(np.uint16)


def save_label(filepath: str, labels):
    with open(filepath, 'wb') as f:
        np.save(f, labels.astype(np.uint16))
