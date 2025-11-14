import base64
import os
import time
from typing import Optional

import soundfile
from .._openapi_client import ApiClient, Configuration, AudioChunk
from .._openapi_client.api.audio_session_api import AudioSessionApi
from .._openapi_client.models.created_session import CreatedSession
from .._openapi_client.models.session_type import SessionType
from .._openapi_client.models.create_session import CreateSession

from .config import APIConfig
from .exceptions import CochlSenseException, TimeoutException
from .result import EventDetectionResult, SoundTag, WindowResult
from .version import check_latest_lib_version

_supported_formats: list = ['mp3', 'wav', 'ogg']


class EventDetection:
    """EventClient is used to predict an audio file with Cochl.Sense."""

    def __init__(
        self,
        api_project_key: str,
        api_config: Optional[APIConfig] = None,
    ):
        if not api_project_key:
            raise ValueError(f"invalid project key '{api_project_key}'")
        if api_config is None:
            api_config = APIConfig()  # use default APIConfig

        self.project_key: str = api_project_key
        self.api_config: APIConfig = api_config
        self.internal_client = None

        # check client library version
        check_latest_lib_version(self.api_config.get_host())

    def predict(self, file_path: str, timeout: Optional[float] = None) -> EventDetectionResult:
        """
        Predicts the given file.

        Args:
            file_path: Path to the file. For example, "/Users/user/file.mp3"
            timeout: Maximum amount of seconds to wait until prediction of the given file is done.
        """

        if not os.path.exists(file_path):
            raise FileNotFoundError(file_path)

        self.internal_client = self._create_internal_client()

        # create Session
        # session_id = self._create_session(file_path)
        session = self._create_session(file_path)

        # upload file chunks
        with open(file_path, "rb") as file:
            chunk_sequence: int = 0
            while True:
                chunk = file.read(self.api_config.chunk_size.value)
                if not chunk:
                    # all bytes of the file has been processed
                    break

                self._upload_chunk(session.session_id, chunk_sequence, chunk)

                chunk_sequence += 1

        # get results
        results = self._get_all_results(session, timeout)

        return results

    def _create_internal_client(self) -> AudioSessionApi:
        if self.api_config and self.api_config.host:
            configuration = Configuration(host=self.api_config.host)
        else:
            configuration = Configuration()

        configuration.api_key['API_Key'] = self.project_key
        return AudioSessionApi(ApiClient(configuration))

    def _create_session(self, file_path: str) -> CreatedSession:
        """
        Returns:
            str: ID of the created session
        """
        file_name: str = os.path.basename(file_path)
        file_size: int = os.stat(file_path).st_size
        file_format: str = self._get_file_format(file_path)
        file_length: float = self._get_file_length(file_path)

        content_type = f'audio/{file_format.lower()}'

        default_sensitivity = self.api_config.sensitivity.default.value
        tags_sensitivity: dict = {}
        for tag_name, scale in self.api_config.sensitivity.by_tags.items():
            tags_sensitivity[tag_name] = scale.value

        resp: CreatedSession = self.internal_client.create_session(
            CreateSession(
                type=SessionType('file'),
                total_size=file_size,
                content_type=content_type,
                file_name=file_name,
                file_length=file_length,
                default_sensitivity=default_sensitivity,
                tags_sensitivity=tags_sensitivity,
            )
        )

        # return resp.session_id
        return resp

    def _upload_chunk(self, session_id: str, chunk_sequence: int, chunk: bytes):
        encoded: str = base64.b64encode(chunk).decode('utf-8')

        _resp = self.internal_client.upload_chunk(
            session_id=session_id,
            chunk_sequence=chunk_sequence,
            audio_chunk=AudioChunk(data=encoded),
        )

    def _get_all_results(self, session: CreatedSession, timeout: Optional[float] = None) -> EventDetectionResult:
        retry_count: int = 0
        data_count: int = 0
        frame_results: list[WindowResult] = []
        start_time = time.time()

        while True:
            # check if this whole function behaviour not complete within the given timeout
            if timeout is not None:
                if time.time() - start_time > timeout:
                    raise TimeoutException(session.session_id, timeout)

            _response = self.internal_client.get_results(
                session_id=session.session_id,
                offset=data_count,
                limit=1024,
            )
            response = _response.to_dict()

            state = response.get('state', None)
            has_more = response.get('has_more', None)
            if (state is None) or (has_more is None) or (type(has_more) is not bool):
                raise CochlSenseException(f'invalid Get Result API response: {response}')

            if state == 'error':
                error_msg = response.get('error', None)
                if not error_msg:
                    error_msg = 'Unexpected error occurred.'
                raise CochlSenseException(error_msg)

            elif state == 'pending' or state == 'in-progress':
                # retry after interval
                time.sleep(self._calculate_retry_interval(retry_count))
                continue

            elif state == 'done':
                retrieved = self._to_frame_results(response)
                frame_results.extend(retrieved)
                data_count += len(retrieved)

                # the loop continues only if the result is paginated
                if not has_more:
                    return EventDetectionResult(
                        session_id=session.session_id,
                        window_results=frame_results,
                        window_hop=session.window_hop,
                    )

            else:
                raise CochlSenseException(f'invalid Get Result API response state: {state}')

            # update loop conditions
            retry_count += 1

        return EventDetectionResult(
            session_id=session.session_id,
            window_results=frame_results,
            window_hop=session.window_hop,
        )

    def _get_results(self, session_id: str, offset: int, limit: int):
        response = self.internal_client.get_results(
            session_id=session_id,
            offset=offset,
            limit=limit,
        )
        return response

    @classmethod
    def _to_frame_results(cls, response: dict) -> list[WindowResult]:
        frame_results: list = []

        for item in response['data']:
            sound_tags = [
                SoundTag(
                    name=tag['name'],
                    probability=tag['probability'],
                )
                for tag in item['tags']
            ]
            frame_results.append(
                WindowResult(
                    start_time=item['start_time'],
                    end_time=item['end_time'],
                    sound_tags=sound_tags,
                )
            )

        return frame_results

    @classmethod
    def _calculate_retry_interval(cls, retry_count: int) -> float:
        return min(1.1**retry_count, 4.0)

    @classmethod
    def _get_file_format(cls, file_path: str) -> str:
        """
        Returns:
            str: File format in str ("mp3", "wav", "ogg")
        """
        try:
            info = soundfile.info(file_path)
            file_format = info.format.lower()
        except Exception as _e:
            raise ValueError(f'invalid file format "{file_path}", supported formats: {_supported_formats}')

        return file_format

    @classmethod
    def _get_file_length(cls, file_path: str) -> float:
        """Get the float seconds of the given file.

        Returns:
            float: Length of the file in second.
        """
        try:
            with soundfile.SoundFile(file_path) as f:
                num_frames = len(f)
                duration_seconds = num_frames / f.samplerate
                return duration_seconds
        except Exception as _e:
            raise ValueError(f'invalid file format "{file_path}", supported formats: {_supported_formats}')
