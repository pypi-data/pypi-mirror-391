import io
import json as j
import mimetypes
import os
import random
import socket
import ssl
from datetime import datetime
from http.client import HTTPConnection, HTTPSConnection, HTTPException, HTTPResponse
from typing import Optional, Union
from urllib.parse import ParseResult, urlparse, urlencode, parse_qsl


class HttpException(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message: str = message


class _HTTPConn:
    def __init__(self, url: str, timeout: Optional[float] = None):
        self.url: str = url
        self.timeout: float = timeout

        self.parse_result: ParseResult = urlparse(self.url)
        self.path: str = self.parse_result.path
        self.query: str = self.parse_result.query

        if self.parse_result.scheme.lower() == 'https':
            self.conn = HTTPSConnection(self.parse_result.hostname, self.parse_result.port, timeout=self.timeout,
                                        context=ssl.create_default_context())
        else:
            self.conn = HTTPConnection(self.parse_result.hostname, self.parse_result.port, timeout=self.timeout)

    def close(self):
        if self.conn is not None:
            self.conn.close()


class HttpResponse:
    def __init__(self, h: _HTTPConn, r: HTTPResponse):
        self.url = '{}://{}:{}{}'.format(h.parse_result.scheme, h.parse_result.hostname, h.parse_result.port, h.path)

        self.status_code: int = r.status
        self.status_text: str = r.reason

        self.headers: list[tuple[str, str]] = r.getheaders()
        self.content: bytes = r.read()

        self.content_type: str = ''
        self.encoding = ''

        content_type = r.headers.get('content-type', None)
        if content_type is not None:
            content_type_lower: str = content_type.lower()

            if ';' in content_type:
                content_type_lower_split = content_type_lower.split(';')
                self.content_type = content_type_lower_split[0]
                charset_encoding_lower = content_type_lower_split[1].lower()

                if '=' in charset_encoding_lower:
                    self.encoding = charset_encoding_lower.split('=')[1]
            else:
                self.content_type = content_type_lower

        self.text: str = ''
        if self.encoding != '':
            self.text = self.content.decode(self.encoding)

    def json(self) -> Optional[Union[dict, list]]:
        d: Optional[Union[dict, list]]

        try:
            d = j.loads(self.content)
        except ValueError as err:
            raise HttpException(str(err))

        return d


class HttpRequest:
    @staticmethod
    def _get_content_type(file_path: str):
        if not os.path.isfile(file_path):
            raise HttpException('not a file')

        if os.stat(file_path).st_size == 0:
            raise HttpException('an empty file')

        content_type: str = 'application/octet-stream'

        _type, _charset = mimetypes.guess_type(file_path)
        if _type is not None:
            if _charset is not None:
                content_type = '{}; charset={}'.format(_type, _charset)
            else:
                content_type = _type

        return content_type

    @staticmethod
    def _get_or_delete(method: str, url: str, params: Optional[dict] = None, headers: Optional[dict] = None,
                       timeout: Optional[float] = None):
        if headers is None:
            headers = {}

        h: Optional[_HTTPConn] = None
        try:
            h = _HTTPConn(url, timeout)

            _params_from_query: dict = {} if h.query == '' else dict(parse_qsl(h.query))
            _params_from_input: dict = {} if params is None else params
            _params = _params_from_query | _params_from_input

            qs: str = urlencode(_params)
            if qs != '':
                h.path += '?{}'.format(qs)

            h.conn.request(method, h.path, headers=headers)
            r = h.conn.getresponse()

            return HttpResponse(h, r)

        except socket.gaierror as get_addr_info_err:
            raise HttpException(str(get_addr_info_err))

        except ConnectionRefusedError as conn_refused_err:
            raise HttpException(str(conn_refused_err))

        except TimeoutError as timeout_err:
            raise HttpException(str(timeout_err))

        except ssl.SSLError as ssl_err:
            raise HttpException(str(ssl_err))

        except HTTPException as http_exc:
            raise HttpException(str(http_exc))

        finally:
            if h is not None:
                h.close()

    @classmethod
    def get(cls, url: str, params: Optional[dict] = None, headers: Optional[dict] = None,
            timeout: Optional[float] = None):
        return cls._get_or_delete('GET', url, params, headers, timeout)

    @classmethod
    def post(cls, url: str, data: Optional[dict] = None, headers: Optional[dict] = None, files: dict = None,
             json: Optional[Union[dict, list]] = None, timeout: Optional[float] = None):

        if headers is None:
            headers = {}

        if isinstance(json, dict) or isinstance(json, list):
            body: str = j.dumps(json)
            headers['Content-Length'] = str(len(body))

            if 'Content-Type' not in headers:
                headers['Content-Type'] = 'application/json; charset=utf-8'

        elif isinstance(files, dict):
            boundary = 'boundary_{}_{}'.format(
                datetime.now().strftime('%Y%m%d%H%M%S%f'), random.randint(100000, 999999))
            multi_parts: list[bytes] = []

            if isinstance(data, dict):
                for form_name, value in data.items():
                    multi_parts.append(f'--{boundary}\r\n'.encode())
                    multi_parts.append(
                        f'Content-Disposition: form-data; name="{form_name}";\r\n\r\n{value}\r\n'.encode())

            for form_name, file in files.items():
                multi_parts.append(f'--{boundary}\r\n'.encode())
                multi_parts.append(f'Content-Disposition: form-data; '
                                   f'name="{form_name}"; filename="{os.path.basename(file.name)}"\r\n'.encode())
                multi_parts.append(f'Content-Type: {cls._get_content_type(file.name)}\r\n\r\n'.encode())
                multi_parts.append(file.read())
                multi_parts.append('\r\n'.encode())
                file.close()

            multi_parts.append(f'--{boundary}--\r\n'.encode())
            body: bytes = b''.join(multi_parts)

            headers['Content-Type'] = 'multipart/form-data; boundary={}'.format(boundary)
            headers['Content-Length'] = str(len(body))

        elif isinstance(data, dict):
            body = urlencode(data)
            headers['Content-Length'] = str(len(body))

            if 'Content-Type' not in headers:
                headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=utf-8'

        else:
            raise HttpException('invalid request')

        h: Optional[_HTTPConn] = None
        try:
            h = _HTTPConn(url, timeout)
            if h.query != '':
                h.path += '?' + h.query

            h.conn.request('POST', h.path, body, headers)
            r = h.conn.getresponse()

            return HttpResponse(h, r)

        except socket.gaierror as get_addr_info_err:
            raise HttpException(str(get_addr_info_err))

        except ConnectionRefusedError as conn_refused_err:
            raise HttpException(str(conn_refused_err))

        except TimeoutError as timeout_err:
            raise HttpException(str(timeout_err))

        except ssl.SSLError as ssl_err:
            raise HttpException(str(ssl_err))

        except HTTPException as http_exc:
            raise HttpException(str(http_exc))

        finally:
            if h is not None:
                h.close()

    @staticmethod
    def put(url: str, data=None, headers: Optional[dict] = None, json: Optional[Union[dict, list]] = None,
            timeout: Optional[float] = None):

        if headers is None:
            headers = {}

        if isinstance(json, dict) or isinstance(json, list):
            body = j.dumps(json)
            headers['Content-Length'] = str(len(body))

            if 'Content-Type' not in headers:
                headers['Content-Type'] = 'application/json; charset=utf-8'

        elif isinstance(data, dict):
            body = urlencode(data)
            headers['Content-Length'] = str(len(body))

            if 'Content-Type' not in headers:
                headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=utf-8'

        elif isinstance(data, io.IOBase):
            body = data.read()
            data.close()

            headers['Content-Type'] = 'application/octet-stream'
            headers['Content-Length'] = str(len(body))

        else:
            raise HttpException('data is required')

        h: Optional[_HTTPConn] = None
        try:
            h = _HTTPConn(url, timeout)
            if h.query != '':
                h.path += '?' + h.query

            h.conn.request('PUT', h.path, body, headers)
            r = h.conn.getresponse()

            return HttpResponse(h, r)

        except socket.gaierror as get_addr_info_err:
            raise HttpException(str(get_addr_info_err))

        except ConnectionRefusedError as conn_refused_err:
            raise HttpException(str(conn_refused_err))

        except TimeoutError as timeout_err:
            raise HttpException(str(timeout_err))

        except ssl.SSLError as ssl_err:
            raise HttpException(str(ssl_err))

        except HTTPException as http_exc:
            raise HttpException(str(http_exc))

        finally:
            if h is not None:
                h.close()

    @classmethod
    def delete(cls, url: str, params: Optional[dict] = None, headers=None, timeout: Optional[float] = None):
        return cls._get_or_delete('DELETE', url, params, headers, timeout)
