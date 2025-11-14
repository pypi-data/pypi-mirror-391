import os

from cochl import Configuration, ApiClient, AudioSessionApi

from .config import APIConfig
from .event_detection import EventDetection
from .result import Result
from .speaker_recognition import SpeakerRecognition
from .version import check_latest_lib_version


class Client:
    """Client is used to predict an audio file with Cochl.Sense."""

    def __init__(
        self,
        api_project_key: str,
        api_config: APIConfig = None,
    ):
        if not api_project_key:
            raise ValueError(f'invalid project key "{api_project_key}"')
        if api_config is None:
            api_config = APIConfig()  # use default APIConfig

        self.project_key: str = api_project_key
        self.api_config: APIConfig = api_config

        # check client library version
        check_latest_lib_version(self.api_config.get_host())

    def get_official_tags(self):
        configuration = Configuration(host=self.api_config.host)
        configuration.api_key['API_Key'] = self.project_key

        api_client = AudioSessionApi(ApiClient(configuration))
        return api_client.get_official_tags()

    def predict(self, file_path: str) -> Result:
        """
        Predicts the given file.

        Args:
            file_path: Path to the file. For example, '/Users/user/file.mp3'
        """

        if not os.path.exists(file_path):
            raise FileNotFoundError(file_path)

        result = Result()

        event_detection = EventDetection(self.project_key, self.api_config)
        result.events = event_detection.predict(file_path)

        if not self.api_config.speaker_recognition:
            return result

        if '[Speech]' not in result.events.to_summarized_result():
            return result

        speaker_recognition = SpeakerRecognition(self.project_key, self.api_config)
        result.speakers = speaker_recognition.recognize(file_path)

        return result
