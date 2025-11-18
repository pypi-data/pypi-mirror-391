from typing import List
import math

from .joints import list_of_joints_from_root
from .model import JointNodeModel, PositionModel

def distance_between_joints(jointA: JointNodeModel, jointB: JointNodeModel) -> float:
    '''Calculate the Euclidean distance between two joints based on their origin positions.'''
    dx = jointB.origin.x - jointA.origin.x
    dy = jointB.origin.y - jointA.origin.y
    dz = jointB.origin.z - jointA.origin.z
    return math.sqrt(dx * dx + dy * dy + dz * dz)

def kinematic_angles_to_position(joint: JointNodeModel, angles: List[float]) -> PositionModel:
    ''' Calculate the position of the end effector given a list of joint angles. '''
    list_of_joints = list_of_joints_from_root(joint)

    position_x = 0.0
    position_y = 0.0
    position_z = 0.0
    current_angle_index = 0

    for j in list_of_joints:
        angle = angles[current_angle_index] if current_angle_index < len(angles) else 0.0

        if j.rotation:
            rad = (angle * math.pi) / 180.0
            cosA = math.cos(rad)
            sinA = math.sin(rad)

            rotated_x = j.origin.x
            rotated_y = j.origin.y
            rotated_z = j.origin.z

            # rotation.x/y/z may be ints (0/1) or booleans
            if getattr(j.rotation, "x", 0):
                # Rotate around X axis
                rotated_y = j.origin.y * cosA - j.origin.z * sinA
                rotated_z = j.origin.y * sinA + j.origin.z * cosA
            elif getattr(j.rotation, "y", 0):
                # Rotate around Y axis
                rotated_x = j.origin.x * cosA + j.origin.z * sinA
                rotated_z = -j.origin.x * sinA + j.origin.z * cosA
            elif getattr(j.rotation, "z", 0):
                # Rotate around Z axis
                rotated_x = j.origin.x * cosA - j.origin.y * sinA
                rotated_y = j.origin.x * sinA + j.origin.y * cosA

            rotated_x += position_x
            rotated_y += position_y
            rotated_z += position_z

            position_x = rotated_x
            position_y = rotated_y
            position_z = rotated_z

        current_angle_index += 1

    return PositionModel(x=position_x, y=position_y, z=position_z)


def inverse_kinematics(
    joint: JointNodeModel,
    target: PositionModel,
    max_iterations: int = 100,
    learning_rate: float = 0.5
) -> List[float]:
    joints = list_of_joints_from_root(joint)
    angles: List[float] = [0.0 for _ in joints]

    epsilon = 0.001

    for _iter in range(max_iterations):
        current_pos = kinematic_angles_to_position(joint, angles)

        err_x = target.x - current_pos.x
        err_y = target.y - current_pos.y
        err_z = target.z - current_pos.z

        dist_error = math.sqrt(err_x * err_x + err_y * err_y + err_z * err_z)
        if dist_error < epsilon:
            break

        for i in range(len(angles)):
            saved_angle = angles[i]

            delta = 0.5  # degrees
            angles[i] = saved_angle + delta

            pos_delta = kinematic_angles_to_position(joint, angles)

            grad = (
                ((pos_delta.x - current_pos.x) * err_x +
                 (pos_delta.y - current_pos.y) * err_y +
                 (pos_delta.z - current_pos.z) * err_z) / delta
            )

            new_angle = saved_angle - learning_rate * grad

            joint_constraints = joints[i].constraint if i < len(joints) else None
            if joint_constraints:
                min_angle = joint_constraints.min
                max_angle = joint_constraints.max
                if new_angle < min_angle:
                    new_angle = min_angle
                if new_angle > max_angle:
                    new_angle = max_angle

            angles[i] = new_angle

    return angles