import os
import util
import tqdm
import open3d
import argparse

CUBE_SIDE_LEN = 1.0

open3d.set_verbosity_level(open3d.utility.VerbosityLevel.Error)

parser = argparse.ArgumentParser(description='F-score evaluation')
parser.add_argument('--pr_path', type=str, required=True)
parser.add_argument('--out_path', type=str)
parser.add_argument('--th', type=float)
args = parser.parse_args()

if args.out_path is None:
    out_path = "fscore"
else:
    out_path = args.out_path
os.mkdir(out_path)

if args.th is None:
    threshold_list = [CUBE_SIDE_LEN/200, CUBE_SIDE_LEN/100,
                      CUBE_SIDE_LEN/50, CUBE_SIDE_LEN/20,
                      CUBE_SIDE_LEN/10, CUBE_SIDE_LEN/5]
else:
    threshold_list = [args.th]

class_list = util.get_class_list()
for cat in class_list:
    os.mkdir(os.path.join(out_path, cat))
    model_list = util.get_class_models(cat)

    f_f = open(os.path.join(out_path, cat, "fscore.txt"), "w")
    f_p = open(os.path.join(out_path, cat, "precision.txt"), "w")
    f_r = open(os.path.join(out_path, cat, "recall.txt"), "w")

    for i in tqdm.tqdm(range(len(model_list))):
        model = model_list[i]
        for v in range(util.VIEW_COUNT):
            gt = open3d.read_point_cloud(os.path.join(util.POINTS_PATH, cat, model, str(v) + ".ply"))
            pr = open3d.read_point_cloud(os.path.join(args.pr_path, cat, model, str(v) + ".ply"))
            
            f_f.write(model + "_" + str(v))
            f_p.write(model + "_" + str(v))
            f_r.write(model + "_" + str(v))
            
            for th in threshold_list:
                f, p, r = util.calculate_fscore(gt, pr, th=th)
                f_f.write(" " + str(f))
                f_p.write(" " + str(p))
                f_r.write(" " + str(r))
            
            f_f.write("\n")
            f_p.write("\n")
            f_r.write("\n")
    
    f_f.close()
    f_p.close()
    f_r.close()
