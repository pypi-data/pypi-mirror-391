from unrobot.robot import load_robot_from_file
from unrobot.model import PositionModel, RobotModel
from unrobot.kinematics import distance_between_joints, kinematic_angles_to_position

def test_load_robot_from_file():
    robot = load_robot_from_file('./tests/robot.json')
    assert isinstance(robot, RobotModel)
    assert robot.information.name == "robot_arm"
    assert robot.root_joint.name == "base_link"
    assert len(robot.root_joint.children) == 1 # base_link has one child joint "BrasHorizontal"
    print("Robot loaded successfully with root joint:", robot.root_joint.name)

def test_distance_between_joints():
    robot = load_robot_from_file('./tests/robot.json')
    jointA = robot.root_joint
    jointB = jointA.children[0]  # Assuming there is at least one child

    dist = distance_between_joints(jointA, jointB)
    assert dist >= 0.0  # Distance should be non-negative
    print(f"Distance between {jointA.name} and {jointB.name}: {dist}")

def test_kinematic_angles_to_position():
    robot = load_robot_from_file('./tests/robot.json')
    joint = robot.root_joint
    angles = [30.0, 45.0]  # Example angles for the joints

    position = kinematic_angles_to_position(joint, angles)
    assert isinstance(position, PositionModel)
    assert hasattr(position, 'x')
    assert hasattr(position, 'y')
    assert hasattr(position, 'z')
    print(f"End effector position: x={position.x}, y={position.y}, z={position.z}")