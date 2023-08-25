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
                OutputSerialization={'JSON': {'RecordDelimiter': '\n'}}
            )
            event_stream = response['Payload']
            data = []
            for event in event_stream:
                try:
                    if 'Records' in event:
                        logging.info(f"Records event: {event}")
                        raw_records = event['Records']['Payload'].decode('utf-8').split('\n')
                        logging.info(f"Raw records: {raw_records}")
                        for raw_record in raw_records:
                            if raw_record:
                                record = json.loads(raw_record)
                                data.append(record)
                    elif 'End' in event:
                        print('Result is complete')
                        end_event_received = True
                except Exception as e:
                    logging.error(f"Error parsing S3 file EventStream: {e}")
                    raise e
            if not end_event_received:
                raise Exception("End event not received, request incomplete.")
            return data
        except Exception as e:
            logging.error(f"Error getting files from s3: {e}")
            raise e

    def get_file_by_key(self, bucket_name, key):
        try:
            logging.info(f"Getting file from s3 bucket {bucket_name} with key {key}")
            response = self.s3.get_object(
                Bucket=bucket_name,
                Key=key
            )
            logging.info(f"Response from s3: {response}")
            return response
        except Exception as e:
            logging.error(f"Error getting file from s3: {e}")
            raise e
