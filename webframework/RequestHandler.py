#!/usr/bin/env python3

from __future__ import annotations

import os
from cgi import parse_multipart, parse_header
import io
import json
import re
import mimetypes
import http.server
from http import cookies
from webframework import Session
import urllib.parse
from utils.Logger import logger
from typing import TYPE_CHECKING, List, Dict, Tuple

if TYPE_CHECKING:
    from webframework.Server import Server

pure_path_pattern = re.compile(r'^([^?#]+)(.*)')


class RequestHandler(http.server.BaseHTTPRequestHandler):
    # The supported types of request body
    SUPPORTED_TYPES = ['application/json', 'application/x-www-form-urlencoded', 'multipart/form-data']

    # The web server instance, holds the high-level logic
    web_server: Server

    response_code: int = 200
    # [['Header-Name', 'Header-Value']]
    response_headers: List[List[str]] = []
    response_content_type: str = "text/html"

    # Formatted like JSON. If the content-type is form-data, it's a dict.
    # If it's application/json, this can be anything.
    post_data: dict or list

    # field-name -> list of pairs (file_content, file_name)
    post_files: Dict[str, List[Tuple[bytes, str]]]

    # Request body content types that will be parsed and processed
    acceptable_types: List[str] = []

    # The path query (?a=b&b=c) parsed into dict{name -> list of values}
    query: Dict[str, List[str]] = {}

    # The user session, stored on the server
    session: Session

    # cookies stored in the users browser
    cookies: http.cookies

    # Used to check if the data was sent after the handler finished working.
    done = False

    def __init__(self, request, client_address, server):
        if self.web_server is None:
            raise RuntimeError("web_server was not specified!")

        super().__init__(request, client_address, server)

    def do(self, method):
        self.cookies = cookies.SimpleCookie()
        cookie = self.headers.get("Cookie", failobj=None)
        if cookie is not None:
            self.cookies.load(cookie.replace('{', '').replace('}', ''))
        if "sid" in self.cookies:
            if str(self.cookies.get("sid").value) in self.web_server.sessions:
                self.session = self.web_server.sessions[str(self.cookies["sid"].value)]
            else:
                logger.debug("Couldn't find sid in global storage")
                self.session = Session.Session()
                self.cookies["sid"] = self.session.sid
        else:
            self.session = Session.Session()
            self.cookies["sid"] = self.session.sid

            # Parse the URL properly
        url = urllib.parse.urlparse(self.path)
        self.path = url.path
        self.query = urllib.parse.parse_qs(url.query)

        # Try to find a matching handler function among the ones defined by the server
        if self.path in self.web_server.handlers[method].keys():
            # Call the handler
            self.web_server.handlers[method][self.path](self)
            if not self.done:
                # The handler didn't send the response. Assume something went wrong
                self.send_error(500)
        else:  # Didn't find a matching handler function
            self.send_error(404)

    def do_GET(self):
        # Clean up the URL path for checkups
        match = pure_path_pattern.match(self.path)
        local_path = match.group(1)
        # If we don't have a handler for this path, try static first
        if local_path not in self.web_server.handlers['GET'].keys():
            # Check each static prefix - optimal because there aren't many prefixes
            for prefix, local_dir_path in self.web_server.staticPaths.items():
                if self.path.startswith(prefix):
                    # logger.debug("Prefix converted: '{}' -> '{}'".format(prefix, localDirPath))
                    local_path = local_dir_path + local_path
                    # logger.debug(localPath)
                    # TODO: Injection protection!

                    # If we're pointing at a directory, try index.html
                    if os.path.isdir(local_path):
                        # redirect if directory path doesnt't end with a '/'
                        if not local_path.endswith('/'):
                            self.redirect_to(match.group(1) + '/' + match.group(2))
                            return
                        local_path = local_path.rstrip('/') + '/index.html'
                    # 301 response
                    # If the file is not found, skip
                    if not os.path.isfile(local_path):
                        continue

                    # Guess the mimetype based on the file URL
                    content_type = mimetypes.guess_type(local_path)[0]
                    if content_type is None:  # If can't guess, assume plain text
                        content_type = "text/plain"
                    self.send_response(200)  # If we reached here, then it's a success
                    self.send_header('Content-Type', content_type)
                    with open(local_path, 'rb') as file:
                        filestat: os.stat_result = os.fstat(file.fileno())  # To get filesize and last modified
                        self.send_header("Content-Length", str(filestat[6]))
                        self.send_header("Last-Modified", self.date_time_string(int(filestat.st_mtime)))
                        self.end_headers()
                        self.wfile.write(file.read())  # Send the file over
                        file.close()
                    return

        self.do('GET')

    def redirect_to(self, url: str):
        self.send_response(301)
        self.send_header('Location', url)
        self.send_header('Content-Type', 'text/html')
        self.wfile.write(f'<script>location.href={url}</script>'.encode())

    def do_POST(self):
        self.process_request_body()
        self.do('POST')

    def do_PUT(self):
        self.process_request_body()
        self.do('PUT')

    def do_DELETE(self):
        self.do('DELETE')

    def do_PATCH(self):
        self.process_request_body()
        self.do('PATCH')

    def send(self, data_raw: str | dict | list | bytes, encoding="utf-8"):
        data: bytes
        # Dict / List -> JSON string -> encoded bytes
        if type(data_raw) is dict or type(data_raw) is list:
            logger.debug("JSON response detected!")
            self.response_content_type = "text/json"
            data = json.dumps(data_raw).encode(encoding)
        elif type(data_raw) is str:
            # String -> properly encrypted bytes
            data = data_raw.encode(encoding)
        elif type(data_raw) is bytes:
            data = data_raw
        else:
            raise TypeError("Response body type {} is not supported!".format(type(data_raw)))

        # Send response code
        self.send_response(self.response_code)

        contentTypeSent = False

        # Save session
        if self.session.sid not in self.web_server.sessions:
            self.web_server.sessions[self.session.sid] = self.session
            for cookie in self.cookies.output().splitlines():
                regex = r"^([^:]+): (.+=.*)$"
                matches = re.match(regex, cookie)
                self.response_headers.append((matches.group(1), matches.group(2)))
            logger.debug("Reached this part of the code")

        # Send all headers
        for header in self.response_headers:
            self.send_header(*header)
            if header[0] == "Content-Type":
                contentTypeSent = True

        # We have to have the Content-Type header, so if it's not present, we assume it's HTML
        # Because in this case it's us who's encoding this, we can safely specify the encoding
        if not contentTypeSent:
            if self.response_content_type == "text/html":  # REVIEW: HTML? Maybe something else?
                self.response_content_type += "; charset=" + encoding
            self.send_header("Content-Type", self.response_content_type)

        # Finish up the response
        self.end_headers()
        self.wfile.write(data)

        # We just sent the data, mark as done.
        self.done = True

    def process_request_body(self):
        pure_path = pure_path_pattern.match(self.path).group(1)
        if pure_path in self.web_server.accept_content_types['POST'].keys():
            self.acceptable_types = self.web_server.accept_content_types['POST'][pure_path]

        body = {}
        files = {}
        # Get the content length to read
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length != 0:
            # Now we read the whole POST body in parts.
            # First, we check the content type
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

        self.post_data = body
        self.post_files = files

    def parse_request_body(self, content_type, content_type_raw, content_length) -> Tuple[Dict, Dict]:
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
            _, c_data = parse_header(content_type_raw)
            bytestring = self.rfile.read(content_length)

            # === Let the CGI module handle the multipart parse.
            # HACK: the cgi module requires the boundary to be in bytes, the artifact of python 2
            # noinspection PyTypeChecker
            c_data['boundary'] = bytes(c_data['boundary'], 'utf-8')  # type: ignore
            c_data['CONTENT-LENGTH'] = content_length
            # noinspection PyTypeChecker
            form_data = parse_multipart(io.BytesIO(bytestring), c_data)  # type: ignore
            # ==================================================

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
        return {}, {}
