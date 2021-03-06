#!/usr/bin/python3

"""usage: dm applications [list|add|stop|start|rm] --cluster=<cluster> [--application=<application>] [--file=<path>] --server=<server> --port=<port> --login=<login> --password=<password>  [--columns=<column1,column2>] [--help] [--verbose=<level>]

Returns cluster information

Options:
  -h --help                         Show this screen.
  -v --version                      Show version.
  -l --log=<level>                  Log level
  -s --server=<server>              host of DM server [default: localhost]
  -p --port=<port>                  port of DM server [default: 8761]
  -u --user=<login>                 Username of DM
  -p --password=<password>          Password of DM
  -c --cluster=<cluster>            Cluster name
  -a --application=<application>    Application name
  --file=<path>                     File path
  --columns=<column1,column2>       List of columns [default: name,cluster,initFile,containers]

Commands:
  info                              Default action: shows application
  add                               Creates new application using compose file, requires --application=<application> --file=<path>
  stop                              Removes action, requires --application=<application>
  rm                                Removes action, requires --application=<application>
Examples:
  dm applications --cluster=dev
  dm applications add --cluster=dev --application=pythonApp --file=/home/user/compose.yaml
  dm applications stop --cluster=dev --application=pythonApp
  dm applications rm --cluster=dev --application=pythonApp

Help:
  You can put any configs to dm.conf file
  For help using this tool, please open an issue on the Github repository:
  https://codeabovelab.com
"""

from .base import Base
import json


class Cluster(Base):
    def run(self):
        # /clusters/{cluster}/containers
        add = self.options.get('add')
        rm = self.options.get('rm')
        stop = self.options.get('stop')
        start = self.options.get('start')
        if add:
            self.__add()
        if rm:
            self.__rm()
        if stop:
            self.__stop()
        if start:
            self.__start()
        if not add and not rm and not stop and not start:
            self.__list()

    def __list(self):
        # get /ui/api/application/{cluster}/all
        result = self._send("/ui/api/application/" + self.options.get('--cluster') + "/all")
        columns = self.options.get('--columns')
        keys = columns.split(",")
        self._print(keys, json.loads(result))

    def __stop(self):
        # post /ui/api/application/{cluster}/{appId}/stop
        cluster = self.options.get('--cluster')
        application = self.options.get('--application')
        if application:
            self._send("/ui/api/application/" + cluster + "/" + application + "/stop", method='POST')
        else:
            print("specify --application=<appId>")

    def __start(self):
        # post /ui/api/application/{cluster}/{appId}/start
        cluster = self.options.get('--cluster')
        application = self.options.get('--application')
        if application:
            self._send("/ui/api/application/" + cluster + "/" + application + "/start", method='POST')
        else:
            print("specify --application=<appId>")

    def __rm(self):
        # delete /ui/api/application/{cluster}/{appId}
        cluster = self.options.get('--cluster')
        application = self.options.get('--application')
        if application:
            self._send("/ui/api/application/" + cluster + "/" + application, method='DELETE')
        else:
            print("specify --application=<appId>")

    def __add(self):
        # /clusters/{cluster}/compose
        file = self.options.get('--file')
        cluster = self.options.get('--cluster')
        application = self.options.get('--application')
        if not file and not application:
            print("specify --file=<path> --application=<application>")
            return
        try:
            from base64 import b64encode
            self._open()

            userAndPass = self.options.get('--login') + ':' + self.options.get('--password')
            bAuth = b64encode(str.encode(userAndPass)).decode("ascii")
            headers = {
                "Content-type": "application/octet-stream",
                "Authorization": "Basic %s" % bAuth
            }
            files = {'file': ('compose.yaml', open(file, 'rb'), 'application/json', {'Expires': '0'})}
            self.conn.request(method='POST', url="/ui/api/application/" + cluster + '/' + application + "/compose",
                               headers=headers, body=open(file, 'rb'))
        except Exception as ex:
            self.conn.close()
            self.conn = None
            print("Can not connect to dm %s due to error: %s", self.options.get('--server'), ex)
