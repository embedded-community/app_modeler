from importlib.metadata import version, PackageNotFoundError


def get_version():
    try:
        return version('app_modeler')
    except PackageNotFoundError:
        # package is not installed
        return '0.0.0'


__version__ = get_version()
