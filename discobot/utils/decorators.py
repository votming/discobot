from requests import Response


def log_api_call(func):
    def _wrapper(*args, **kwargs):
        print(f'{func.__name__}, args: {args}, kwargs: {kwargs}')
        result = func(*args, **kwargs)
        try:
            if isinstance(result, Response):
                print(result.json() if result.status_code < 300 else result.content)
            else:
                print(result)
        except Exception as ex:
            print(str(ex))
        return result
    return _wrapper