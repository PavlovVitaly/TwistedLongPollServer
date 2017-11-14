from twisted.internet import reactor, endpoints
from twisted.web import server, resource

TESTDATA = {'server': 'http://127.0.0.1:8000',
            'key': 'qwerty',
            'ts': '0'}


class Counter(resource.Resource):
    isLeaf = True
    numberRequests = 0

    def render_GET(self, request):
        self.numberRequests += 1
        request.setHeader(b"content-type", b"text/plain")
        content = u"I am request #{}\n".format(self.numberRequests)
        # return content.encode("ascii")
        return str(TESTDATA).encode("ascii")

endpoints.serverFromString(reactor, "tcp:8080").listen(server.Site(Counter()))
reactor.run()
