import boto3

from adam.commands.command import Command
from adam.commands.export.export import ing
from adam.config import Config
from adam.repl_state import ReplState, RequiredState
from adam.utils import log2
from adam.utils_athena import Athena

class RemoveExportDatabases(Command):
    COMMAND = '&rmdbs'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(RemoveExportDatabases, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)
        self.schema_dirty = True

    def command(self):
        return RemoveExportDatabases.COMMAND

    def required(self):
        return RequiredState.CLUSTER_OR_POD

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        state, args = self.apply_state(args, state)
        if not self.validate_state(state):
            return state

        dbs = Athena.database_names('export_')
        def drop_all_exports():
            for db in dbs:
                query = f'DROP DATABASE {db} CASCADE'
                if Config().is_debug():
                    log2(query)
                Athena.query(query)

        if Config().is_debug():
            drop_all_exports()
        else:
            ing(f'Droping {len(dbs)} databases', drop_all_exports)

        def delete_s3_folder():
            s3 = boto3.resource('s3')
            bucket = s3.Bucket('c3.ops--qing')
            bucket.objects.filter(Prefix='export/').delete()

        if Config().is_debug():
            delete_s3_folder()
        else:
            ing(f'Deleting s3 folder: export', delete_s3_folder)

        return state

    def completion(self, state: ReplState):
        return super().completion(state)

    def help(self, _: ReplState):
        return f'{RemoveExportDatabases.COMMAND}\t remove all export databases'