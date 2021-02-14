#!/usr/bin/env python3

from __future__ import annotations

import os
from cgi import parse_multipart, parse_header
import io
import json
import re
import mimetypes
import http.server
import urllib.parse
from utils.Logger import logger
from typing import TYPE_CHECKING, List, Dict, Tuple

if TYPE_CHECKING:
    from webframework.Server import Server


class RequestHandler(http.server.BaseHTTPRequestHandler):
    SUPPORTED_TYPES = ['application/json', 'application/x-www-form-urlencoded', 'multipart/form-data']

    webServer: Server = None

    responseCode: int = 200
    # [['Header-Name', 'Header-Value']]
    responseHeaders: List[List[str]] = []
    contentType: str = "text/html"

    postData: dict or list
    postFiles: Dict[str, List[Tuple[bytes, str]]]

    acceptable_types: List[str] = []

    query: Dict[str, List[str]] = {}

    session: Dict[str, str]

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
        for prefix, localDirPath in self.webServer.staticPaths.items():
            if self.path.startswith(prefix):
                logger.debug("Prefix converted: '{}' -> '{}'".format(prefix, localDirPath))
                localPath = localDirPath + self.path[len(prefix):]
                for c in '?#':
                    if c in localPath:
                        localPath = localPath[:localPath.index('?')]
                logger.debug(localPath)
                # TODO: Injection protection!

                if os.path.isdir(localPath):
                    localPath = localPath.rstrip('/') + '/index.html'

                if not os.path.isfile(localPath):
                    continue

                contentType = mimetypes.guess_type(localPath)[0]
                if contentType is None:
                    contentType = "text/html"
                self.send_response(200)
                self.send_header('Content-Type', contentType)
                with open(localPath, 'rb') as file:
                    filestat: os.stat_result = os.fstat(file.fileno())
                    self.send_header("Content-Length", str(filestat[6]))
                    self.send_header("Last-Modified", self.date_time_string(int(filestat.st_mtime)))
                    self.end_headers()
                    self.wfile.write(file.read())
                return

        self.do('GET')

    def do_POST(self, *args, **kwargs):
        pure_path = re.match('^([^?#]+).*', self.path).group(1)
        if pure_path in self.webServer.accept_content_types['POST'].keys():
            self.acceptable_types = self.webServer.accept_content_types['POST'][pure_path]

        body = {}
        files = {}
        # Get the content length to read
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length != 0:
            # Now we read the whole POST body in parts.
            # First, we check the content type (assume it's text/plain if not provided)
            content_type_raw: str = self.headers.get('Content-Type', '')
            content_type: str = content_type_raw
            if ';' in content_type_raw:
                content_type = content_type_raw[:content_type_raw.index(';')].strip()

            if content_type is not None and content_type in self.acceptable_types and \
                    content_type in self.SUPPORTED_TYPES:
                body, files = self.parse_request_body(content_type, content_type_raw, content_length)
                if body is None:
                    body = {}
                if files is None:
                    files = {}

        self.postData = body
        self.postFiles = files

        self.do('POST')

    def do_PUT(self, *args, **kwargs):
        self.do('PUT')

    def do_DELETE(self, *args, **kwargs):
        self.do('DELETE')

    def do_PATCH(self, *args, **kwargs):
        self.do('PATCH')

    done = False

    def send(self, data: str, encoding="utf-8"):
        if type(data) is dict:
            logger.debug("JSON response detected!")
            self.contentType = "text/json"
            data = json.dumps(data)

        self.done = True
        self.send_response(self.responseCode)
        contentTypeSent = False
        for header in self.responseHeaders:
            self.send_header(*header)
            if header[0] == "Content-Type":
                contentTypeSent = True
        if not contentTypeSent:
            if self.contentType == "text/html":
                self.contentType += "; charset=" + encoding
            self.send_header("Content-Type", self.contentType)
        self.end_headers()
        self.wfile.write(data.encode(encoding))

    def parse_request_body(self, content_type, content_type_raw, content_length) -> Tuple[dict, dict]:
        if content_type not in self.SUPPORTED_TYPES:  # Check just in case
            raise RuntimeError("Content-Type {} not supported!".format(content_type))
        if content_type == 'application/json':
            body_raw = self.rfile.read(content_length)
            body_parsed = json.loads(body_raw)
            return body_parsed, {}
        if content_type == "application/x-www-form-urlencoded":
            body_raw = self.rfile.read(content_length)
            print(body_raw)
            body_parsed_tuples = urllib.parse.parse_qsl(body_raw.decode())
            body_parsed = {}
            for key, value in body_parsed_tuples:
                # key = key.decode("utf-8")
                if key not in body_parsed.keys():
                    body_parsed[key] = []
                # body_parsed[key].append(value.decode("utf-8"))
                body_parsed[key].append(value)
            return body_parsed, {}
        if content_type == "multipart/form-data":
            c_type, c_data = parse_header(content_type_raw)
            bytestring = self.rfile.read(content_length)

            # noinspection PyTypeChecker
            c_data['boundary'] = bytes(c_data['boundary'], 'utf-8')
            c_data['CONTENT-LENGTH'] = content_length

            # noinspection PyTypeChecker
            form_data = parse_multipart(io.BytesIO(bytestring), c_data)
            form_files: Dict[str, List[Tuple[bytes, str]]] = {}

            pattern: re.Pattern = re.compile(b'Content-Disposition: form-data; name="(.*)"; filename="(.*)"')
            for match in pattern.finditer(bytestring):
                name, filename = match.group(1).decode("utf-8"), match.group(2).decode()

                if name not in form_files.keys():
                    form_files[name] = []
                form_files[name].append((form_data[name][0], filename))
                del form_data[name][0]
                if not form_data[name]:
                    del form_data[name]

            return form_data, form_files
