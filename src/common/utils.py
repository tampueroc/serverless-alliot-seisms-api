import json


def create_http_response(status_code: int, body: str) -> dict:
    if status_code in [200, 201]:
        return {
            'statusCode': status_code,
            'body': json.dumps(body)
        }
    else:
        return {
            'statusCode': status_code,
            'body': json.dumps(body)
        }
