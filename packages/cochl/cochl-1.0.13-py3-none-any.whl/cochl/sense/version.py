import warnings

from . import __version__
from .http_request import HttpResponse, HttpRequest, HttpException


def check_latest_lib_version(host: str):
    url: str = f'{host}/client-libraries/versions'

    try:
        response: HttpResponse = HttpRequest.get(url)
        if response.status_code == 200:
            supported_versions: list = response.json().get('supported_versions')

            if __version__ not in supported_versions:
                warnings.warn(
                    f'Warning! The library version is outdated. '
                    f'Please upgrade the library: supported versions {", ".join(supported_versions)}',
                    stacklevel=3
                )
        else:
            pass
    except HttpException as _e:
        pass
