import json
import os
import socket
import ssl
from http.client import HTTPSConnection, HTTPConnection, HTTPException
from typing import Optional
from urllib.parse import ParseResult, urlparse

from .exceptions import CochlSenseException

from .config import APIConfig


class CustomSound:
    def __init__(self, x_org_key: str, api_config: Optional[APIConfig] = None):
        if not x_org_key:
            raise ValueError(f'invalid organization key "{x_org_key}"')
        if api_config is None:
            api_config = APIConfig(custom_sound=True)  # use default APIConfig

        self.x_org_key: str = x_org_key
        self.api_config: APIConfig = api_config

    @staticmethod
    def _get_http_conn(parse_result: ParseResult, timeout: Optional[float] = None):
        if parse_result.scheme.lower() == 'https':
            return HTTPSConnection(parse_result.hostname, parse_result.port, timeout=timeout,
                                   context=ssl.create_default_context())
        else:
            return HTTPConnection(parse_result.hostname, parse_result.port, timeout=timeout)

    def _http_post_custom_sound(self, custom_sound_tag: str) -> Optional[dict]:
        parse_result: ParseResult = urlparse(self.api_config.get_custom_sound_host())
        http_conn = self._get_http_conn(parse_result)

        try:
            http_conn.request('POST', parse_result.path + '/custom_sound', json.dumps({
                'custom_sound_tag': custom_sound_tag,
            }), {
                'X-Org-Key': self.x_org_key,
                'Content-Type': 'application/json; charset=utf-8'
            })

            http_resp = http_conn.getresponse()
            http_resp_read: bytes = http_resp.read()

            resp_body: dict = {}
            if http_resp_read != '':
                resp_body = json.loads(http_resp_read)

            return {
                'status_code': http_resp.status,
                'status_text': http_resp.reason,
                'resp_headers': http_resp.getheaders(),
                'resp_body': resp_body,
            }

        except socket.gaierror as get_addr_info_err:
            return {'http_error': str(get_addr_info_err)}

        except ConnectionRefusedError as conn_refused_err:
            return {'http_error': str(conn_refused_err)}

        except TimeoutError as timeout_err:
            return {'http_error': str(timeout_err)}

        except ssl.SSLError as ssl_err:
            return {'http_error': str(ssl_err)}

        except HTTPException as http_exc:
            return {'http_error': str(http_exc)}

        except ValueError as val_err:
            return {'http_error': str(val_err)}

        finally:
            if http_conn is not None:
                http_conn.close()

    def _http_put_zip_file_to_aws_s3(self, s3_put_url: str, zip_file_path: str) -> Optional[dict]:
        parse_result: ParseResult = urlparse(s3_put_url)
        http_conn = self._get_http_conn(parse_result)

        try:
            http_conn.request('PUT', f'{parse_result.path}?{parse_result.query}', open(zip_file_path, 'rb'), {
                'Content-Type': 'application/octet-stream',
                'Content-Length': os.stat(zip_file_path).st_size
            })

            http_resp = http_conn.getresponse()

            return {
                'status_code': http_resp.status,
                'status_text': http_resp.reason,
            }

        except socket.gaierror as get_addr_info_err:
            return {'http_error': str(get_addr_info_err)}

        except ConnectionRefusedError as conn_refused_err:
            return {'http_error': str(conn_refused_err)}

        except TimeoutError as timeout_err:
            return {'http_error': str(timeout_err)}

        except ssl.SSLError as ssl_err:
            return {'http_error': str(ssl_err)}

        except HTTPException as http_exc:
            return {'http_error': str(http_exc)}

        except ValueError as val_err:
            return {'http_error': str(val_err)}

        finally:
            if http_conn is not None:
                http_conn.close()

    def _http_put_custom_sound_upload_finished(self, cs_api_url: str, x_org_key: str,
                                               custom_sound_id: int) -> Optional[dict]:
        parse_result: ParseResult = urlparse(cs_api_url)
        http_conn = self._get_http_conn(parse_result)

        try:
            http_conn.request('PUT', parse_result.path + '/custom_sound/upload/finished', json.dumps({
                'custom_sound_id': custom_sound_id,
            }), {
                'X-Org-Key': x_org_key,
                'Content-Type': 'application/json; charset=utf-8'
            })

            http_resp = http_conn.getresponse()
            http_resp_read: bytes = http_resp.read()

            resp_body: dict = {}
            if http_resp_read != '':
                resp_body = json.loads(http_resp_read)

            return {
                'status_code': http_resp.status,
                'status_text': http_resp.reason,
                'resp_headers': http_resp.getheaders(),
                'resp_body': resp_body,
            }

        except socket.gaierror as get_addr_info_err:
            return {'http_error': str(get_addr_info_err)}

        except ConnectionRefusedError as conn_refused_err:
            return {'http_error': str(conn_refused_err)}

        except TimeoutError as timeout_err:
            return {'http_error': str(timeout_err)}

        except ssl.SSLError as ssl_err:
            return {'http_error': str(ssl_err)}

        except HTTPException as http_exc:
            return {'http_error': str(http_exc)}

        except ValueError as val_err:
            return {'http_error': str(val_err)}

        finally:
            if http_conn is not None:
                http_conn.close()

    def upload(self, custom_sound_tag: str, zip_file_path: str) -> Optional[dict]:

        http_resp = self._http_post_custom_sound(custom_sound_tag)
        if 'http_error' in http_resp or 'resp_body' not in http_resp:
            raise CochlSenseException(http_resp['http_resp'])
        elif 'error' in http_resp['resp_body']:
            api_error: str = http_resp['resp_body']['error']
            if api_error != '':
                raise CochlSenseException(api_error)

        custom_sound_id: int = http_resp['resp_body']['data']['custom_sound_id']
        s3_put_url: str = http_resp['resp_body']['data']['s3_put_url']

        http_resp = self._http_put_zip_file_to_aws_s3(s3_put_url, zip_file_path)
        if 'http_error' in http_resp:
            raise CochlSenseException(http_resp['http_resp'])

        http_resp = self._http_put_custom_sound_upload_finished(
            self.api_config.get_custom_sound_host(),
            self.x_org_key,
            custom_sound_id
        )

        if 'http_error' in http_resp or 'resp_body' not in http_resp:
            raise CochlSenseException(http_resp['http_resp'])
        elif 'error' in http_resp['resp_body']:
            api_error: str = http_resp['resp_body']['error']
            if api_error != '':
                raise CochlSenseException(api_error)

        if 'data' in http_resp['resp_body']:
            return http_resp['resp_body']['data']
        else:
            return None
