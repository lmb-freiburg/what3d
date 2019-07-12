import os
import open3d
import numpy as np
import copy
import matplotlib.pyplot as plt
from .path_config import *

CLASSES_FILE_PATH = os.path.join(BASE_DATA_PATH, "classes.txt")
LISTS_PATH = os.path.join(BASE_DATA_PATH, "lists")
BINVOX_PATH = os.path.join(BASE_DATA_PATH, "binvox")
POINTS_PATH = os.path.join(BASE_DATA_PATH, "points")
VIEW_COUNT = 5

def read_txt_file(file_path):
    with open(file_path) as f:
        lines = f.readlines()
        lines = [l.rstrip() for l in lines]
    return lines

def get_class_list():
    lines = read_txt_file(CLASSES_FILE_PATH)
    lines = [l.split(" ")[0] for l in lines]
    return lines

def get_class_models(category, mode="test"):
    model_list = read_txt_file(os.path.join(LISTS_PATH, category, mode + ".txt"))
    return model_list

def calculate_fscore(gt, pr, th=0.01):
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

def assign_colors(pc, dist, cmap_name='hot'):
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

def visualize_distance(gt, pr, max_distance=None):
    s = copy.deepcopy(gt)
    t = copy.deepcopy(pr)

    d1 = open3d.compute_point_cloud_to_point_cloud_distance(s, t)
    d2 = open3d.compute_point_cloud_to_point_cloud_distance(t, s)

    if max_distance is None:
        max_distance = np.max([np.max(np.asarray(d1)), np.max(np.asarray(d2))])
        print("MAX distance: " + str(max_distance))

    precision_pc = assign_colors(s, np.asarray(d1) / max_distance)
    open3d.draw_geometries([precision_pc])

    recall_pc = assign_colors(t, np.asarray(d2) / max_distance)
    open3d.draw_geometries([recall_pc])
