import os
from typing import Optional, Union
from urllib.parse import quote_plus

from .http_request import HttpRequest, HttpResponse
from .config import APIConfig
from .exceptions import CochlSenseException


class SpeakerRecognition:
    def __init__(
            self,
            api_project_key: str,
            api_config: Optional[APIConfig] = None,
    ):
        if not api_project_key:
            raise ValueError(f'invalid project key "{api_project_key}"')
        if api_config is None:
            api_config = APIConfig(speaker_recognition=True)  # use default APIConfig

        self.project_key: str = api_project_key
        self.api_config: APIConfig = api_config

    @staticmethod
    def _result(resp: HttpResponse) -> Optional[Union[dict, list]]:
        try:
            resp_json: dict = resp.json()
        except ValueError as err:
            raise err

        if 'error' in resp_json and resp_json['error'] != '':
            raise CochlSenseException(resp_json['error'])

        if 'data' in resp_json:
            return resp_json['data']
        else:
            return None

    def get_all(self) -> Optional[Union[dict, list]]:
        return self._result(HttpRequest.get(self.api_config.get_speaker_recognition_host() + '/speakers', headers={
            'X-Api-Key': self.project_key,
        }))

    def add(self, speaker: str, file_paths: list[str]) -> Optional[Union[dict, list]]:
        if len(file_paths) > self.api_config.speaker_recognition_upload_max_file_count:
            raise CochlSenseException(
                'max upload file count is {}'.format(self.api_config.speaker_recognition_upload_max_file_count))

        for file_path in file_paths:
            if os.stat(file_path).st_size > self.api_config.speaker_recognition_upload_max_file_size:
                raise CochlSenseException(
                    'one of files is bigger than {} MB'.format(
                        self.api_config.speaker_recognition_upload_max_file_size / 1024 / 1024))

        return self._result(HttpRequest.post(self.api_config.get_speaker_recognition_host() + '/speaker', data={
            'speaker': speaker,
        }, headers={
            'X-Api-Key': self.project_key,
        }, files={
            'file01': open(file_paths[0], 'rb'),
            'file02': open(file_paths[1], 'rb'),
            'file03': open(file_paths[2], 'rb'),
            'file04': open(file_paths[3], 'rb'),
            'file05': open(file_paths[4], 'rb'),
            'file06': open(file_paths[5], 'rb'),
            'file07': open(file_paths[6], 'rb'),
            'file08': open(file_paths[7], 'rb'),
            'file09': open(file_paths[8], 'rb'),
            'file10': open(file_paths[9], 'rb'),
            'file11': open(file_paths[10], 'rb'),
            'file12': open(file_paths[11], 'rb'),
            'file13': open(file_paths[12], 'rb'),
            'file14': open(file_paths[13], 'rb'),
            'file15': open(file_paths[14], 'rb'),
            'file16': open(file_paths[15], 'rb'),
            'file17': open(file_paths[16], 'rb'),
            'file18': open(file_paths[17], 'rb'),
            'file19': open(file_paths[18], 'rb'),
            'file20': open(file_paths[19], 'rb'),
        }))

    def remove(self, speaker: str) -> Optional[Union[dict, list]]:
        return self._result(
            HttpRequest.delete(
                self.api_config.get_speaker_recognition_host() + '/speaker?speaker={}'.format(quote_plus(speaker)),
                headers={'X-Api-Key': self.project_key}))

    def recognize(self, file_path: str) -> Optional[Union[dict, list]]:
        if os.stat(file_path).st_size > self.api_config.speaker_recognition_upload_max_file_size:
            raise CochlSenseException(
                'file is bigger than {} MB'.format(self.api_config.speaker_recognition_upload_max_file_size / 1024))

        return self._result(HttpRequest.post(
            self.api_config.get_speaker_recognition_host() + '/speaker/recognition',
            headers={
                'X-Api-Key': self.project_key,
            }, files={
                'file': open(file_path, 'rb')
            })
        )
