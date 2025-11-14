from requests import Response


def call_processor(response: Response):
    try:
        data = response.json()
    except Exception as e:
        data = response.text
    return {
        'status': response.status_code,
        'reason': response.reason,
        'response': data,
    }


def data_processor(response: Response):
    try:
        data = response.json()
    except Exception as e:
        raise Exception({
            'status': response.status_code,
            'reason': response.reason,
            'response': response.text,
            'exception': str(e)
        })

    return data
