import json
from .model import RobotModel, RobotDescriptorModel
from .joints import create_joints_tree

def load_robot_from_file(file_path: str) -> RobotModel:
    ''' Load a robot from a JSON file and return a Robot instance. '''

    with open(file_path, 'r') as file:
        data = json.load(file)

    # Validate and parse the robot descriptor
    robot_descriptor = RobotDescriptorModel.model_validate(data)

    # Create the joints tree
    root_joint = create_joints_tree(robot_descriptor.joints)

    # Create the RobotModel
    robot_model = RobotModel(
        information=robot_descriptor.information,
        root_joint=root_joint
    )

    return robot_model