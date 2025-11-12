from _pytest.outcomes import Failed

from src.kdb_python.webdriver import kdb_driver

schema_json_dict = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "number"},
    },
    "required": ["name"],
    "additionalProperties": False
}

schema_json_string = """{
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "number"},
    },
    "required": ["name"],
    "additionalProperties": False
}"""

instance = {"name": "John", "age": 30}
instance2 = {"name": "John"}
instance_invalid = {"name": "John", "age": "30"}
instance_invalid2 = {"age": 30}  # 'name' is a required property
instance_invalid3 = {"name": "John", "age": 30, "job": "Engineer"}

schema_array = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "number"},
        "scores": {
            "type": "array",
            "items": {"type": "number"},
        },
    },
    "required": ["name"],
}
instance_array = {"name": "John", "age": 30, "scores": [70, 90]}


def test_case_simple():
    kdb_driver.verify_json_schemas(instance, schema_json_dict)
    kdb_driver.verify_json_schemas(instance2, schema_json_dict)
    try:
        kdb_driver.verify_json_schemas(instance2, schema_json_string)
        assert False
    except Failed:
        assert True
    try:
        kdb_driver.verify_json_schemas(instance_invalid, schema_json_dict)
        assert False
    except Failed:
        assert True
    try:
        kdb_driver.verify_json_schemas(instance_invalid2, schema_json_dict)
        assert False
    except Failed:
        assert True
    try:
        kdb_driver.verify_json_schemas(instance_invalid3, schema_json_dict)
        assert False
    except Failed:
        assert True

    kdb_driver.verify_json_schemas(instance_array, schema_array)
