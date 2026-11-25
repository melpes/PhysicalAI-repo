import csv
import math
import sys

from neutral_robot import joint_axis_world, link_poses, read_robot


def test_poses(robot):
    joints = {j["id"]: j for j in robot["joints"]}
    forearm = joints["J5"]["position"][0]
    elbow_offset = joints["J4"]["position"][2]
    straight_q3 = math.degrees(math.atan2(elbow_offset, forearm)) - 90.0
    return [
        ("home", [0, 0, 0, 0, 0, 0]),
        ("abb_max_reach", [0, 90, straight_q3, 0, 0, 0]),
        ("abb_max_height", [0, 0, straight_q3, 0, 0, 0]),
        ("abb_max_back_reach", [0, -90, straight_q3, 0, 0, 0]),
        ("abb_max_depth", [0, 150, straight_q3 + 180.0 - 150.0, 0, 0, 0]),
        ("general_1", [30, 20, -10, 40, 30, 60]),
        ("general_2", [-120, -60, 50, -200, -100, 300]),
        ("general_3", [175, 140, -170, 390, 115, -390]),
    ]


def make_robot_test_poses(neutral_path, csv_path):
    robot = read_robot(neutral_path)
    with open(csv_path, "w", newline="", encoding="utf-8") as fp:
        writer = csv.writer(fp)
        writer.writerow(["pose_id"] + [j["id"] for j in robot["joints"]] +
                        ["wc_x", "wc_y", "wc_z", "j6_axis_x", "j6_axis_y", "j6_axis_z"])
        for pose_id, q in test_poses(robot):
            poses = link_poses(robot, q)
            writer.writerow([pose_id] + [repr(float(v)) for v in q] +
                            [repr(v) for v in poses["WristCenter"][1]] +
                            [repr(v) for v in joint_axis_world(robot, poses, "J6")])


if __name__ == "__main__":
    make_robot_test_poses(sys.argv[1], sys.argv[2])
