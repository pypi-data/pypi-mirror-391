import atexit
import shutil
import signal
import sys
from pathlib import Path
from threading import Event
from typing import Optional, Callable, Union


class ExitHook(object):
    def __init__(
        self,
        once: bool = True,
        hook_uncaught_exception: bool = True,
        wrap_old_excepthook: bool = True,
        hook_signals: bool = True,
        wrap_old_signal_handlers: bool = True,
    ):
        self._once = once
        self._hook_uncaught_exception = hook_uncaught_exception
        self._wrap_old_excepthook = wrap_old_excepthook
        self._hook_signals = hook_signals
        self._wrap_old_signal_handlers = wrap_old_signal_handlers

        self._callbacks = set()

    def try_hook(self, exit_callback: Callable):
        callback_id = id(exit_callback)
        if callback_id in self._callbacks:
            raise ValueError("exit callback already registered")
        self._callbacks.add(callback_id)

        is_called = Event()
        called_once = self._once

        def wrapped_callback():
            nonlocal is_called
            if called_once and is_called.is_set():
                return
            try:
                exit_callback()
            except Exception as e:
                print(
                    f"exit callback {exit_callback} raised exception: {e}",
                    file=sys.stderr,
                )
            is_called.set()

        atexit.register(wrapped_callback)

        if self._hook_uncaught_exception:
            self._do_hook_uncaught_exception(wrapped_callback)

        if self._hook_signals:
            self._do_hook_signals(wrapped_callback)

    def _do_hook_uncaught_exception(self, callback: Callable):
        old_excepthook = sys.excepthook

        def wrapped_excepthook(type_, value, traceback):
            try:
                callback()
            except Exception as e:
                print(
                    f"exit callback {callback} raised exception: {e}",
                    file=sys.stderr,
                )

            if callable(old_excepthook) and self._wrap_old_excepthook:
                old_excepthook(type_, value, traceback)
            else:
                sys.__excepthook__(type_, value, traceback)

        sys.excepthook = wrapped_excepthook

    def _do_hook_signals(self, callback: Callable):
        old_signal_handlers = {
            signal.SIGINT: signal.getsignal(signal.SIGINT),
            signal.SIGTERM: signal.getsignal(signal.SIGTERM),
        }

        def wrapped_signal_handler(signum, frame):
            try:
                callback()
            except Exception as e:
                print(
                    f"exit callback {callback} raised exception: {e}",
                    file=sys.stderr,
                )
            old_handler = old_signal_handlers.get(signum, None)
            if callable(old_handler) and self._wrap_old_signal_handlers:
                return old_handler(signum, frame)

            sys.exit(128 + signum)

        signal.signal(signal.SIGINT, wrapped_signal_handler)
        signal.signal(signal.SIGTERM, wrapped_signal_handler)


def _dir_path(package: str, path: str) -> Optional[Path]:
    pkg = sys.modules.get(package, None)
    if pkg and hasattr(pkg, "__path__") and pkg.__path__:
        return Path(pkg.__path__[0]) / path
    return None


def read(
    package: str,
    file_path: str,
    binary: bool,
    encoding: str = "utf-8",
    errors: Optional[str] = None,
) -> Union[str, bytes]:
    try:
        from importlib.resources import as_file, files

        with as_file(files(package).joinpath(file_path)) as p:
            p = Path(p)
            if binary:
                return p.read_bytes()
            else:
                return p.read_text(encoding=encoding, errors=errors)
    except ImportError:
        try:
            import pkg_resources

            p = Path(pkg_resources.resource_filename(package, file_path))
            if binary:
                return p.read_bytes()
            else:
                return p.read_text(encoding=encoding, errors=errors)
        except FileNotFoundError as e:
            raise e
        except BaseException:
            p = _dir_path(package, file_path)
            if not p:
                raise RuntimeError(f"cannot find file {file_path} in package {package}")
            if binary:
                return p.read_bytes()
            else:
                return p.read_text(encoding=encoding, errors=errors)


def read_text(
    package: str, file_path: str, encoding: str = "utf-8", errors: Optional[str] = None
) -> str:
    return read(package, file_path, False, encoding=encoding, errors=errors)


def read_binary(package: str, file_path: str) -> bytes:
    return read(package, file_path, True)


def copytree(
    package: str,
    src: str,
    dst: str,
    symlinks: bool = False,
    ignore=None,
    copy_function=shutil.copy2,
    ignore_dangling_symlinks=False,
    dirs_exist_ok=True,
):
    dst_path = Path(dst)

    try:
        from importlib.resources import as_file, files

        with as_file(files(package).joinpath(src)) as p:
            src_path = Path(p)
            shutil.copytree(
                src=src_path,
                dst=dst_path,
                symlinks=symlinks,
                ignore=ignore,
                copy_function=copy_function,
                ignore_dangling_symlinks=ignore_dangling_symlinks,
                dirs_exist_ok=dirs_exist_ok,
            )

    except ImportError:
        try:
            import pkg_resources

            src_path = Path(pkg_resources.resource_filename(package, src))
            if not src_path.exists():
                raise FileNotFoundError(f"directory not found: {src_path.as_posix()}")
            shutil.copytree(
                src=src_path,
                dst=dst_path,
                symlinks=symlinks,
                ignore=ignore,
                copy_function=copy_function,
                ignore_dangling_symlinks=ignore_dangling_symlinks,
                dirs_exist_ok=dirs_exist_ok,
            )
        except FileNotFoundError as e:
            raise e
        except BaseException:
            src_path = _dir_path(package, src)
            if not p:
                raise RuntimeError(f"cannot find file {p} in package {package}")
            shutil.copytree(
                src=src_path,
                dst=dst_path,
                symlinks=symlinks,
                ignore=ignore,
                copy_function=copy_function,
                ignore_dangling_symlinks=ignore_dangling_symlinks,
                dirs_exist_ok=dirs_exist_ok,
            )
