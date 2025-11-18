import importlib


def import_string(dotted_path):
    # Lifted from Django, to avoid a dependency if using Varanus outside Django.
    module_path, class_name = dotted_path.rsplit(".", 1)
    try:
        return getattr(importlib.import_module(module_path), class_name)
    except AttributeError as err:
        raise ImportError(f"`{module_path}` does not define `{class_name}`") from err
