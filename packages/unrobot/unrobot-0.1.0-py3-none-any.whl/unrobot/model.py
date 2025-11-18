from pydantic import BaseModel, Field, model_validator
from typing import Optional

#########################################
## Basic types
#########################################

class AngleModel(BaseModel):
    angle: float = Field(ge=-180.0, le=180.0)  # Angle in degrees between -360 and 360

class PositionModel(BaseModel):
    x: float
    y: float
    z: float

class RotationAxisModel(BaseModel):
    x: int = Field(ge=0, le=1)
    y: int = Field(ge=0, le=1)
    z: int = Field(ge=0, le=1)

class ConstraintModel(BaseModel):
    min: float = Field(ge=-180.0, le=180.0)
    max: float = Field(ge=-180.0, le=180.0)

    @model_validator(mode='after')
    def check_constraints(self):
        if self.min > self.max:
            raise ValueError('Minimum angle must be less than or equal to maximum angle')
        return self
    
class InformationModel(BaseModel):
    name: str
    version: float | None = 1.0
    description: str | None = None
    author: str | None = None

#########################################
## Description of the robot (In file)
#########################################

class JointDescModel(BaseModel):
    id: int = Field(ge=0)
    is_root: bool = False
    constraint: ConstraintModel | None = ConstraintModel(min=-180.0, max=180.0)
    rotation: RotationAxisModel | None = None
    origin: PositionModel = PositionModel(x=0.0, y=0.0, z=0.0)
    linked_to: list[str] | None = None

class RobotDescriptorModel(BaseModel):
    information: InformationModel
    joints: dict[str, JointDescModel]

#########################################
## Robot structure in memory
#########################################

class JointNodeModel(BaseModel):
    name: str
    angle: AngleModel
    constraint: ConstraintModel
    origin: PositionModel
    rotation: Optional[RotationAxisModel] = None
    parent: Optional['JointNodeModel'] = None
    children: list['JointNodeModel'] = []

class RobotModel(BaseModel):
    information: InformationModel
    root_joint: JointNodeModel