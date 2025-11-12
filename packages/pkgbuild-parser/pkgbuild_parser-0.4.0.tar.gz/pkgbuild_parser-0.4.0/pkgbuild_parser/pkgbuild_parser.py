# Licencia: MIT 2025 KevinCrrl
# Simple Python module to extract basic information directly from PKGBUILD files (not .SRCINFO)
# Versión 0.4.0
# Documentación en https://github.com/KevinCrrl/pkgbuild_parser/blob/main/README.md

from pkgbuild_parser.parser_core import *
import json

class Parser(ParserCore):
    def get_pkgname(self):
        return self.get_base("pkgname")

    def get_pkgver(self):
        return self.get_base("pkgver")

    def get_pkgrel(self):
        return self.get_base("pkgrel")

    def get_pkgdesc(self):
        return self.get_base("pkgdesc")

    def get_arch(self):
        return self.multiline("arch")

    def get_url(self):
        return self.get_base("url")

    def get_license(self):
        return self.multiline("license")

    def get_source(self):
        return self.multiline("source")

    def get_dict_base_info(self):
        return {"pkgname": self.get_pkgname(),
                "pkgver": self.get_pkgver(),
                "pkgrel": self.get_pkgrel(),
                "pkgdesc": self.get_pkgdesc(),
                "arch": self.get_arch(),
                "url": self.get_url(),
                "license": self.get_license(),
                "source": self.get_source()}

    def base_info_to_json(self):
        return json.dumps(self.get_dict_base_info(), ensure_ascii=False, indent=4)

    def write_base_info_to_json(self, json_name) -> None:
        with open(json_name, 'w', encoding="utf-8") as f:
            f.write(self.base_info_to_json())

    def get_dict_base_info_without_quotes(self):
        return {a: remove_quotes(b) for a, b in self.get_dict_base_info().items()}

    def base_info_to_json_without_quotes(self) -> str:
        return json.dumps(self.get_dict_base_info_without_quotes(), ensure_ascii=False, indent=4)

    def write_base_info_to_json_without_quotes(self, json_name):
        with open(json_name, 'w', encoding="utf-8") as f:
            f.write(self.base_info_to_json_without_quotes())

    def get_epoch(self):
        return self.none_prevention("epoch")

    def get_full_package_name(self):
        name = remove_quotes(self.get_pkgname())
        version = f"{remove_quotes(self.get_pkgver())}-{remove_quotes(self.get_pkgrel())}"
        try:
            return f"{name}-{remove_quotes(self.get_epoch())}:{version}"
        except ParserNoneTypeError:
            return f"{name}-{version}"

    def get_depends(self):
        return self.multiline("depends")

    def get_makedepends(self):
        return self.multiline("makedepends")

    def get_optdepends(self) -> list:
        return self.multiline("optdepends")

    def get_dict_optdepends(self):
        opt_dict: dict[str, str] = {}
        for optdepend in self.get_optdepends():
            optdepend = optdepend.split(":")
            opt_dict[optdepend[0]] = optdepend[1].strip()
        return opt_dict

    def optdepends_to_json(self):
        return json.dumps(self.get_dict_optdepends(), ensure_ascii=False, indent=4)

    def write_optdepends_to_json(self, json_name:str="optdepends.json") -> None:
        with open(json_name, 'w', encoding="utf-8") as f:
            f.write(self.optdepends_to_json())

    def get_options(self):
        return self.none_prevention("options")
    
    def get_checkdepends(self):
        return self.multiline("checkdepends")
