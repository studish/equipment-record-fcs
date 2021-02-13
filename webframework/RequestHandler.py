#!/usr/bin/env python3

from __future__ import annotations

import re
import http.server
import urllib.parse
from utils.Logger import webServerLogger as logger
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from webframework.Server import Server


class RequestHandler(http.server.BaseHTTPRequestHandler):
    webServer: Server = None

    responseCode: int = 200
    responseHeaders: list[list[str]] = [["Content-Type", "text/html"]]

    query: dict[str, list[str]] = {}

    def __init__(self, request, client_address, server):
        if self.webServer is None:
            raise RuntimeError("webServer was not specified!")

        super().__init__(request, client_address, server)

    def do(self, method):
        url = urllib.parse.urlparse(self.path)

        self.path = url.path
        self.query = urllib.parse.parse_qs(url.query)

        if self.path in self.webServer.handlers[method].keys():
            self.webServer.handlers[method][self.path](self)
            if not self.done:
                # The handler didn't send the response. Assume something went wrong
                self.send_error(500)
        else:
            self.send_error(404)

    def do_GET(self, *args, **kwargs):
        self.do('GET')

    def do_POST(self, *args, **kwargs):
        self.do('POST')

    def do_PUT(self, *args, **kwargs):
        self.do('PUT')

    def do_DELETE(self, *args, **kwargs):
        self.do('DELETE')

    def do_PATCH(self, *args, **kwargs):
        self.do('PATCH')

    done = False

    def send(self, data: str):
        self.done = True
        self.send_response(self.responseCode)
        for header in self.responseHeaders:
            self.send_header(*header)
        self.end_headers()
        self.wfile.write(data.encode())
