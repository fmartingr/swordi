from dataclasses import dataclass
from typing import List

from swordi.core.objects import Resource, Quantity, GameObject


@dataclass
class GameObjectWithNestedList(GameObject):
    resources: List[Resource]


def test_gameobject_serializes_ok():
    resource = Resource(name="Test")
    serialized = resource.serialize()
    assert isinstance(serialized, dict)


def test_gameobject_serializes_nested_ok():
    resource = Resource("test")
    quantity = Quantity(value=1, resource=resource)
    serialized = quantity.serialize()
    assert isinstance(serialized, dict)
    assert isinstance(serialized['resource'], dict)
    assert serialized['resource'] == resource.serialize()


def test_gameobject_serializes_nested_list_ok():
    resource1 = Resource(name="Test1")
    resource2 = Resource(name="Test2")
    resources = GameObjectWithNestedList(resources=[resource1, resource2])
    serialized = resources.serialize()
    assert isinstance(serialized['resources'], list)


def test_gameobject_deserializes_ok():
    resource = Resource("test")
    serialized = resource.serialize()
    deserialized = Resource.deserialize(serialized)
    assert deserialized.serialize() == serialized


def test_gameobject_deserializes_nested_ok():
    resource = Resource("test")
    quantity = Quantity(value=1, resource=resource)
    serialized = quantity.serialize()
    deserialized = Quantity.deserialize(serialized)
    assert deserialized.serialize() == serialized
    assert isinstance(deserialized.resource, Resource)


def test_gameobject_deserializes_nested_list_ok():
    resource1 = Resource(name="Test1")
    resource2 = Resource(name="Test2")
    resources = GameObjectWithNestedList(resources=[resource1, resource2])
    serialized = resources.serialize()
    deserialized = GameObjectWithNestedList.deserialize(serialized)
    assert deserialized.serialize() == serialized
    assert isinstance(deserialized.resources, list)
    assert isinstance(deserialized.resources[0], Resource)
