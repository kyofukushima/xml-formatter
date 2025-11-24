
import xml.etree.ElementTree as ET
import sys

def validate_xml(file_path):
    """
    Validates an XML file by attempting to parse it.

    Args:
        file_path (str): The path to the XML file.
    """
    try:
        tree = ET.parse(file_path)
        print(f"SUCCESS: XML file '{file_path}' is well-formed.")
    except ET.ParseError as e:
        print(f"ERROR: XML parsing failed for file '{file_path}'.")
        print(f"Error message: {e}")
    except FileNotFoundError:
        print(f"ERROR: File not found at '{file_path}'.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python validate_xml.py <path_to_xml_file>")
        sys.exit(1)
    
    xml_file = sys.argv[1]
    validate_xml(xml_file)
