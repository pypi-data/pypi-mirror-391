from adam.commands.command import Command
from adam.config import Config
from adam.repl_state import ReplState, RequiredState
from adam.sql.sql_completer import SqlCompleter
from adam.utils import log2
from adam.utils_athena import Athena

class ExportSql(Command):
    COMMAND = '&select'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(ExportSql, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)
        if not hasattr(self, 'schema_dirty'):
            self.schema_dirty = True

    def command(self):
        return ExportSql.COMMAND

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
                log2('Use a SQL statement.')
            else:
                log2('* SQL statement is missing.')

                Command.display_help()

            return 'command-missing'

        query = ' '.join(args)

        Athena.run_query(f'select {query}', database=f'export_{state.export_session}')

        return state

    def completion(self, state: ReplState):
        if not state.export_session:
            return {}

        db = f'export_{state.export_session}'

        if self.schema_dirty:
            Config().wait_log(f'Inspecting export database schema...')
            self.schema_dirty = False
            # warm up the caches first time when l: drive is accessed
            Athena.table_names(database=db, function='export')
            Athena.column_names(database=db, function='export')
            Athena.column_names(partition_cols_only=True, database=db, function='export')

        return {ExportSql.COMMAND: SqlCompleter(
            lambda: Athena.table_names(database=db, function='export'),
            dml='select',
            columns=lambda table: Athena.column_names(database=db, function='export'),
            variant='athena'
        )}

    def help(self, _: ReplState):
        return f'{ExportSql.COMMAND} <sql statement>\t run queries on export database'