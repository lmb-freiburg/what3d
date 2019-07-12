import os
import shapenet
import argparse

def get_point_cloud(pc_path):
    pc = open3d.read_point_cloud(pc_path)
    return np.asarray(pc.points)

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

parser = argparse.ArgumentParser(description='F-score evaluation')
parser.add_argument('--pr_path', type=str, required=True)
parser.add_argument('--out_path', type=str)
args = parser.parse_args()

if args.out_path is None:
    out_path = "fscore"
    os.mkdir(out_path)

class_list = shapenet.get_class_list()
for cat in class_list:
    os.mkdir(os.path.join(out_path, cat))
    model_list = shapenet.get_class_models(cat)

    f_f = open(os.path.join(out_path, cat, "fscore.txt"), "w")
    f_p = open(os.path.join(out_path, cat, "precision.txt"), "w")
    f_r = open(os.path.join(out_path, cat, "recall.txt"), "w")

    for model in model_list:
        for v in range(shapenet.VIEW_COUNT):
            gt = get_point_cloud(os.path.join(shapenet.POINTS_PATH, cat, model, str(v) + ".ply"))
            pr = get_point_cloud(os.path.join(args.pr_path, cat, model, str(v) + ".ply"))
            f, p, r = calculate_fscore(gt, pr)
    
    f_f.close()
    f_p.close()
    f_r.close()
