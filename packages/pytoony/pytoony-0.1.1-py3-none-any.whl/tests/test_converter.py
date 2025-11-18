"""
Tests for TOON converter.
"""

import json
from pytoony import toon2json, json2toon, Toon


class TestToonToJson:
    """Tests for TOON to JSON conversion."""

    def test_simple_key_value(self):
        """Test simple key-value pairs."""
        toon = "name: John\nage: 30"
        result = toon2json(toon)
        data = json.loads(result)
        assert data["name"] == "John"
        assert data["age"] == 30

    def test_nested_object(self):
        """Test nested objects."""
        toon = """name: John
address:
    street: Main St
    city: New York"""
        result = toon2json(toon)
        data = json.loads(result)
        assert data["name"] == "John"
        assert data["address"]["street"] == "Main St"
        assert data["address"]["city"] == "New York"

    def test_tabular_array(self):
        """Test tabular array format."""
        toon = """users[2]{id,name}:
    1,Alice
    2,Bob"""
        result = toon2json(toon)
        data = json.loads(result)
        assert len(data["users"]) == 2
        assert data["users"][0]["id"] == 1
        assert data["users"][0]["name"] == "Alice"
        assert data["users"][1]["id"] == 2
        assert data["users"][1]["name"] == "Bob"

    def test_simple_array(self):
        """Test simple array format."""
        toon = """tags:
    python
    json
    toon"""
        result = toon2json(toon)
        data = json.loads(result)
        assert data["tags"] == ["python", "json", "toon"]

    def test_mixed_types(self):
        """Test different data types."""
        toon = """name: John
age: 30
active: true
score: 95.5
email: null"""
        result = toon2json(toon)
        data = json.loads(result)
        assert data["name"] == "John"
        assert data["age"] == 30
        assert data["active"] is True
        assert data["score"] == 95.5
        assert data["email"] is None

    def test_comments(self):
        """Test that comments are ignored."""
        toon = """# This is a comment
name: John
# Another comment
age: 30"""
        result = toon2json(toon)
        data = json.loads(result)
        assert "name" in data
        assert "age" in data
        assert len(data) == 2

    def test_empty_lines(self):
        """Test that empty lines are ignored."""
        toon = """name: John

age: 30


city: NY"""
        result = toon2json(toon)
        data = json.loads(result)
        assert len(data) == 3


class TestJsonToToon:
    """Tests for JSON to TOON conversion."""

    def test_simple_key_value(self):
        """Test simple key-value pairs."""
        json_str = '{"name": "John", "age": 30}'
        result = json2toon(json_str)
        assert "name: John" in result
        assert "age: 30" in result

    def test_nested_object(self):
        """Test nested objects."""
        json_str = (
            '{"name": "John", "address": {"street": "Main St", "city": "New York"}}'
        )
        result = json2toon(json_str)
        assert "name: John" in result
        assert "address:" in result
        assert "street: Main St" in result
        assert "city: New York" in result

    def test_tabular_array(self):
        """Test tabular array format generation."""
        json_str = '{"users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]}'
        result = json2toon(json_str)
        assert "users[2]{id,name}:" in result
        assert "1,Alice" in result
        assert "2,Bob" in result

    def test_simple_array(self):
        """Test simple array format."""
        json_str = '{"tags": ["python", "json", "toon"]}'
        result = json2toon(json_str)
        assert "tags:" in result
        assert "python" in result
        assert "json" in result
        assert "toon" in result

    def test_mixed_types(self):
        """Test different data types."""
        json_str = '{"name": "John", "age": 30, "active": true, "score": 95.5, "email": null}'
        result = json2toon(json_str)
        assert "name: John" in result
        assert "age: 30" in result
        assert "active: true" in result
        assert "score: 95.5" in result
        assert "email: null" in result


class TestRoundTrip:
    """Tests for round-trip conversion (JSON -> TOON -> JSON)."""

    def test_simple_round_trip(self):
        """Test simple round-trip conversion."""
        original = '{"name": "John", "age": 30}'
        toon = json2toon(original)
        back = toon2json(toon)
        original_data = json.loads(original)
        back_data = json.loads(back)
        assert original_data == back_data

    def test_nested_round_trip(self):
        """Test nested object round-trip."""
        original = '{"name": "John", "address": {"street": "Main St", "city": "NY"}}'
        toon = json2toon(original)
        back = toon2json(toon)
        original_data = json.loads(original)
        back_data = json.loads(back)
        assert original_data == back_data

    def test_tabular_array_round_trip(self):
        """Test tabular array round-trip."""
        original = '{"users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]}'
        toon = json2toon(original)
        back = toon2json(toon)
        original_data = json.loads(original)
        back_data = json.loads(back)
        assert original_data == back_data

    def test_simple_array_round_trip(self):
        """Test simple array round-trip."""
        original = '{"tags": ["python", "json", "toon"]}'
        toon = json2toon(original)
        back = toon2json(toon)
        original_data = json.loads(original)
        back_data = json.loads(back)
        assert original_data == back_data

    def test_complex_round_trip(self):
        """Test complex nested structure round-trip."""
        original = """{
            "name": "John",
            "age": 30,
            "address": {
                "street": "123 Main St",
                "city": "NY"
            },
            "users": [
                {"id": 1, "name": "Alice"},
                {"id": 2, "name": "Bob"}
            ],
            "tags": ["python", "json"]
        }"""
        toon = json2toon(original)
        back = toon2json(toon)
        original_data = json.loads(original)
        back_data = json.loads(back)
        assert original_data == back_data


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_object(self):
        """Test empty object."""
        toon = ""
        result = toon2json(toon)
        data = json.loads(result)
        assert data == {}

    def test_string_with_special_chars(self):
        """Test strings with special characters."""
        toon = 'name: "John: Doe"'
        result = toon2json(toon)
        data = json.loads(result)
        assert data["name"] == "John: Doe"

    def test_numbers(self):
        """Test integer and float numbers."""
        toon = "int: 42\nfloat: 3.14"
        result = toon2json(toon)
        data = json.loads(result)
        assert data["int"] == 42
        assert data["float"] == 3.14
        assert isinstance(data["int"], int)
        assert isinstance(data["float"], float)

    def test_boolean_values(self):
        """Test boolean values."""
        toon = "active: true\ninactive: false"
        result = toon2json(toon)
        data = json.loads(result)
        assert data["active"] is True
        assert data["inactive"] is False


class TestToonClass:
    """Tests for Toon class encode/decode methods."""

    def test_encode_json_to_toon(self):
        """Test Toon.encode() converts JSON to TOON."""
        json_str = '{"name": "John", "age": 30}'
        result = Toon.encode(json_str)
        assert "name: John" in result
        assert "age: 30" in result

    def test_decode_toon_to_json(self):
        """Test Toon.decode() converts TOON to JSON."""
        toon = "name: John\nage: 30"
        result = Toon.decode(toon)
        data = json.loads(result)
        assert data["name"] == "John"
        assert data["age"] == 30

    def test_encode_with_custom_indent(self):
        """Test Toon.encode() with custom indentation."""
        json_str = '{"name": "John", "address": {"street": "Main St"}}'
        result = Toon.encode(json_str, indent=4)
        lines = result.split("\n")
        for line in lines:
            if "street:" in line:
                assert line.startswith("    street:")  # 4 spaces

    def test_round_trip_with_toon_class(self):
        """Test round-trip conversion using Toon class."""
        original = '{"name": "John", "age": 30}'
        toon = Toon.encode(original)
        back = Toon.decode(toon)
        original_data = json.loads(original)
        back_data = json.loads(back)
        assert original_data == back_data
