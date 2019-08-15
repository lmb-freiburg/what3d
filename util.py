import os
import typing
import open3d
import mcubes
import numpy as np
import copy
import matplotlib.pyplot as plt
from .path_config import *


CLASSES_FILE_PATH = os.path.join(BASE_DATA_PATH, "classes.txt")
LISTS_PATH = os.path.join(BASE_DATA_PATH, "lists")
BINVOX_PATH = os.path.join(BASE_DATA_PATH, "binvox")
POINTS_PATH = os.path.join(BASE_DATA_PATH, "points")
VIEW_COUNT = 5


def read_txt_file(file_path: str) -> list:
    '''Reads a .txt file and returns a list of lines.'''
    with open(file_path) as f:
        lines = f.readlines()
        lines = [l.rstrip() for l in lines]
    return lines


def get_class_list() -> list:
    '''Returns the list of ShapeNet class names.'''
    lines = read_txt_file(CLASSES_FILE_PATH)
    lines = [l.split(" ")[0] for l in lines]
    return lines


def get_class_models(category: str, mode: str="test") -> list:
    '''Returns the list of shape IDs for a class from the corresponding subset.'''
    model_list = read_txt_file(os.path.join(LISTS_PATH, category, mode + ".txt"))
    return model_list


def voxel_grid_to_mesh(vox_grid: np.array) -> open3d.geometry.TriangleMesh:
    '''Converts a voxel grid represented as a numpy array into a mesh.'''
    sp = vox_grid.shape
    if len(sp) != 3 or sp[0] != sp[1] or \
       sp[1] != sp[2] or sp[0] == 0:
        raise ValueError("Only non-empty cubic 3D grids are supported.")
    padded_grid = np.pad(vox_grid, ((1,1),(1,1),(1,1)), 'constant')
    m_vert, m_tri = mcubes.marching_cubes(padded_grid, 0)
    m_vert = m_vert / (padded_grid.shape[0] - 1)
    out_mesh = open3d.geometry.TriangleMesh()
    out_mesh.vertices = open3d.utility.Vector3dVector(m_vert)
    out_mesh.triangles = open3d.utility.Vector3iVector(m_tri)
    return out_mesh


def calculate_fscore(gt: open3d.geometry.PointCloud, pr: open3d.geometry.PointCloud, th: float=0.01) -> typing.Tuple[float, float, float]:
    '''Calculates the F-score between two point clouds with the corresponding threshold value.'''
    d1 = open3d.compute_point_cloud_to_point_cloud_distance(gt, pr)
    d2 = open3d.compute_point_cloud_to_point_cloud_distance(pr, gt)
    
    if len(d1) and len(d2):
        recall = float(sum(d < th for d in d2)) / float(len(d2))
        precision = float(sum(d < th for d in d1)) / float(len(d1))

        if recall+precision > 0:
            fscore = 2 * recall * precision / (recall + precision)
        else:
            fscore = 0
    else:
        fscore = 0
        precision = 0
        recall = 0

    return fscore, precision, recall


def assign_colors(pc: open3d.geometry.PointCloud, dist: np.array, cmap_name: str='hot') -> open3d.geometry.PointCloud:
    '''Assigns per-point colors to a point cloud given a distance array.'''
    cmap = plt.cm.get_cmap(cmap_name)
    points = np.asarray(pc.points)
    colors = np.zeros(points.shape)

    ind = 0
    for pt in points:
        colors[ind, :] = cmap(1-dist[ind])[0:3]
        ind += 1

    out_pc = open3d.PointCloud()
    out_pc.points = open3d.Vector3dVector(points)
    out_pc.colors = open3d.Vector3dVector(colors)

    return out_pc


def visualize_distance(gt: open3d.geometry.PointCloud, pr: open3d.geometry.PointCloud, max_distance: float=None) -> None:
    '''Displays precision and recall based on the F-score between two point clouds.'''
    s = copy.deepcopy(gt)
    t = copy.deepcopy(pr)

    d1 = open3d.compute_point_cloud_to_point_cloud_distance(s, t)
    d2 = open3d.compute_point_cloud_to_point_cloud_distance(t, s)

    if max_distance is None:
        max_distance = np.max([np.max(np.asarray(d1)), np.max(np.asarray(d2))])
        print("MAX distance: " + str(max_distance))

    precision_pc = assign_colors(s, np.asarray(d1) / max_distance)
    print("Showing precision...")
    open3d.draw_open3d.geometrymetries([precision_pc])

    recall_pc = assign_colors(t, np.asarray(d2) / max_distance)
    print("Showing recall...")
    open3d.draw_open3d.geometrymetries([recall_pc])
