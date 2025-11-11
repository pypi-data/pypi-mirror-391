import atexit
from contextlib import ExitStack

try:  # Python 3.9+
    from importlib import resources as importlib_resources  # type: ignore
except ImportError:  # pragma: no cover -- fallback for very old interpreters
    import importlib_resources  # type: ignore

_exit_stack = ExitStack()
atexit.register(_exit_stack.close)


def _enter_context(manager) -> str:
    return str(_exit_stack.enter_context(manager))


def resource_filename(package: str, resource: str) -> str:
    """
    Return a filesystem path for a package resource with broad compatibility.

    Preference order:
        1. importlib.resources.files / as_file  (Py>=3.9 or backport)
        2. importlib_resources.path             (Py3.8 backport API)
        3. pkg_resources.resource_filename      (setuptools)
    """

    files = getattr(importlib_resources, "files", None)
    files_available = callable(files)
    if files_available:
        ref = files(package).joinpath(resource)
        as_file = getattr(importlib_resources, "as_file", None)
        if callable(as_file):
            try:
                return _enter_context(as_file(ref))
            except IsADirectoryError:
                # Py<3.12 표준 라이브러리는 디렉터리를 지원하지 않으므로
                # 아래 폴백(importlib_resources.path → pkg_resources)으로 진행합니다.
                pass
        # as_file가 없거나 디렉터리를 처리하지 못한 경우 importlib_resources.path로 위임
        path_cm = getattr(importlib_resources, "path", None)
        if callable(path_cm):
            try:
                return _enter_context(path_cm(package, resource))
            except (IsADirectoryError, ValueError):
                pass
    else:
        path_cm = getattr(importlib_resources, "path", None)
        if callable(path_cm):
            try:
                return _enter_context(path_cm(package, resource))
            except (IsADirectoryError, ValueError):
                pass

    try:
        import pkg_resources  # type: ignore
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "Unable to locate resource utilities; install 'importlib-resources' "
            "for Python 3.8 or 'setuptools' to provide pkg_resources."
        ) from exc

    return pkg_resources.resource_filename(package, resource)


__all__ = ["resource_filename"]

