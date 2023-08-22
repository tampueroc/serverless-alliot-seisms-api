import datetime
import json
import logging
import os

from .common.s3_client import S3Client

from .models.payloads import GetEntriesQueryParameters, GetSeismPayload
logging.getLogger().setLevel(logging.INFO)


def get_seisms(event: dict, context: dict):
    try:
        logging.info(f"Starting get_seisms lambda function {datetime.datetime.utcnow()} with event: {event} and context: {context}")
        query_string_parameters_raw = event['queryStringParameters'] if event.get('queryStringParameters') else {}
        query_string_parameters = GetEntriesQueryParameters(**query_string_parameters_raw)
        s3_client = S3Client()
        logging.info(f"Query string parameters to sql query: {query_string_parameters.to_sql_query()}")
        s3_response = s3_client.get_files('seisms-bucket', query_string_parameters.to_sql_query())
        logging.info(f"Response from s3: {s3_response}")
        return {
            'statusCode': 200,
            'body': json.dumps(s3_response)
        }
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps('Internal Server Error')
        }


def create_seisms(event: dict, context: dict):
    try:
        logging.info(f"Starting create_seisms lambda function {datetime.datetime.utcnow()} with event: {event} and context: {context}")
        event_body = json.loads(event['body'])
        seisms_entries = [GetSeismPayload(**seism) for seism in event_body]
        s3_client = S3Client()
        os.chdir('/tmp')
        with open("seisms.csv", "w") as f:
            f.write('timestamp,country,magnitude\n')
            for seism in seisms_entries:
                f.write(f"{seism.timestamp},{seism.country},{seism.magnitude}")
                f.write('\n')
            logging.info(f"Uploading file to s3 {f.name}")
            s3_client.upload_file(f.name, 'seisms-bucket', f.name)
            f.close()
        return {
            'statusCode': 200,
            'body': json.dumps('Ok')
        }
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps('Internal Server Error')
        }
