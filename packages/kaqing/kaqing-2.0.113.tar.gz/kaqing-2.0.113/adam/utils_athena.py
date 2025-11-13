from datetime import datetime
import functools
import time
import boto3

from adam.config import Config
from adam.utils import lines_to_tabular, log, log2

# no state utility class
class Athena:
   def database_names(prefix: str = 'export_'):
      query = f"SELECT schema_name FROM information_schema.schemata WHERE schema_name <> 'information_schema'"
      if prefix:
         query = f"{query} AND schema_name like '{prefix}%'"

      state, reason, rs = Athena.query(query)
      if rs:
         names = []
         for row in rs[1:]:
               row_data = [col.get('VarCharValue') if col else '' for col in row['Data']]
               names.append(row_data[0])

         return names

      return []

   def clear_cache():
      Athena.table_names.cache_clear()
      Athena.column_names.cache_clear()

   @functools.lru_cache()
   def table_names(database: str = 'audit', function: str = 'audit'):
      region_name = Config().get(f'{function}.athena.region', 'us-west-2')
      database_name = Config().get(f'{function}.athena.database', database)
      catalog_name = Config().get(f'{function}.athena.catalog', 'AwsDataCatalog')

      athena_client = boto3.client('athena', region_name=region_name)
      paginator = athena_client.get_paginator('list_table_metadata')

      table_names = []
      for page in paginator.paginate(CatalogName=catalog_name, DatabaseName=database_name):
         for table_metadata in page.get('TableMetadataList', []):
            table_names.append(table_metadata['Name'])

      return table_names

   @functools.lru_cache()
   def column_names(tables: list[str] = [], database: str = None, function: str = 'audit', partition_cols_only = False):
      if not database:
         database = Config().get(f'{function}.athena.database', 'audit')

      if not tables:
         tables = Config().get(f'{function}.athena.tables', 'audit').split(',')

      table_names = "'" + "','".join([table.strip() for table in tables]) + "'"

      query = f"select column_name from information_schema.columns where table_name in ({table_names}) and table_schema = '{database}'"
      if partition_cols_only:
         query = f"{query} and extra_info = 'partition key'"

      _, _, rs = Athena.query(query)
      if rs:
         return [row['Data'][0].get('VarCharValue') for row in rs[1:]]

      return []

   def run_query(sql: str, database: str = None):
      state, reason, rs = Athena.query(sql, database)

      if state == 'SUCCEEDED':
         if rs:
            column_info = rs[0]['Data']
            columns = [col.get('VarCharValue') for col in column_info]
            lines = []
            for row in rs[1:]:
                  row_data = [col.get('VarCharValue') if col else '' for col in row['Data']]
                  lines.append('\t'.join(row_data))

            log(lines_to_tabular(lines, header='\t'.join(columns), separator='\t'))
      else:
         log2(f"Query failed or was cancelled. State: {state}")
         log2(f"Reason: {reason}")

   def query(sql: str, database: str = None, function: str = 'audit') -> tuple[str, str, list]:
      athena_client = boto3.client('athena')

      if not database:
         database = Config().get(f'{function}.athena.database', 'audit')

      s3_output_location = Config().get(f'{function}.athena.output', f's3://s3.ops--{function}/ddl/results')

      response = athena_client.start_query_execution(
         QueryString=sql,
         QueryExecutionContext={
               'Database': database
         },
         ResultConfiguration={
               'OutputLocation': s3_output_location
         }
      )

      query_execution_id = response['QueryExecutionId']

      while True:
         query_status = athena_client.get_query_execution(QueryExecutionId=query_execution_id)
         state = query_status['QueryExecution']['Status']['State']
         if state in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
               break
         time.sleep(1)

      if state == 'SUCCEEDED':
         results_response = athena_client.get_query_results(QueryExecutionId=query_execution_id)
         if results_response['ResultSet']['Rows']:
            return (state, None, results_response['ResultSet']['Rows'])

         return (state, None, [])
      else:
         return (state, query_status['QueryExecution']['Status'].get('StateChangeReason'), [])