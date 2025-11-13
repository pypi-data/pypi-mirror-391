from datetime import datetime
import io
import re
from typing import Callable
import boto3

from adam.commands.command import Command
from adam.commands.cql.cql_utils import cassandra_table_names, run_cql
from adam.commands.export.export_sql import ExportSql
from adam.config import Config
from adam.repl_state import ReplState, RequiredState
from adam.sql.sql_completer import SqlCompleter
from adam.utils import lines_to_tabular, log, log2
from adam.utils_athena import Athena
from adam.utils_k8s.cassandra_nodes import CassandraNodes
from adam.utils_k8s.pods import Pods
from adam.utils_k8s.statefulsets import StatefulSets

class ExportTable(Command):
    COMMAND = 'export'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(ExportTable, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return ExportTable.COMMAND

    def required(self):
        return RequiredState.POD

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        state, args = self.apply_state(args, state)
        if not self.validate_state(state):
            return state

        if not args:
            def show_tables():
                log(lines_to_tabular(cassandra_table_names(state), separator=','))

            if state.in_repl:
                log2('Table is required.')
                log2()
                log2('Tables:')
                show_tables()
            else:
                log2('* Table is missing.')
                show_tables()

                Command.display_help()

            return 'command-missing'

        table = args[0]
        columns = Config().get('cql.export.columns', f'id')

        table_and_cols = ' '.join(args)
        p = re.compile('(.*?)\((.*)\)')
        match = p.match(table_and_cols)
        if match:
            table = match.group(1)
            columns = match.group(2)

        athena_table = table
        if '.' in athena_table:
            athena_table = athena_table.split('.')[-1]

        temp_dir = Config().get('cql.export.temp_dir', '/c3/cassandra/tmp')
        create_db = not state.export_session
        if create_db:
            state.export_session = datetime.now().strftime("%Y%m%d%H%M%S")
        ts = state.export_session
        db = f'export_{state.export_session}'

        CassandraNodes.exec(state.pod, state.namespace, f'mkdir -p {temp_dir}/{ts}', show_out=True, shell='bash')
        csv_file = f'{temp_dir}/{ts}/{table}.csv'
        succeeded = False
        try:
            if Config().is_debug():
                run_cql(state, f"COPY {table}({columns}) TO '{csv_file}' WITH HEADER = TRUE", show_out=True)
            else:
                ing(f'Dumping table {table}',
                    lambda: run_cql(state, f"COPY {table}({columns}) TO '{csv_file}' WITH HEADER = TRUE", show_out=False))

            header = []
            def upload_to_s3():
                bytes = Pods.read_file(state.pod, 'cassandra', state.namespace, csv_file)
                header.append(GeneratorStream(bytes).readline().decode("utf-8").strip('\r\n'))

                bytes = Pods.read_file(state.pod, 'cassandra', state.namespace, csv_file)

                s3 = boto3.client('s3')
                s3.upload_fileobj(GeneratorStream(bytes), 'c3.ops--qing', f'export/{ts}/{athena_table}/{table}.csv')

            ing(f'Uploading to S3', upload_to_s3)

            def create_schema():
                query = f'CREATE DATABASE IF NOT EXISTS {db};'
                if Config().is_debug():
                    log2(query)
                Athena.query(query, 'default')

                query = f'DROP TABLE IF EXISTS {athena_table};'
                if Config().is_debug():
                    log2(query)
                Athena.query(query, db)

                columns = ', '.join([f'{h.strip(" ")} string' for h in header[0].split(',')])
                query = f'CREATE EXTERNAL TABLE IF NOT EXISTS {athena_table}(\n' + \
                        f'    {columns})\n' + \
                         "ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'\n" + \
                         'WITH SERDEPROPERTIES (\n' + \
                         '    "separatorChar" = ",",\n' + \
                         '    "quoteChar"     = "\\"")\n' + \
                        f"LOCATION 's3://c3.ops--qing/export/{ts}/{athena_table}'\n" + \
                         'TBLPROPERTIES ("skip.header.line.count"="1");'
                if Config().is_debug():
                    log2(query)
                Athena.query(query, db)

            if Config().is_debug():
                create_schema()
            else:
                ing(f"Creating database {db}" if create_db else f"Creating table {athena_table}", create_schema)

            succeeded = True
        except Exception as e:
            log2(e)
        finally:
            if Config().is_debug():
                CassandraNodes.exec(state.pod, state.namespace, f'rm -rf {csv_file}', show_out=True, shell='bash')
            else:
                ing('Cleaning up temporary files',
                    lambda: CassandraNodes.exec(state.pod, state.namespace, f'rm -rf {csv_file}', show_out=False, shell='bash'))

        if succeeded:
            ExportSql().schema_dirty = True
            Athena.clear_cache()

            query = f'select * from {athena_table} limit 10'
            log2(query)
            Athena.run_query(query, db)

        return state

    def completion(self, state: ReplState):
        def sc():
            return SqlCompleter(
                lambda: cassandra_table_names(state),
                dml='export',
                # columns=lambda table: Athena.column_names(database=db, function='export'),
                variant='cql'
            )

        dict = {}
        if state.pod:
            dict = {ExportTable.COMMAND: sc()}

        if state.sts:
            return dict | \
                {f'@{p}': {ExportTable.COMMAND: sc()} for p in StatefulSets.pod_names(state.sts, state.namespace)}

        return {}

    def help(self, _: ReplState):
        return f'{ExportTable.COMMAND} TABLE\t export table'

def ing(msg: str, body: Callable[[], None]):
    log2(f'{msg}...', nl=False)
    body()
    log2(' OK')

class GeneratorStream(io.RawIOBase):
    def __init__(self, generator):
        self._generator = generator
        self._buffer = b''  # Buffer to store leftover bytes from generator yields

    def readable(self):
        return True

    def _read_from_generator(self):
        try:
            chunk = next(self._generator)
            if isinstance(chunk, str):
                chunk = chunk.encode('utf-8')  # Encode if generator yields strings
            self._buffer += chunk
        except StopIteration:
            pass  # Generator exhausted

    def readinto(self, b):
        # Fill the buffer if necessary
        while len(self._buffer) < len(b):
            old_buffer_len = len(self._buffer)
            self._read_from_generator()
            if len(self._buffer) == old_buffer_len:  # Generator exhausted and buffer empty
                break

        bytes_to_read = min(len(b), len(self._buffer))
        b[:bytes_to_read] = self._buffer[:bytes_to_read]
        self._buffer = self._buffer[bytes_to_read:]
        return bytes_to_read

    def read(self, size=-1):
        if size == -1:  # Read all remaining data
            while True:
                old_buffer_len = len(self._buffer)
                self._read_from_generator()
                if len(self._buffer) == old_buffer_len:
                    break
            data = self._buffer
            self._buffer = b''
            return data
        else:
            # Ensure enough data in buffer
            while len(self._buffer) < size:
                old_buffer_len = len(self._buffer)
                self._read_from_generator()
                if len(self._buffer) == old_buffer_len:
                    break

            data = self._buffer[:size]
            self._buffer = self._buffer[size:]
            return data