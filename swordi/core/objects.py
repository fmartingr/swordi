"""
Python representations of the flavor objects.
"""
import copy
from dataclasses import dataclass, asdict, is_dataclass, fields
from typing import List, Text, _GenericAlias


@dataclass
class GameObject:
    def serialize(self):
        return asdict(self)

    @classmethod
    def deserialize(cls, serialized):
        data = copy.deepcopy(serialized)
        for field in fields(cls):
            if is_dataclass(field.type):
                data[field.name] = field.type.deserialize(data[field.name])

            if isinstance(field.type, _GenericAlias):
                if field.type._name == "List" and is_dataclass(field.type.__args__[0]):
                    gameobject_cls = field.type.__args__[0]
                    data[field.name] = [
                        gameobject_cls.deserialize(deserialized)
                        for deserialized in data[field.name]
                    ]
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


OBJECTS = {cls.__name__.lower(): cls for cls in [Resource, Building, Planet, Player]}
