import datetime
import json
import logging

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
        # s3_client = S3Client()
        logging.info(f"Query string parameters to sql query: {query_string_parameters.to_sql_query()}")
        # s3_response = s3_client.get_files('seisms-bucket', query_string_parameters.to_sql_query())
        response_id = AthenaClient.execute_sql_query_on_bucket(bucket_name='seism-bucket-results', query=query_string_parameters.to_sql_query())
        if response_id.get('QueryExecutionId'):
            response = AthenaClient.get_query_execution(query_execution_id=response_id['QueryExecutionId'])
            logging.info(f"Response from athena: {response}")
        logging.info(f"Response from s3: {response}")
        if len(response) > 100:
            logging.error(f"Error in get_seisms lambda function: Too many entries, {len(response)}")
            return create_http_response(400, 'Bad Request: Too many entries, more than 100')
        entries = [SeismEntry(**entry) for entry in response]
        entries.sort(key=lambda x: x.timestamp)
        return create_http_response(200, json.dumps(entries, cls=CustomPydanticJSONEncoder))
    except Exception as e:
        logging.exception(f"Exception in get_seisms lambda function: {e}")
        return create_http_response(500, json.dumps({"message": 'Internal Server Error'}))


def create_seisms(event: dict, context: dict):
    try:
        logging.info(f"Starting create_seisms lambda function {datetime.datetime.utcnow()} with event: {event}")
        event_body = json.loads(event['body'])
        if len(event_body) > 100:
            logging.error(f"Error in create_seisms lambda function: Too many entries, {len(event_body)}")
            return create_http_response(400, 'Bad Request: Too many entries, more than 100')
        seisms_entries = [SeismEntry(**seism) for seism in event_body]
        s3_client = S3Client()
        filename = '/tmp/seisms.csv'
        seism_file = s3_client.get_file_by_key('seisms-bucket', 'seisms.csv')
        with open(filename, "w") as f:
            try:
                if seism_file:
                    logging.info("Extending seisms from s3")
                    f.write(seism_file['Body'].read().decode('utf-8'))
                else:
                    f.write('timestamp,country,magnitude\n')
                for seism in seisms_entries:
                    f.write(f"{seism.timestamp},{seism.country},{seism.magnitude}")
                    f.write('\n')
                f.close()
            except Exception as e:
                logging.exception(f"Exception writing seism entries to file: {e}")
            s3_client.upload_file(filename, 'seisms-bucket', 'seisms.csv')
        return create_http_response(200, 'Success creating seisms entries')
    except Exception as e:
        logging.exception(f"Exception in create_seisms lambda function: {e}")
        return create_http_response(500, json.dumps({"message": 'Internal Server Error'}))
