from adam.commands.command import Command
from adam.commands.export.export_sql import ExportSql
from adam.config import Config
from adam.repl_state import ReplState, RequiredState
from adam.utils import log2
from adam.utils_athena import Athena

class ExportUse(Command):
    COMMAND = '&use'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(ExportUse, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)
        self.schema_dirty = True

    def command(self):
        return ExportUse.COMMAND

    def required(self):
        return RequiredState.CLUSTER_OR_POD

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        state, args = self.apply_state(args, state)
        if not self.validate_state(state):
            return state

        if not args:
            if state.in_repl:
                log2('Specify database to use.')
            else:
                log2('* database is missing.')

                Command.display_help()

            return 'command-missing'

        state.export_session = args[0].replace('export_', '') if args[0].startswith('export_') else args[0]

        return state

    def completion(self, state: ReplState):
        if ExportSql().schema_dirty:
            Config().wait_log(f'Inspecting export databases...')
            ExportSql().schema_dirty = False
            # warm up the caches first time when l: drive is accessed
            Athena.database_names()

        return super().completion(state, {n: None for n in Athena.database_names()})

    def help(self, _: ReplState):
        return f'{ExportUse.COMMAND} <sql statement>\t run queries on export database'