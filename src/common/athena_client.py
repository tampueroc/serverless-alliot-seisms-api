import boto3


class AthenaClient:

    athena_client = boto3.client('athena')

    def execute_sql_query_on_bucket(cls, bucket_name, query):
        try:
            response = cls.athena_client.start_query_execution(
                QueryString=query,
                QueryExecutionContext={
                    'Database': 'seisms_database'
                },
                ResultConfiguration={
                    'OutputLocation': f's3://{bucket_name}/results/'
                }
            )
            return response
        except Exception as e:
            raise e
