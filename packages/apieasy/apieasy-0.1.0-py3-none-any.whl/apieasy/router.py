class Router:
    def __init__(self):
        self.routes = {}   # key: (method, path)  value: handler

    def add_route(self, method, path, handler):
        key = (method.upper(), path)
        self.routes[key] = handler

    def resolve(self, method, path):
        key = (method.upper(), path)
        return self.routes.get(key, None)


router = Router()
