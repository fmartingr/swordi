"""
Python representations of the flavor objects.
"""
import copy
from dataclasses import dataclass, asdict, is_dataclass
from typing import List, Text


@dataclass
class GameObject:
    def serialize(self):
        return asdict(self)

    @classmethod
    def deserialize(cls, serialized):
        data = copy.deepcopy(serialized)
        for field_name, field_annotation in cls.__annotations__.items():
            if is_dataclass(field_annotation):
                data[field_name] = field_annotation.deserialize(data[field_name])
        return cls(**data)


@dataclass
class Resource(GameObject):
    name: Text


@dataclass
class Building(GameObject):
    name: Text
    description: Text
    provides: List[GameObject]
    requires: List[GameObject]
    building: dict
    building_requires: List[Resource]


@dataclass
class Quantity(GameObject):
    resource: Resource
    value: int


@dataclass
class Planet(GameObject):
    pass


@dataclass
class Player(GameObject):
    name: Text
    planet: Planet


OBJECTS = {
    cls.__name__.lower(): cls for cls in [
        Resource, Building, Planet, Player
    ]
}
