def convert_any(data, to="binary"):
    """Universal converter function:
    Converts numbers or strings into binary, hex, octal, ascii, etc."""
    if isinstance(data, int):
        if to == "binary":
            return bin(data)[2:]
        elif to == "hex":
            return hex(data)[2:]
        elif to == "oct":
            return oct(data)[2:]
        else:
            return f"Invalid conversion '{to}' for number."
    elif isinstance(data, str):
        if to == "binary":
            return ' '.join(format(ord(c), '08b') for c in data)
        elif to == "hex":
            return ' '.join(format(ord(c), 'x') for c in data)
        elif to == "ascii":
            return [ord(c) for c in data]
        elif to == "oct":
            return ' '.join(format(ord(c), 'o') for c in data)
        else:
            return f"Invalid conversion '{to}' for string."
    else:
        return "Unsupported data type"


def auto_convert(data):
    """Shows all available formats at once"""
    if isinstance(data, int):
        return {
            "binary": bin(data)[2:],
            "hex": hex(data)[2:],
            "oct": oct(data)[2:]
        }
    elif isinstance(data, str):
        return {
            "binary": ' '.join(format(ord(c), '08b') for c in data),
            "hex": ' '.join(format(ord(c), 'x') for c in data),
            "oct": ' '.join(format(ord(c), 'o') for c in data),
            "ascii": [ord(c) for c in data]
        }
    else:
        return {"error": "Unsupported data type"}
