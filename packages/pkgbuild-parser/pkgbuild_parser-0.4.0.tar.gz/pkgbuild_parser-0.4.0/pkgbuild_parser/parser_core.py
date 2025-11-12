# Licencia: MIT 2025 KevinCrrl
# Módulo sencillo para obtener datos básicos de un PKGBUILD.

class ParserFileError(Exception):
    pass

class ParserKeyError(Exception):
    pass

class ParserNoneTypeError(Exception):
    pass

def remove_quotes(string) -> list[str] | str:
    if type(string) == list:
        return string
    new_string = ""
    for char in string:
        if char != "'" and char != '"':
            new_string += char
    return new_string

class ParserCore:
    def __init__(self, filename: str):
        try:
            with open(filename, 'r', encoding="utf-8") as f:
                self.lines = [line.strip() for line in f]
        except FileNotFoundError as exc:
            raise ParserFileError(f"PKGBUILD file '{filename}' not found") from exc

    def multiline(self, key: str) -> list[str]:
        list_of_lines: list[str] = []
        key_found: bool = False
        for line in self.lines: 
            # line example: optdepends=('package: desc' # comment
            # or
            # line example: optdepends=('one_package: one_desc') # comment
            line: str = remove_quotes(line.split("#")[0].strip()) # new line example: optdepends=(one_package: one_desc) or optdepends=(package: desc
            if not key_found and key in line:
                list_of_lines.append(line.split("=")[1].lstrip("(").rstrip(" ")) # new line example: one_package: one_desc) or package: desc
                key_found = True
            if key_found and ")" in list_of_lines[0]:
                list_of_lines[0] = list_of_lines[0].rstrip(")")
                break
            if key_found and ")" not in line and key not in line:
                list_of_lines.append(line.split("#")[0].strip())
            if key_found and ")" in line:
                list_of_lines.append(line.strip().rstrip(")"))
                break
        list_of_lines = list(filter(None, list_of_lines))
        if list_of_lines:
            return list_of_lines
        raise ParserKeyError(f"{key} not found in PKGBUILD")
    
    def get_base(self, key: str):
        "Basic function to obtain simple values."
        try:
            for line in self.lines:
                if key in line:
                    # line example: pkgdesc=("desc here") # packager's comment
                    # line.split("=")[1].strip() example: ("desc here") # packager's comment
                    # line.split("=")[1].strip().split("#")[0].lstrip("(").rstrip(") ") example: "package info"
                    return line.split("=")[1].strip().split("#")[0].lstrip("(").rstrip(") ")
        except IndexError as exc:
            raise ParserKeyError(f"{key} not found in PKGBUILD") from exc
        except AttributeError as exc:
            raise ParserNoneTypeError(f"'NoneType' returned when trying to get {key}") from exc

    def none_prevention(self, key:str):
        prevention = self.get_base(key)
        if not prevention is None:
            return prevention
        raise ParserNoneTypeError(f"'NoneType' returned when trying to get {key}")
