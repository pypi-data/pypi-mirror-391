import sys
import traceback
from pathlib import Path
from typing import Optional

from .pathutils import read_text, read_binary, copytree

PACKAGE_NAME = "pyguiadapterlite"
ASSETS_DIR_NAME = "_assets"
LOCALES_DIR_NAME = "locales"
IMAGES_DIR_NAME = "images"


def image_file(filename: str) -> str:
    return Path(IMAGES_DIR_NAME).joinpath(filename).as_posix()


def locale_file(domain: str, locale_code: str) -> str:
    return (
        Path(LOCALES_DIR_NAME)
        .joinpath(locale_code, "LC_MESSAGES", f"{domain}.mo")
        .as_posix()
    )


def read_asset_text(
    file_path: str, encoding: str = "utf-8", errors: Optional[str] = None
) -> str:

    file_path = (Path(ASSETS_DIR_NAME) / file_path.lstrip("/")).as_posix()
    return read_text(PACKAGE_NAME, file_path, encoding, errors)


def read_assets_binary(file_path: str) -> bytes:
    file_path = (Path(ASSETS_DIR_NAME) / file_path.lstrip("/")).as_posix()
    return read_binary(PACKAGE_NAME, file_path)


def copy_assets_tree(
    src_dir: str, dest_dir: str, dirs_exist_ok: bool = True, ignore=None, **kwargs
):
    src_dir = (Path(ASSETS_DIR_NAME) / src_dir.lstrip("/")).as_posix()
    copytree(
        package=PACKAGE_NAME,
        src=src_dir,
        dst=dest_dir,
        dirs_exist_ok=dirs_exist_ok,
        ignore=ignore,
        **kwargs,
    )


def load_locale_file(domain: str, locale_code: str) -> Optional[bytes]:
    locale_file_path = locale_file(domain, locale_code)
    try:
        return read_assets_binary(locale_file_path)
    except BaseException as e:
        print(
            f"failed to load builtin locale file:{locale_file_path}:{e}",
            file=sys.stderr,
        )
        traceback.print_exc()
        return None
