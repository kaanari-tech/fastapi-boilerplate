import os
import importlib
from typing import Iterator
import types
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Handlers:
    handlers_base_path = ('backend', 'app')
    ignored = ('__init__.py', '__pycache__','crud','schema','service')
    paths = ('admin/api/v1', 'client/api/v1', 'mentor/api/v1', 'company/api/v1')
    # include_dirs = ["v1"]

    @classmethod
    def __all_module_paths(cls) -> list:
        module_paths = []
        
        for path in cls.paths:
            handlers_path = f"{os.path.join(os.getcwd(), *cls.handlers_base_path)}/{path}/".replace("backend/backend","backend")
            for root, dirs, files in os.walk(handlers_path):
                for file in files:
                    if file.endswith('.py') and file not in cls.ignored:
                        relative_path = os.path.relpath(os.path.join(root, file), handlers_path)
                        module_paths.append(os.path.join(path, relative_path))
                
            
                    

        return module_paths

    @classmethod
    def __module_namespace(cls, module_path: str) -> str:
        module_path = module_path.replace(os.sep, '.').replace('.py', '')
        namespace = '%s.%s' % ('.'.join(cls.handlers_base_path), module_path)
        return namespace

    @classmethod
    def iterator(cls) -> Iterator[types.ModuleType]:
        for module_path in cls.__all_module_paths():
            module_name = cls.__module_namespace(module_path)
            try:
                handler = importlib.import_module(module_name)
                yield handler
            except Exception as e:
                logger.error(f"Erreur lors de l'importation de {module_name}: {e}")

    @classmethod
    def modules(cls) -> map:
        return map(
            lambda module_path: cls.__module_namespace(module_path), cls.__all_module_paths()
        )
