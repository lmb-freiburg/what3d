import os
import open3d
import numpy as np

BASE_DATA_PATH = "."
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

def get_voxel_grid(category, shape_id):
    return None
