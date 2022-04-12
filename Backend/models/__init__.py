import importlib
import pkgutil


def import_module():
    for finder, name, _ in pkgutil.walk_packages(['']):
        try:
            importlib.import_module("{}".format(name))
        except Exception as e:
            print("Cannot import module {}".format(name), e)


# __all__ = ['import_module']

__all__ = ['diabetes', 'qcsi']
