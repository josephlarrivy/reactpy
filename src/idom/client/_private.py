import re
import shutil
from pathlib import Path
from typing import List, Tuple

from idom.config import IDOM_CLIENT_BUILD_DIR

HERE = Path(__file__).parent


APP_DIR = HERE / "app"
BACKUP_BUILD_DIR = APP_DIR / "build"


if not IDOM_CLIENT_BUILD_DIR.get().exists():  # pragma: no cover
    shutil.copytree(BACKUP_BUILD_DIR, IDOM_CLIENT_BUILD_DIR.get(), symlinks=True)


def build_dir() -> Path:
    return IDOM_CLIENT_BUILD_DIR.get()


def web_modules_dir() -> Path:
    return build_dir() / "_snowpack" / "pkg"


def restore_build_dir_from_backup() -> None:
    target = build_dir()
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(BACKUP_BUILD_DIR, target, symlinks=True)


def replace_build_dir(source: Path) -> None:
    target = build_dir()
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target, symlinks=True)


def get_package_name(pkg: str) -> str:
    return split_package_name_and_version(pkg)[0]


def split_package_name_and_version(pkg: str) -> Tuple[str, str]:
    at_count = pkg.count("@")
    if pkg.startswith("@"):
        if at_count == 1:
            return pkg, ""
        else:
            name, version = pkg[1:].split("@", 1)
            return ("@" + name), version
    elif at_count:
        name, version = pkg.split("@", 1)
        return name, version
    else:
        return pkg, ""


_JS_MODULE_EXPORT_PATTERN = re.compile(
    r";?\s*export\s*{([0-9a-zA-Z_$\s,]*)}\s*;", re.MULTILINE
)
_JS_VAR = r"[a-zA-Z_$][0-9a-zA-Z_$]*"
_JS_MODULE_EXPORT_NAME_PATTERN = re.compile(
    fr";?\s*export\s+({_JS_VAR})\s+{_JS_VAR}\s*;", re.MULTILINE
)
_JS_MODULE_EXPORT_FUNC_PATTERN = re.compile(
    fr";?\s*export\s+function\s+({_JS_VAR})\s*\(.*?", re.MULTILINE
)


def find_js_module_exports_in_source(content: str) -> List[str]:
    names: List[str] = []
    for match in _JS_MODULE_EXPORT_PATTERN.findall(content):
        for export in match.split(","):
            export_parts = export.split(" as ", 1)
            names.append(export_parts[-1].strip())
    names.extend(_JS_MODULE_EXPORT_FUNC_PATTERN.findall(content))
    names.extend(_JS_MODULE_EXPORT_NAME_PATTERN.findall(content))
    return names
