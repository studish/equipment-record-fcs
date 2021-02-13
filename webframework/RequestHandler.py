#!/usr/bin/env python3

from __future__ import annotations

import os
import json
import re
import mimetypes
import http.server
import urllib.parse
from utils.Logger import webServerLogger as logger
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from webframework.Server import Server


class RequestHandler(http.server.SimpleHTTPRequestHandler):
    webServer: Server = None

    request: bytes

    responseCode: int = 200
    responseHeaders: list[list[str]] = []
    contentType: str

    query: dict[str, list[str]] = {}

    def __init__(self, request, client_address, server):
        if self.webServer is None:
            raise RuntimeError("webServer was not specified!")
        self.request = request

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
        for prefix, localDirPath in self.webServer.staticPaths.items():
            logger.debug(prefix + " -> " + localDirPath)
            if self.path.startswith(prefix):
                localPath = localDirPath + self.path[len(prefix):]
                logger.debug(localPath)

                if os.path.isdir(localPath):
                    localPath = localPath.rstrip('/') + '/index.html'

                if not os.path.isfile(localPath):
                    break

                contentType = mimetypes.guess_type(localPath)[0]
                if contentType == None:
                    contentType = "text/plain"
                self.send_response(200)
                self.send_header('Content-Type', contentType)
                self.end_headers()
                with open(localPath, 'rb') as file:
                    self.wfile.write(file.read())
                return

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
        # TODO: Send encoding for plain text, UTF-8 by default

        if type(data) is dict:
            logger.debug("JSON detected!")
            self.contentType = "text/json"
            data = json.dumps(data)

        self.done = True
        self.send_response(self.responseCode)
        for header in self.responseHeaders:
            self.send_header(*header)
        self.end_headers()
        self.wfile.write(data.encode())
