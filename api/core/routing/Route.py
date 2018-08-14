from werkzeug.routing import Rule


class Route:
    def __init__(self, verb, url, name, controller, method):
        """creates an instance of a Route Object"""
        self.verb = verb
        self.url = url
        self.name = name
        self.controller = controller
        self.method_name = method

    def rule(self):
        """ factory for werkzeug.rule"""
        return Rule(self.url, endpoint=self.name, methods=[self.verb])

    def run(self, **params):

        return getattr(self.controller(), self.method_name)(*params.values())

    def prefix(self, url_prefix):
        """ prefixes a url with some prefix e.g api"""
        self.url = url_prefix + self.url
        return self
