from swordi.core.objects import Resource, Quantity


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
