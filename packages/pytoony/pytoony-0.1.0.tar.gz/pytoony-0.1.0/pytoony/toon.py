"""
TOON converter class with encode/decode methods.
"""

from .converter import toon2json, json2toon


class Toon:
    """
    TOON converter class with encode/decode methods.
    
    - encode: Convert JSON to TOON format
    - decode: Convert TOON format to JSON
    """
    
    @staticmethod
    def encode(json_content: str, indent: int = 2) -> str:
        """
        Encode JSON string to TOON format.
        
        Args:
            json_content: JSON string to encode
            indent: Number of spaces for indentation (default: 2)
            
        Returns:
            String in TOON format
        """
        return json2toon(json_content, indent=indent)
    
    @staticmethod
    def decode(toon_content: str) -> str:
        """
        Decode TOON format string to JSON.
        
        Args:
            toon_content: String in TOON format
            
        Returns:
            JSON string representation
        """
        return toon2json(toon_content)

