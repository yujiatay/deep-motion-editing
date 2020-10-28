import argparse
import os

import numpy as np
# from torch.utils.data import Dataset, DataLoader


class TrajectoryPoint:
    def __init__(self, positions, velocities, accelerations, effort, secs_from_start, nsecs_from_start):
        """
        positions : ndarray of radians (joint angles)
        """
        self.positions = positions
        self.velocities = velocities
        self.accelerations = accelerations
        self.effort = effort
        self.seconds_from_start = secs_from_start
        self.nanoseconds_from_start = nsecs_from_start


class MoveitMotionPlan:
    def __init__(self, name, joint_names, traj_points):
        self.name = os.path.basename(name)
        self.joint_names = joint_names
        self.trajectory_points = traj_points
        self.num_points = len(traj_points)

    def __repr__(self):
        return f'<Motion plan: {self.name}>'

    def get_motion(self, num_points):
        return np.array([self.trajectory_points[i].positions for i in range(0, num_points)])


# class MoveitDataset(Dataset):
#     def __init__(self, config, subset_name, data_dir):
#         super(MoveitDataset, self).__init__()
#
#         self.device = config.device  # CUDA or CPU
#
#         data_files = [os.path.join(data_dir, file) for file in os.listdir(data_dir) if file.endswith('.txt')]
#         self.motion_plans = [parse_moveit_motion_plan(file) for file in data_files]
#         self.min_points = min([motion.num_points for motion in self.motion_plans])
#         # TODO: HARDCODED!!!!!!!!!!
#         self.min_points = 10
#
#         self.len = len(self.motion_plans)
#         # TODO: Add label to motion plans when parsing
#         self.labels = [0] * self.len
#
#     def __len__(self):
#         return self.len
#
#     def __getitem__(self, index):
#         data = {
#             "label": self.labels[index],  # used in model.py
#             "meta": [],
#             "content": self.motion_plans[index].get_motion(self.min_points),  # used in model.py
#             # TODO: Find proper data for style
#             "style3d": self.motion_plans[(index + 1) % self.len].get_motion(self.min_points),
#             "contentraw": self.motion_plans[index].get_motion(self.min_points),  # used in model.py
#             "style3draw": self.motion_plans[(index + 1) % self.len].get_motion(self.min_points),  # used in model.py
#             # TODO: This should be a different data with same style
#             "same_style3d": self.motion_plans[index].get_motion(self.min_points),
#             # TODO: This should be a different data with different style
#             "diff_style3d": self.motion_plans[(index + 2) % self.len].get_motion(self.min_points),
#             "foot_contact": [],
#         }
#         # TODO: Does data need to be normalized?
#         return data
#
#
# def get_franka_dataloader(config, subset_name, data_dir, shuffle=True):
#     dataset = MoveitDataset(config, subset_name, data_dir)
#     return DataLoader(dataset,
#                       batch_size=config.batch_size if subset_name == 'train' else 1,
#                       shuffle=shuffle,
#                       num_workers=0)


def parse_moveit_motion_plan(filename: str) -> MoveitMotionPlan:
    def convert_to_numpy_array(arr):
        empty_arr = ['']
        if arr == empty_arr:
            return np.array([])
        return np.array(arr).astype(np.double)

    with open(filename) as f:
        # Motion plan only begins from line 20 onwards
        for _ in range(19):
            next(f)

        joint_names = f.readline().strip()
        joint_names += ' ' + f.readline().strip()
        joint_names = joint_names[14:-1].split(', ')
        next(f)

        traj_points = []
        while f.readline().strip() == '-':
            positions = f.readline().strip()[12:-1].split(', ')
            velocities = f.readline().strip()[13:-1].split(', ')
            accelerations = f.readline().strip()[len('accelerations: ['):-1].split(', ')
            effort = f.readline().strip()[len('effort: ['):-1].split(', ')
            next(f)
            seconds = f.readline().strip()[len('secs: ')]
            nanoseconds = f.readline().strip()[len('nsecs:'):].strip()

            positions = convert_to_numpy_array(positions)
            velocities = convert_to_numpy_array(velocities)
            accelerations = convert_to_numpy_array(accelerations)
            effort = convert_to_numpy_array(effort)
            seconds = int(seconds)
            nanoseconds = int(nanoseconds)

            traj_point = TrajectoryPoint(positions, velocities, accelerations, effort, seconds, nanoseconds)
            traj_points.append(traj_point)
        motion_plan = MoveitMotionPlan(filename, joint_names, traj_points)
    return motion_plan


def parse_args():
    parser = argparse.ArgumentParser("franka")
    parser.add_argument("--filename", type=str, default="./data/moveit_train/input1.txt")
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    parse_moveit_motion_plan(args.filename)
