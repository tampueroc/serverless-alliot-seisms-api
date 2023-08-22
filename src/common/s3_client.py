import json
import logging
import os
import boto3
logging.getLogger().setLevel(logging.INFO)


class S3Client:

    def __init__(self):
        is_offline_environment = (os.getenv('OFFLINE_ENV', 'False') == 'True')
        if is_offline_environment:
            print('local s3')
            self.s3 = boto3.client('s3',
                                   endpoint_url='http://localhost:4569',
                                   aws_access_key_id='S3RVER',
                                   aws_secret_access_key='S3RVER',
                                   region_name='us-west-2')
        else:
            self.s3 = boto3.client('s3')

    def upload_file(self, file_path, bucket_name, key):
        try:
            logging.info(f"Uploading file {file_path} to s3 bucket {bucket_name} with key {key}")
            return self.s3.upload_file(file_path, bucket_name, key)
        except Exception as e:
            logging.error(f"Error uploading file to s3: {e}")
            raise e

    def get_files(self, bucket_name, expression):
        try:
            logging.info(f"Getting files from s3 bucket {bucket_name} with expression {expression}")
            response = self.s3.select_object_content(
                Bucket=bucket_name,
                Key='seisms.csv',
                ExpressionType='SQL',
                Expression=expression,
                InputSerialization={'CSV': {'FileHeaderInfo': 'Use', 'FieldDelimiter': ','}},
                OutputSerialization={'JSON': {'RecordDelimiter': ','}}
            )
            logging.info(f"Response from s3: {response}")
            event_stream = response['Payload']
            logging.info(f"Event stream: {event_stream}")
            data = []
            for event in event_stream:
                if 'Records' in event:
                    logging.info(f"Adding data to response: {event['Records']['Payload'].decode('utf-8')}")
                    for record in event['Records']['Payload'].decode('utf-8').split(','):
                        data.append(json.loads(record))
                elif 'End' in event:
                    print('Result is complete')
                    end_event_received = True
            if not end_event_received:
                raise Exception("End event not received, request incomplete.")
            return data
        except Exception as e:
            logging.error(f"Error getting files from s3: {e}")
            raise e
