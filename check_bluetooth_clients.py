#!/usr/bin/env python

import urllib2
import json
import sys
import contextlib



class Connection(object):

    def __init__(self, server, user, passwd):
        self.server = "http://{}/ubus".format(server)
        auth_response = self._request("session", "login", username=user, password=passwd)
        assert "ubus_rpc_session" in auth_response

        self._session_id = auth_response["ubus_rpc_session"]

    @property
    def session_id(self):
        if not hasattr(self, "_session_id"):
            return "00000000000000000000000000000000"
        return self._session_id

    def _request(self, subsytem, method, **params):

        request = {"jsonrpc": "2.0",
                   "id": 1,
                   "method": "call",
                   "params": [ self.session_id,
                               subsytem,
                               method,
                               params] }
        response = None
        with contextlib.closing(urllib2.urlopen(self.server, json.dumps(request))) as stream:
            assert stream.getcode() == 200
            response = json.load(stream)

        if not response or "error" in response:
            raise Exception(str(response))

        return response["result"][1]

    def bluetooth_clients(self, btaddr):
        subsytem = "bluetooth"
        method = "check_client"
        result = self._request(subsytem, method, bt_address=btaddr)
        assert "clients" in result

        return result["clients"].values()
        return result



if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: {} <OpenWrt_Host> <User> <Pass> <bt_address>".format(sys.argv[0]))
        sys.exit(1)

    clients = []
    connection = Connection(sys.argv[1], sys.argv[2], sys.argv[3])
    for btaddr in sys.argv[4:]:
        clients.extend(connection.bluetooth_clients(btaddr))

    print(", ".join(clients))
