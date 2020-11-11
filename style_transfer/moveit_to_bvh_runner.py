import subprocess
import argparse
import os


def convert_moveit_data_dir(data_dir):
    data_files = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.endswith('.txt')]
    for filepath in data_files:
        subprocess.call(["blender",
                         "./data/Franka_armature.blend",
                         "--background",
                         "--python", "moveit_to_bvh.py",
                         "--",
                         "--file_path", filepath])


def parse_args():
    parser = argparse.ArgumentParser("moveit_to_bvh_runner")
    parser.add_argument("--dir", type=str, default="./data/motion_plans/")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    convert_moveit_data_dir(args.dir)
