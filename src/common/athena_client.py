import boto3


class AthenaClient:

    athena_client = boto3.client('athena')

    @classmethod
    def execute_sql_query_on_bucket(cls, bucket_name, query):
        try:
            response = cls.athena_client.start_query_execution(
                QueryString=query,
                QueryExecutionContext={
                    'Database': 'seisms_database'
                },
                ResultConfiguration={
                    'OutputLocation': f's3://{bucket_name}'
                }
            )
            return response
        except Exception as e:
            raise e

    @classmethod
    def get_query_execution(cls, query_execution_id):
        try:
            response = cls.athena_client.get_query_execution(
                QueryExecutionId=query_execution_id
            )
            return response
        except Exception as e:
            raise e
