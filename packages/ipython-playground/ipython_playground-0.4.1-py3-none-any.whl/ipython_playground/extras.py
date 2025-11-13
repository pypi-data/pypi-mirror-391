# ruff: noqa: F401

import inspect
import pkgutil
import sys
from types import ModuleType
from typing import Optional

from .utils import log


def load_app_modules() -> dict:
    """Attempt to import common app modules and return them in a dict."""
    modules = {}
    try:
        import app.models

        modules["app.models"] = app.models
    except ImportError:
        log.warning("Could not import app.models")

    try:
        import app.commands

        modules["app.commands"] = app.commands
    except ImportError:
        log.warning("Could not import app.commands")

    try:
        import app.jobs

        modules["app.jobs"] = app.jobs
    except ImportError:
        log.warning("Could not import app.jobs")

    return modules


def get_default_module_imports():
    """Get the default list of modules to import with their aliases and options."""
    return [
        # Built-in modules - always available
        {"module": "json"},
        {"module": "re"},
        
        # Additional built-in and common imports
        {"module": "datetime", "extra_imports": [
            {"from": "datetime", "import": "datetime"}
        ]},
        {"module": "whenever", "extra_imports": [
            {"from": "whenever", "import": "ZonedDateTime"}
        ], "log_warning": True},
        
        # External libraries with aliases
        {"module": "funcy", "alias": "f"},
        {"module": "funcy_pipe", "alias": "fp", "log_warning": True},
        {"module": "sqlalchemy", "alias": "sa", "log_warning": True},
        
        # Special handling for sqlmodel - imports additional symbols
        {
            "module": "sqlmodel", 
            "alias": "sm", 
            "log_warning": True,
            "extra_imports": [
                {"from": "sqlmodel", "import": "SQLModel"},
                {"from": "sqlmodel", "import": "select"}
            ]
        }
    ]


def load_modules_for_ipython(module_imports=None) -> dict:
    """Load list of common modules for use in ipython sessions and return them as a dict so they can be appended to the global namespace
    
    Args:
        module_imports: Optional list of module import configurations. If None, uses default list.
                       Each item should be a dict with keys:
                       - module: module name to import
                       - alias: name to use in namespace (optional, defaults to module name)
                       - log_warning: whether to log warning on import failure (optional, defaults to False)
                       - extra_imports: list of additional imports from the module (optional)
    """

    modules = {}

    # Load app modules
    modules.update(load_app_modules())

    if module_imports is None:
        module_imports = get_default_module_imports()

    for import_config in module_imports:
        module_name = import_config["module"]
        alias = import_config.get("alias", module_name)
        log_warning = import_config.get("log_warning", False)
        extra_imports = import_config.get("extra_imports", [])

        try:
            imported_module = __import__(module_name)
            modules[alias] = imported_module

            # Handle extra imports from the module
            for extra_import in extra_imports:
                try:
                    from_module = extra_import["from"]
                    import_name = extra_import["import"]
                    import_alias = extra_import.get("alias", import_name)
                    
                    # Use importlib for from imports
                    import importlib
                    mod = importlib.import_module(from_module)
                    modules[import_alias] = getattr(mod, import_name)
                except (ImportError, AttributeError) as e:
                    if log_warning:
                        log.warning(f"Could not import {import_name} from {from_module}: {e}")

        except ImportError:
            if log_warning:
                log.warning(f"Could not import {module_name}")

    return modules


def find_all_sqlmodels(module: ModuleType):
    """Import all model classes from module and submodules into current namespace."""

    try:
        from sqlmodel import SQLModel
    except ImportError:
        log.warning("Could not find SQLModel, skipping model discovery")
        return {}

    log.debug(f"Starting model import from module: {module.__name__}")
    model_classes = {}

    # Walk through all submodules
    for loader, module_name, is_pkg in pkgutil.walk_packages(module.__path__):
        full_name = f"{module.__name__}.{module_name}"
        log.debug(f"Importing submodule: {full_name}")

        # Check if module is already imported
        if full_name in sys.modules:
            submodule = sys.modules[full_name]
        else:
            log.warning(f"Module not found in sys.modules, not importing: {full_name}")
            continue

        # Get all classes from module
        for name, obj in inspect.getmembers(submodule):
            if inspect.isclass(obj) and issubclass(obj, SQLModel) and obj != SQLModel:
                log.debug(f"Found model class: {name}")
                model_classes[name] = obj

    log.debug(f"Completed model import. Found {len(model_classes)} models")
    return model_classes


def all(*, database_url: Optional[str] = None):
    from .database import get_database_url, setup_database_session
    from .redis import setup_redis

    modules = load_modules_for_ipython()

    if "app.models" in modules:
        modules = modules | find_all_sqlmodels(modules["app.models"])

    if not database_url:
        database_url = get_database_url()

    if database_url:
        modules = modules | setup_database_session(database_url)

    # Add redis client if available
    modules = modules | setup_redis()

    return modules
