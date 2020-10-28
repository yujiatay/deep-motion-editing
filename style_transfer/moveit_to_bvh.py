import bpy
import math
import argparse
import sys
import os

sys.path.append('/home/yujia/deep-motion-editing/style_transfer')

from franka import parse_moveit_motion_plan


scene = bpy.context.scene

# joint_axes refers to the single axis of rotation for each joint (1 to 7)
# x = 0, y = 1, z = 2
joint_axes = [1, 1, 1, 1, 1, 0, 1]
joint_names = ["Joint1", "Joint2", "Joint3", "Joint4", "Joint5", "Joint6", "Joint7"]

joints = bpy.data.objects[3].pose.bones


def clear_scene():
    for action in bpy.data.actions:
        bpy.data.actions.remove(action)

    scene.animation_data_clear()
    for obj in scene.objects:
        obj.animation_data_clear()


def move_joint(joint_id, angle_in_rad, axis=1):
    if joint_id == "Joint7":
        angle = angle_in_rad + (math.pi / 2)
    else:
        angle = angle_in_rad

    joints[joint_id].rotation_euler[axis] = angle
    joints[joint_id].keyframe_insert(data_path="rotation_euler")
    # print(joint_id, joints[joint_id], joints[joint_id].rotation_euler)


def move_joints(joint_rotations):
    for joint_id, id in zip(joint_names, [i for i in range(7)]):
        move_joint(joint_id, joint_rotations[id], joint_axes[id])


scene.frame_set(0)
neutral_pose = [-0.017792060227770554, -0.7601235411041661, 0.019782607023391807, -2.342050140544315,
                0.029840531355804868, 1.5411935298621688, 0.7534486589746342]
# neutral_pose = [0,0,0,0,0,0,0]
move_joints(neutral_pose)
#
# scene.frame_set(10)
# rotations = [2.5518125080559173e-05, -0.7849307176477147, -4.645161306537915e-05, -2.3559771465868264,
#              7.019030750043953e-05, 1.570980184533493, 0.7849546746366798]
# move_joints(rotations)
#
# scene.frame_set(20)
# rotations = [-0.10210890092890124, -0.7530542856907088, 0.0778394068956478, -2.357517548836725, -0.023321629840332522,
#              1.5410010824242582, 0.8459632720163934]
# move_joints(rotations)


def add_keyframes(traj_points):
    end_secs, end_nsecs = traj_points[-1].seconds_from_start, traj_points[-1].nanoseconds_from_start
    end_secs += end_nsecs * 1e-9
    for traj in traj_points:
        curr_secs, curr_nsecs = traj.seconds_from_start, traj.nanoseconds_from_start
        curr_secs += curr_nsecs * 1e-9
        frame = int((curr_secs / end_secs) * 100)
        print("Setting frame to ", frame)
        scene.frame_set(frame)
        move_joints(traj.positions)

    return


dir_prefix = "/home/yujia/deep-motion-editing/style_transfer/data"


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []

    parser = argparse.ArgumentParser("moveit_to_bvh")
    parser.add_argument("--file_path", type=str)
    parser.add_argument('--save_path', type=str, default=dir_prefix+'/moveit_bvh/', help='path of output bvh file')

    return parser.parse_args(argv)


if __name__ == "__main__":
    args = parse_args()
    motion_plan = parse_moveit_motion_plan(args.file_path)
    traj_points = motion_plan.trajectory_points

    clear_scene()
    add_keyframes(traj_points)

    bvh_file_path = args.save_path + os.path.basename(args.file_path).split(".")[0] + ".bvh"
    # Programmatically selects the armature to be exported
    bpy.ops.object.select_all(action='DESELECT')  # Deselect all objects
    bpy.context.view_layer.objects.active = bpy.data.objects['Franka']  # Make Franka the active object
    bpy.data.objects['Franka'].select_set(True)

    bpy.ops.export_anim.bvh(filepath=bvh_file_path)
