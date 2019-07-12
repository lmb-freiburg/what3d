import open3d
import argparse
import util

open3d.set_verbosity_level(open3d.utility.VerbosityLevel.Error)

parser = argparse.ArgumentParser(description='Precision/recall visualization')
parser.add_argument('--gt', type=str, required=True)
parser.add_argument('--pr', type=str, required=True)
parser.add_argument('--th', type=float)
args = parser.parse_args()

gt = open3d.read_point_cloud(args.gt)
pr = open3d.read_point_cloud(args.pr)

if args.th is not None:
    f, p, r = util.calculate_fscore(gt, pr, args.th)
    print("F-score: %f, Precision: %f, Recall: %f" % (f, p, r))
util.visualize_distance(gt, pr, max_distance=args.th)
