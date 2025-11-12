from .command import Command
from ..environment import Environment
from ..error import InvalidModuleNameError
import importlib


class Import(Command):
    def __init__(self, path: str):
        self.path = path

    def execute(self, env: Environment) -> None:
        module_names = self.path.split(".")
        for name in module_names:
            if not name.isalnum():
                raise InvalidModuleNameError(name)
        module_name = module_names[0]
        env.context.define(module_name, importlib.import_module(module_name))
