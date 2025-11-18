from core import router

def request_mapping(uri: str):
    def wrapper(cls):
        cls._uri = uri
        return cls
    return wrapper

class Controller():
    def __init__(self):
        self.uri = self._uri
        router.get_routes(self.__class__)

    def get_mapping(uri: str):
        def wrapper(func):
            func._http_method = 'GET'
            func._method_uri = uri
            return func
        return wrapper
