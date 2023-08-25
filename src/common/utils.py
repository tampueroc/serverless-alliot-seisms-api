
def create_http_response(status_code: int, body: str) -> dict:
    return {
        'statusCode': status_code,
        'body': body
    }
