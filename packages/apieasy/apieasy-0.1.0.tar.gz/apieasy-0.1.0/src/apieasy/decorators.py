from .router import router


def get(path):
    def decorator(func):
        router.add_route("GET", path, func)
        return func
    return decorator


def post(path):
    def decorator(func):
        router.add_route("POST", path, func)
        return func
    return decorator
