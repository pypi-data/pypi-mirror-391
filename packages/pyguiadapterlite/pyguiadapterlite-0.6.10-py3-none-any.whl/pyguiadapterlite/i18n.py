import gettext
import io
import locale
import os
import platform
import subprocess
import sys
import traceback
from gettext import GNUTranslations
from pathlib import Path
from typing import Optional

from pyguiadapterlite.assets import LOCALES_DIR_NAME, copy_assets_tree, load_locale_file

_DEFAULT_LOCALE_DIR = ""
_DEFAULT_DOMAIN = "pyguiadapterlite"
_DEFAULT_LOCALE = "en_US"

ENV_AUTO_EXPORT = "PYGUIADAPTERLITE_EXPORT_LOCALES"
ENV_LOCALE = "PYGUIADAPTERLITE_LOCALE"
ENV_LOCALE_DIR = "PYGUIADAPTERLITE_LOCALE_DIR"
ENV_DOMAIN = "PYGUIADAPTERLITE_DOMAIN"


class SystemLocaleDetector(object):
    _system = platform.system().lower()

    def __init__(self):
        raise NotImplementedError("This class is not intended to be instantiated")

    @classmethod
    def detect(cls, default: str = _DEFAULT_LOCALE) -> str:
        if cls._system == "linux":
            return cls._detect_linux() or default
        elif cls._system == "darwin":
            return cls._detect_macos() or default
        elif cls._system == "windows":
            return cls._detect_windows() or default
        else:
            return cls._detect_other() or default

    @classmethod
    def detect_language_code(
        cls, fallback_locale: str = _DEFAULT_LOCALE
    ) -> Optional[str]:
        locale_str = cls.detect(fallback_locale).strip()
        if locale_str and "_" in locale_str:
            return locale_str.split("_")[0]
        return locale_str or None

    @classmethod
    def detect_country_code(
        cls, fallback_locale: str = _DEFAULT_LOCALE
    ) -> Optional[str]:
        locale_str = cls.detect(fallback_locale)
        if locale_str and "_" in locale_str:
            return locale_str.split("_")[1]
        return None

    @staticmethod
    def _detect_linux() -> Optional[str]:
        # 检查多个环境变量
        env_vars = ["LC_ALL", "LC_CTYPE", "LANG", "LANGUAGE"]
        for var in env_vars:
            value = os.environ.get(var)
            if value and value != "C" and value != "POSIX":
                return value
        # 使用locale命令
        try:
            result = subprocess.run(["locale"], capture_output=True, text=True)
            if result.returncode != 0:
                return None
            for line in result.stdout.split("\n"):
                line = line.strip()
                if line.startswith("LANG=") or line.startswith("LC_CTYPE="):
                    return line.split("=")[1].strip().strip('"')
            return None
        except BaseException as e:
            print(f"failed to detect system locale on Linux: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return None

    @staticmethod
    def _detect_macos() -> Optional[str]:
        try:
            result = subprocess.run(
                ["defaults", "read", "-g", "AppleLocale"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except BaseException as e:
            print(
                f"failed to detect system locale on macOS: {e}",
            )
            traceback.print_exc(file=sys.stderr)
            return None

    @staticmethod
    def _detect_windows() -> Optional[str]:
        try:
            import ctypes

            # noinspection PyUnresolvedReferences
            lcid = ctypes.windll.kernel32.GetUserDefaultLCID()
            return locale.windows_locale.get(lcid, None)
        except BaseException as e:
            print(f"failed to detect system locale on Windows: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return None

    @staticmethod
    def _detect_other() -> Optional[str]:
        try:
            return locale.getdefaultlocale()[0] or None
        except BaseException as e:
            print(
                f"failed to detect system locale on other system: {e}", file=sys.stderr
            )
            traceback.print_exc(file=sys.stderr)
            return None


def detect_system_locale(fallback: str = _DEFAULT_LOCALE) -> str:
    return SystemLocaleDetector.detect(fallback)


def detect_system_language_code(
    fallback_locale: str = _DEFAULT_LOCALE,
) -> Optional[str]:
    return SystemLocaleDetector.detect_language_code(fallback_locale)


def detect_system_country_code(fallback_locale: str = _DEFAULT_LOCALE) -> Optional[str]:
    return SystemLocaleDetector.detect_country_code(fallback_locale)


class I18N:
    def __init__(
        self,
        domain: Optional[str] = None,
        localedir: Optional[str] = None,
        locale_code: Optional[str] = None,
    ):

        self._domain: str = ""
        self._localedir: str = ""
        self._current_locale: str = ""
        self._translation: Optional[gettext.NullTranslations] = None

        self.set_locale(locale_code, domain, localedir)

    def get_locale_dir(self) -> str:
        return self._localedir

    def set_locale(
        self,
        locale_code: Optional[str] = None,
        domain: Optional[str] = None,
        localedir: Optional[str] = None,
    ) -> None:
        domain = (domain or "").strip()
        if not domain:
            domain = self.get_domain_from_env().strip()
        self._domain = domain
        if not self._domain:
            raise ValueError("unable to determine domain")

        locale_code = (locale_code or "").strip()
        if not locale_code:
            locale_code = self.get_locale_code_from_env().strip()
        if locale_code.lower() == "auto" or locale_code == "":
            locale_code = detect_system_locale()
        self._current_locale = locale_code

        localedir = (localedir or "").strip()
        if not localedir:
            localedir = self.get_locales_dir_from_env().strip()
        locale_file = None
        if not localedir:
            # 如果没有指定locales目录，则使用内置的locales中查找匹配domain和locale_code的翻译文件
            self._localedir = ""
            locale_file = self.load_builtin_locale_file(domain, locale_code)
        else:
            # 如果指定了locales目录，则将该目录作为locales文件查找目录

            # 如果locales目录不存在，则创建目录
            if not os.path.isdir(localedir):
                os.makedirs(localedir, exist_ok=True)

            # 如果locales目录不为空，且要求自动导出，则导出内置locales文件到该目录
            export_locales = self.should_export_locales()
            if export_locales and not os.listdir(localedir):
                self.export_builtin_locales(localedir, overwrite=True)
                # print(f"exporting built-in locales to {localedir}")
            self._localedir = localedir

        try:
            # 如果指定了locales目录，则将该目录作为查找目录
            if self._localedir:
                self._translation = gettext.translation(
                    self._domain,
                    localedir=self._localedir,
                    languages=[self._current_locale],
                    fallback=True,
                )
            else:
                # 如果没有指定locales目录，则使用内置的locales中查找匹配domain和locale_code的翻译文件
                # 如果没有匹配到对应的翻译文件，则使用空翻译
                if not locale_file:
                    self._translation = gettext.NullTranslations()
                else:
                    # 加载翻译文件
                    self._translation = GNUTranslations(fp=locale_file)
            # self._translation.install()
        except BaseException as e:
            # 如果找不到翻译文件或者加载翻译文件出错，则使用空翻译
            print(
                f"failed to create translation for {self._domain}@{self._current_locale}': {e}",
                file=sys.stderr,
            )
            self._translation = gettext.NullTranslations()
            # self._translation.install()

    def gettext(self, message: str) -> str:
        if self._translation:
            return self._translation.gettext(message)
        return message

    def ngettext(self, singular: str, plural: str, n: int) -> str:
        if self._translation:
            return self._translation.ngettext(singular, plural, n)
        return singular if n == 1 else plural

    # noinspection PyMethodMayBeStatic
    def load_builtin_locale_file(
        self, domain: str, locale_code: str
    ) -> Optional[io.BytesIO]:
        """加载内部locale文件"""
        locale_file_data = load_locale_file(domain, locale_code)
        if not locale_file_data:
            return None
        return io.BytesIO(locale_file_data)

    # noinspection PyMethodMayBeStatic
    def export_builtin_locales(self, target_dir: str, overwrite: bool = False) -> None:
        """导出locales文件到指定目录"""
        target_dir = Path(target_dir)
        if target_dir.is_dir() and not overwrite:
            return
        target_dir.mkdir(parents=True, exist_ok=True)
        copy_assets_tree(LOCALES_DIR_NAME, target_dir.as_posix(), dirs_exist_ok=True)

    # noinspection PyMethodMayBeStatic
    def get_domain_from_env(self, default: str = _DEFAULT_DOMAIN) -> str:
        return os.environ.get(ENV_DOMAIN, default)

    # noinspection PyMethodMayBeStatic
    def get_locale_code_from_env(self, default: str = "") -> str:
        return os.environ.get(ENV_LOCALE, default).strip()

    # noinspection PyMethodMayBeStatic
    def get_locales_dir_from_env(self, default: str = _DEFAULT_LOCALE_DIR) -> str:
        return os.environ.get(ENV_LOCALE_DIR, default).strip()

    # noinspection PyMethodMayBeStatic
    def should_export_locales(self) -> bool:
        return os.environ.get(ENV_AUTO_EXPORT, "false").lower() == "true"

    # 简化方法别名
    def _(self, message: str) -> str:
        """gettext 的简写形式"""
        return self.gettext(message)

    def _n(self, singular: str, plural: str, n: int) -> str:
        """ngettext 的简写形式"""
        return self.ngettext(singular, plural, n)


# 创建全局实例
_default_i18n = I18N()


def tr_(message: str) -> str:
    """翻译字符串"""
    return _default_i18n.gettext(message)


def ntr_(singular: str, plural: str, n: int) -> str:
    """翻译单复数字符串"""
    return _default_i18n.ngettext(singular, plural, n)
