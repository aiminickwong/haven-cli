#!/usr/bin/python3

"""The base command."""
import http.client
import logging


class Base(object):
    def __init__(self, options, *args, **kwargs):
        self.options = options
        self.args = args
        self.kwargs = kwargs
        self.conn = None

    def run(self):
        self.options
        raise NotImplementedError('You must implement the run() method yourself!')

    def __open(self):
        if self.conn:
            return
        self.conn = http.client.HTTPConnection(self.options.get('--server'), self.options.get('--port'))

    def _send(self, path, method='GET', data=None):
        self.last_req_info = {'method': method, 'path': path, 'data': data}
        try:
            from base64 import b64encode
            self.__open()

            userAndPass = b64encode(
                b"" + self.options.get('--login') + ":" + self.options.get('--server') + "").decode("ascii")
            headers = {'Authorization': 'Basic %s' % userAndPass}

            self.conn.request(method, path, headers=headers)
        except Exception as ex:
            self.conn.close()
            self.conn = None
            logging.error("Can not connect to dm %s due to error: %s", self.options.get('--server'), ex)
            raise
        resp = self.conn.getresponse()
        if resp.status != '200':
            raise Exception("Invalid response: {} {} from {}"
                            .format(resp.status, resp.reason, self.options.get('--server')))
        return json.loads(resp.read().decode('utf8'))