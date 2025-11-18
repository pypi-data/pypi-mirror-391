from typing import Dict, Optional, List

from .model import (
    JointDescModel,
    JointNodeModel,
    AngleModel,
    PositionModel,
    ConstraintModel,
    RobotModel,
)

def create_joints_tree(joints_descriptor: Dict[str, JointDescModel]) -> JointNodeModel:
    """
    Create a tree structure of JointNodeModel from the robot description.
    Returns the root JointNodeModel.
    """
    # Find root joint
    root_name: Optional[str] = None
    root_desc: Optional[JointDescModel] = None
    for name, desc in joints_descriptor.items():
        if getattr(desc, "is_root", False):
            root_name = name
            root_desc = desc
            break

    if root_name is None or root_desc is None:
        raise ValueError("No root joint found in robot description")

    # Create a JointNodeModel for each joint in the description
    joint_nodes: Dict[str, JointNodeModel] = {}
    for joint_name, joint_desc in joints_descriptor.items():
        constraint = (
            joint_desc.constraint
            if joint_desc.constraint is not None
            else ConstraintModel(min=-180.0, max=180.0)
        )
        origin = (
            joint_desc.origin
            if joint_desc.origin is not None
            else PositionModel(x=0.0, y=0.0, z=0.0)
        )
        joint_nodes[joint_name] = JointNodeModel(
            name=joint_name,
            angle=AngleModel(angle=0.0),
            constraint=constraint,
            origin=origin,
            rotation=joint_desc.rotation,
            parent=None,
            children=[],
        )

    # Link the JointNodeModel instances together based on linked_to
    for joint_name, node in joint_nodes.items():
        linked_to = joints_descriptor[joint_name].linked_to
        if linked_to:
            for linked_name in linked_to:
                linked_node = joint_nodes.get(linked_name)
                if linked_node is None:
                    raise ValueError(f"Linked joint {linked_name} not found in description")
                linked_node.parent = node
                node.children.append(linked_node)

    # Return the root node
    return joint_nodes[root_name]


def find_joint_by_name(robot: RobotModel, name: str) -> Optional[JointNodeModel]:
    """
    Find a joint by name in the robot's joint hierarchy.
    """

    def recursive_search(joint: JointNodeModel) -> Optional[JointNodeModel]:
        if joint.name == name:
            return joint
        for child in joint.children:
            res = recursive_search(child)
            if res:
                return res
        return None

    return recursive_search(robot.root_joint)


def list_of_joints_from_root(joint: JointNodeModel) -> List[JointNodeModel]:
    """
    Get the list of joints from the root to the specified joint.
    """
    joints: List[JointNodeModel] = []
    current: Optional[JointNodeModel] = joint
    while current is not None:
        joints.append(current)
        current = current.parent
    joints.reverse()
    return joints