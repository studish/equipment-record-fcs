#!/usr/bin/env python3

from utils import logger as logger
from webframework.RequestHandler import RequestHandler
from webframework import Session
import http.server
from typing import List, Dict, Callable, Any

# (host, port)
default_server_address = ("", 8000)


class Server:
    """
    Represents a web server
    """

    #              method   path  handler
    handlers: Dict[str, Dict[str, Callable]] = {}
    #                         method    path    types
    accept_content_types: Dict[str, Dict[str, List[str]]] = {}
    server: http.server.HTTPServer

    # Main storage for all of the sessions stored on the server
    #              sid->Session
    sessions: Dict[str, Session.Session]

    def __init__(
            self, server_class=http.server.HTTPServer, handler_class=RequestHandler
    ):
        super().__init__()
        for method in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
            self.handlers[method] = {}
            self.accept_content_types[method] = {}
        self.server = server_class(default_server_address, handler_class)
        if handler_class is RequestHandler:
            handler_class.web_server = self
        self.staticPaths = {}
        self.sessions = {}

    def __set_request_handler(self, method, path, handler, **kwargs):
        self.handlers[method][path] = handler
        if 'accept' in kwargs.keys():
            self.accept_content_types[method][path] = kwargs['accept']
        logger.debug(
            "Registered handler for {method} {path}: {handler}".format(method=method, path=path, handler=handler))

    def get(self, path, **kwargs):
        def _(handler):
            self.__set_request_handler("GET", path, handler, **kwargs)
            return handler

        return _

    def post(self, path: str, accept: List[str] = RequestHandler.SUPPORTED_TYPES, **kwargs: Dict[str, Any]) -> Callable:
        def _(handler: Callable) -> Callable:
            self.__set_request_handler("POST", path, handler, accept=accept, **kwargs)
            return handler

        return _

    def put(self, path, **kwargs):
        def _(handler):
            self.__set_request_handler("PUT", path, handler, **kwargs)
            return handler

        return _

    def delete(self, path, **kwargs):
        def _(handler):
            self.__set_request_handler("DELETE", path, handler, **kwargs)
            return handler

        return _

    def patch(self, path, **kwargs):
        def _(handler):
            self.__set_request_handler("PATCH", path, handler, **kwargs)
            return handler

        return _

    staticPaths: dict[str, str]

    def serveStatic(self, pathPrefix: str, localPath: str):
        self.staticPaths[pathPrefix.rstrip("/")] = localPath

    def listen(self, host=default_server_address[0], port=default_server_address[1]):
        self.server.server_address = (host, port)
        try:
            logger.info(f'listening at http://{"localhost" if not host else host}:{port}/')
            self.server.serve_forever()
        except KeyboardInterrupt:
            logger.info("Stopping the server...")
            self.server.server_close()
