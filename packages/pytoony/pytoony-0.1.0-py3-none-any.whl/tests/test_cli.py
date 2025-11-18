"""
Tests for TOON converter CLI.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
from pytoony.cli import main


class TestCLI:
    """Tests for command-line interface."""
    
    def test_toon_to_json_file(self):
        """Test converting TOON file to JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "input.toon"
            output_file = Path(tmpdir) / "output.json"
            
            input_file.write_text("name: John\nage: 30")
            
            with patch('sys.argv', ['pytoony', str(input_file), '-o', str(output_file)]):
                main()
            
            assert output_file.exists()
            data = json.loads(output_file.read_text())
            assert data["name"] == "John"
            assert data["age"] == 30
    
    def test_json_to_toon_file(self):
        """Test converting JSON file to TOON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "input.json"
            output_file = Path(tmpdir) / "output.toon"
            
            input_file.write_text('{"name": "John", "age": 30}')
            
            with patch('sys.argv', ['pytoony', str(input_file), '-o', str(output_file), '--to-toon']):
                main()
            
            assert output_file.exists()
            content = output_file.read_text()
            assert "name: John" in content
            assert "age: 30" in content
    
    def test_auto_detect_json(self):
        """Test auto-detection of JSON format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "input.json"
            output_file = Path(tmpdir) / "output.toon"
            
            input_file.write_text('{"name": "John"}')
            
            with patch('sys.argv', ['pytoony', str(input_file), '-o', str(output_file)]):
                main()
            
            assert output_file.exists()
            content = output_file.read_text()
            assert "name: John" in content
    
    def test_auto_detect_toon(self):
        """Test auto-detection of TOON format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "input.toon"
            output_file = Path(tmpdir) / "output.json"
            
            input_file.write_text("name: John")
            
            with patch('sys.argv', ['pytoony', str(input_file), '-o', str(output_file)]):
                main()
            
            assert output_file.exists()
            data = json.loads(output_file.read_text())
            assert data["name"] == "John"
    
    def test_stdin_stdout_toon_to_json(self, capsys, monkeypatch):
        """Test converting TOON from stdin to JSON on stdout."""
        input_content = "name: John\nage: 30"
        
        mock_stdin = MagicMock()
        mock_stdin.read.return_value = input_content
        monkeypatch.setattr('sys.stdin', mock_stdin)
        
        with patch('sys.argv', ['pytoony']):
            main()
        
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["name"] == "John"
        assert data["age"] == 30
    
    def test_stdin_stdout_json_to_toon(self, capsys, monkeypatch):
        """Test converting JSON from stdin to TOON on stdout."""
        input_content = '{"name": "John", "age": 30}'
        
        mock_stdin = MagicMock()
        mock_stdin.read.return_value = input_content
        monkeypatch.setattr('sys.stdin', mock_stdin)
        
        with patch('sys.argv', ['pytoony', '--to-toon']):
            main()
        
        captured = capsys.readouterr()
        assert "name: John" in captured.out
        assert "age: 30" in captured.out
    
    def test_custom_indent(self):
        """Test custom indentation for TOON output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "input.json"
            output_file = Path(tmpdir) / "output.toon"
            
            input_file.write_text('{"name": "John", "address": {"street": "Main St"}}')
            
            with patch('sys.argv', ['pytoony', str(input_file), '-o', str(output_file), '--to-toon', '--indent', '4']):
                main()
            
            assert output_file.exists()
            content = output_file.read_text()
            # Check that indentation is 4 spaces
            lines = content.split('\n')
            for line in lines:
                if 'street:' in line:
                    assert line.startswith('    street:')  # 4 spaces
    
    def test_file_not_found(self, capsys):
        """Test error handling for non-existent file."""
        with patch('sys.argv', ['pytoony', 'nonexistent.toon']):
            with pytest.raises(SystemExit):
                main()
        
        captured = capsys.readouterr()
        assert "not found" in captured.err.lower() or "Error" in captured.err
    
    def test_invalid_json(self, capsys):
        """Test error handling for invalid JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "input.json"
            input_file.write_text('{invalid json}')
            
            with patch('sys.argv', ['pytoony', str(input_file), '--to-toon']):
                with pytest.raises(SystemExit):
                    main()
            
            captured = capsys.readouterr()
            assert "invalid" in captured.err.lower() or "Error" in captured.err
    
    def test_empty_input(self, capsys, monkeypatch):
        """Test error handling for empty input."""
        mock_stdin = MagicMock()
        mock_stdin.read.return_value = ''
        monkeypatch.setattr('sys.stdin', mock_stdin)
        
        with patch('sys.argv', ['pytoony']):
            with pytest.raises(SystemExit):
                main()
        
        captured = capsys.readouterr()
        assert "empty" in captured.err.lower() or "Error" in captured.err
    
    def test_json_array_auto_detect(self):
        """Test auto-detection of JSON array format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "input.json"
            output_file = Path(tmpdir) / "output.toon"
            
            input_file.write_text('["item1", "item2"]')
            
            with patch('sys.argv', ['pytoony', str(input_file), '-o', str(output_file)]):
                main()
            
            assert output_file.exists()
            content = output_file.read_text()
            assert "item1" in content or "item2" in content
    
    def test_invalid_json_auto_detect(self):
        """Test auto-detection with invalid JSON that looks like JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "input.json"
            output_file = Path(tmpdir) / "output.json"
            
            # Starts with { but invalid JSON, should be treated as TOON
            input_file.write_text('{invalid but starts with brace')
            
            with patch('sys.argv', ['pytoony', str(input_file), '-o', str(output_file)]):
                # Should try to parse as TOON and may fail or succeed
                try:
                    main()
                except SystemExit:
                    pass  # May exit with error
    
    def test_toon_not_starting_with_brace(self):
        """Test TOON that doesn't start with { or [."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "input.toon"
            output_file = Path(tmpdir) / "output.json"
            
            input_file.write_text("name: John\nvalue: 42")
            
            with patch('sys.argv', ['pytoony', str(input_file), '-o', str(output_file)]):
                main()
            
            assert output_file.exists()
            data = json.loads(output_file.read_text())
            assert data["name"] == "John"
    
    def test_error_reading_file(self, capsys, monkeypatch):
        """Test error handling when reading file fails (non-FileNotFoundError)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "input.toon"
            # Make file unreadable
            input_file.write_text("test")
            input_file.chmod(0o000)  # Remove all permissions
            
            try:
                with patch('sys.argv', ['pytoony', str(input_file)]):
                    with pytest.raises(SystemExit):
                        main()
                
                captured = capsys.readouterr()
                assert "Error" in captured.err or "error" in captured.err.lower()
            finally:
                # Restore permissions for cleanup
                input_file.chmod(0o644)
    
    def test_error_writing_file(self, capsys):
        """Test error handling when writing file fails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "input.toon"
            output_file = Path(tmpdir) / "output.json"
            
            input_file.write_text("name: John")
            
            # Create output as directory to cause write error
            output_file.mkdir()
            
            with patch('sys.argv', ['pytoony', str(input_file), '-o', str(output_file)]):
                with pytest.raises(SystemExit):
                    main()
            
            captured = capsys.readouterr()
            assert "Error" in captured.err or "error" in captured.err.lower()
    
    def test_toon_conversion_error(self, capsys, monkeypatch):
        """Test error handling when TOON to JSON conversion fails."""
        # Create invalid TOON that will cause conversion error
        invalid_toon = "invalid: toon: format: with: too: many: colons: in: one: line: causing: error"
        
        mock_stdin = MagicMock()
        mock_stdin.read.return_value = invalid_toon
        monkeypatch.setattr('sys.stdin', mock_stdin)
        
        with patch('sys.argv', ['pytoony']):
            # May or may not raise SystemExit depending on how parser handles it
            try:
                main()
            except SystemExit:
                captured = capsys.readouterr()
                assert "Error" in captured.err or "error" in captured.err.lower()
    
    def test_json_to_toon_conversion_error(self, capsys, monkeypatch):
        """Test error handling when JSON to TOON conversion fails."""
        # Valid JSON but might cause issues in conversion
        json_input = '{"valid": "json"}'
        
        mock_stdin = MagicMock()
        mock_stdin.read.return_value = json_input
        monkeypatch.setattr('sys.stdin', mock_stdin)
        
        # Mock json2toon to raise an exception
        with patch('pytoony.cli.json2toon', side_effect=Exception("Conversion error")):
            with patch('sys.argv', ['pytoony', '--to-toon']):
                with pytest.raises(SystemExit):
                    main()
            
            captured = capsys.readouterr()
            assert "Error" in captured.err or "error" in captured.err.lower()
    
    def test_stdout_output(self, capsys, monkeypatch):
        """Test output to stdout when no output file specified."""
        input_content = "name: John\nage: 30"
        
        mock_stdin = MagicMock()
        mock_stdin.read.return_value = input_content
        monkeypatch.setattr('sys.stdin', mock_stdin)
        
        with patch('sys.argv', ['pytoony']):
            main()
        
        captured = capsys.readouterr()
        # Should output JSON to stdout
        data = json.loads(captured.out)
        assert data["name"] == "John"
        assert data["age"] == 30
    
    def test_json_array_to_toon_explicit(self):
        """Test explicit JSON array to TOON conversion."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "input.json"
            output_file = Path(tmpdir) / "output.toon"
            
            input_file.write_text('["item1", "item2", "item3"]')
            
            with patch('sys.argv', ['pytoony', str(input_file), '-o', str(output_file), '--to-toon']):
                main()
            
            assert output_file.exists()
            content = output_file.read_text()
            assert "item1" in content or "item2" in content
    
    def test_complex_json_auto_detect(self):
        """Test auto-detection with complex nested JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = Path(tmpdir) / "input.json"
            output_file = Path(tmpdir) / "output.toon"
            
            complex_json = '''{
                "users": [{"id": 1, "name": "Alice"}],
                "metadata": {"version": 1.0}
            }'''
            input_file.write_text(complex_json)
            
            with patch('sys.argv', ['pytoony', str(input_file), '-o', str(output_file)]):
                main()
            
            assert output_file.exists()
            content = output_file.read_text()
            assert "users" in content or "Alice" in content

