from datetime import datetime
import functools
import getpass
import time
import boto3
import requests

from adam.config import Config
from adam.utils import lines_to_tabular, log, log2
from adam.utils_net import get_my_host

# no state utility class
class Exports:
   @functools.lru_cache()
   def table_names(db: str):
      region_name = Config().get('audit.athena.region', 'us-west-2')
      database_name = Config().get('audit.athena.database', db)
      catalog_name = Config().get('audit.athena.catalog', 'AwsDataCatalog')

      athena_client = boto3.client('athena', region_name=region_name)
      paginator = athena_client.get_paginator('list_table_metadata')

      table_names = []
      for page in paginator.paginate(CatalogName=catalog_name, DatabaseName=database_name):
         for table_metadata in page.get('TableMetadataList', []):
            table_names.append(table_metadata['Name'])

      return table_names

   @functools.lru_cache()
   def column_names(tables: list[str] = [], database: str = None, partition_cols_only = False):
      if not database:
         database = Config().get('audit.athena.database', 'audit')

      if not tables:
         tables = Config().get('audit.athena.tables', 'audit').split(',')

      table_names = "'" + "','".join([table.strip() for table in tables]) + "'"

      query = f"select column_name from information_schema.columns where table_name in ({table_names}) and table_schema = '{database}'"
      if partition_cols_only:
         query = f"{query} and extra_info = 'partition key'"

      _, _, rs = Exports.audit_query(query)
      if rs:
         return [row['Data'][0].get('VarCharValue') for row in rs[1:]]

      return []