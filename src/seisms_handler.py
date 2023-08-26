import csv
import datetime
import io
import json
import logging
import time
import pandas as pd

from .common.athena_client import AthenaClient
from .common.encoders import CustomPydanticJSONEncoder
from .common.utils import create_http_response
from .common.s3_client import S3Client
from .models.payloads import GetEntriesQueryParameters, SeismEntry

logging.getLogger().setLevel(logging.INFO)


def get_seisms(event: dict, context: dict):
    try:
        logging.info(f"Starting get_seisms lambda function {datetime.datetime.utcnow()} with event: {event}")
        query_string_parameters_raw = event['queryStringParameters'] if event.get('queryStringParameters') else {}
        query_string_parameters = GetEntriesQueryParameters(**query_string_parameters_raw)
        s3_client = S3Client()
        logging.info(f"Query string parameters to sql query: {query_string_parameters.to_sql_query()}")
        response_id = AthenaClient.execute_sql_query_on_bucket(bucket_name='seism-bucket-results', query=query_string_parameters.to_sql_query())
        while True:
            response_execution = AthenaClient.get_query_execution(query_execution_id=response_id['QueryExecutionId'])
            finish_state = response_execution['QueryExecution']['Status']['State']
            if finish_state == "RUNNING" or finish_state == "QUEUED":
                time.sleep(1)
            else:
                logging.info(f"Query finished with state: {finish_state}")
                break
        response_s3 = s3_client.get_file_by_key('seism-bucket-results', response_execution['QueryExecution']['ResultConfiguration']['OutputLocation'].split('/')[-1])
        logging.info(f"Response from Athena: {response_s3}")
        if response_s3:
            entries = []
            content = response_s3['Body'].read().decode('utf-8').splitlines(True)
            reader = csv.reader(content)
            for raw_record in reader:
                if raw_record[0] == 'timestamp':
                    continue
                logging.info(f"Raw record: {raw_record}")
                entries.append(SeismEntry(timestamp=raw_record[0], country=raw_record[1], magnitude=raw_record[2]))
        if len(entries) > 100:
            logging.error(f"Error in get_seisms lambda function: Too many entries, {len(entries)}")
            return create_http_response(400, 'Bad Request: Too many entries, more than 100')
        entries.sort(key=lambda x: x.timestamp)
        return create_http_response(200, json.dumps(entries, cls=CustomPydanticJSONEncoder))
    except Exception as e:
        logging.exception(f"Exception in get_seisms lambda function: {e}")
        return create_http_response(500, json.dumps({"message": 'Internal Server Error'}))


def create_seisms(event: dict, context: dict):
    try:
        # logging.info(f"Starting create_seisms lambda function {datetime.datetime.utcnow()} with event: {event}")
        event_body = json.loads(event['body'])
        if len(event_body) > 100:
            logging.error(f"Error in create_seisms lambda function: Too many entries, {len(event_body)}")
            return create_http_response(400, 'Bad Request: Too many entries, more than 100')
        seisms_entries = [SeismEntry(**seism) for seism in event_body]
        df = pd.DataFrame([seism.model_dump() for seism in seisms_entries])
        s3_client = S3Client()
        filename = '/tmp/seisms.parq'
        seism_file = s3_client.get_file_by_key('seisms-bucket', 'seisms.parquet')
        if seism_file:
            try:
                logging.info("Appending new seisms entries to existing seisms file")
                pq_file = io.BytesIO(seism_file['Body'].read())
                df_base = pd.read_parquet(pq_file)
                df = pd.concat([df_base, df])
            except Exception as e:
                logging.exception(f"Exception appending seism entries to file: {e}")
                raise e
        df.to_parquet(filename)
        s3_client.upload_file(filename, 'seisms-bucket', 'seisms.parquet')
        return create_http_response(200, json.dumps({'message': 'Success creating seisms entries'}))
    except Exception as e:
        logging.exception(f"Exception in create_seisms lambda function: {e}")
        return create_http_response(500, json.dumps({"message": 'Internal Server Error'}))
