from typing import Optional

from . import APIConfig
from .config import WindowHop

TAG_NAME_OTHER = 'Others'
DEFAULT_IM = 0


class SoundTag:
    def __init__(self, name: str, probability: float):
        self.name = name
        self.probability = probability

    def __str__(self):
        return str(vars(self))

    def to_dict(self):
        return vars(self).copy()


class WindowResult:
    def __init__(self, start_time: float, end_time: float, sound_tags: list[SoundTag]):
        self.start_time = start_time
        self.end_time = end_time
        self.sound_tags = sound_tags

    def __str__(self):
        v = vars(self).copy()
        v['sound_tags'] = [vars(t) for t in v['sound_tags']]
        return str(v)

    def to_str(self, enabled_tags: Optional[list] = None):
        if enabled_tags is None:
            enabled_tags = []

        v = vars(self).copy()
        # v['sound_tags'] = [vars(t) for t in v['sound_tags']]

        _sound_tags: list = []
        for t in v['sound_tags']:
            if len(enabled_tags) == 0:
                _sound_tags.append(vars(t))
            elif t['name'] in enabled_tags:
                _sound_tags.append(vars(t))
            else:
                pass

        v['sound_tags'] = _sound_tags
        return str(v)

    def to_dict(self, enabled_tags: Optional[list] = None):
        if enabled_tags is None:
            enabled_tags = []

        v = vars(self).copy()
        # v['sound_tags'] = [st.to_dict() for st in self.sound_tags]

        _sound_tags: list = []
        for st in self.sound_tags:
            if len(enabled_tags) == 0:
                _sound_tags.append(st.to_dict())
            elif st.name in enabled_tags:
                _sound_tags.append(st.to_dict())
            else:
                pass

        v['sound_tags'] = _sound_tags
        return v


class EventDetectionResult:
    def __init__(
        self,
        session_id: str,
        window_results: list[WindowResult],
        window_hop: WindowHop,
    ):
        self.session_id: str = session_id
        self.window_results: list[WindowResult] = window_results
        self._window_hop: WindowHop = window_hop

    def to_dict(self, api_config: Optional[APIConfig] = None) -> dict:
        """
        Get results in form of a dict

        Example:
            results.to_dict()
            {
                'session_id': 'df1637ab-5478-455c-bff8-c7b90ff215c2',
                'window_results': [
                    {
                        'start_time': 0.0,
                        'end_time': 1.0,
                        'sound_tags': [
                            {'name': 'Gunshot', 'probability': 0.578891396522522},
                            {'name': 'Gunshot_single', 'probability': 0.578891396522522},
                        ],
                    },
                    {
                        'start_time': 0.5,
                        'end_time': 1.5,
                        'sound_tags': [
                            {'name': 'Others', 'probability': 0.0}
                        ],
                    },
                    {
                        'start_time': 1.0,
                        'end_time': 2.0,
                        'sound_tags': [
                            {'name': 'Others', 'probability': 0.0}
                        ],
                    },
                ]
            }
        """

        enabled_tags = []
        if api_config is not None:
            enabled_tags = api_config.enabled_tags

        return {
            'session_id': self.session_id,
            'window_results': [wr.to_dict(enabled_tags) for wr in self.window_results],
        }

    def to_summarized_result(
        self,
        interval_margin: int = 0,
        by_tags: dict[str, int] = None,
        enabled_tags: Optional[list] = None
    ) -> str:
        """
        Used to make your Cochl.Sense results understandable in a glance
        Useful for demo, human testing etc.

        Args:
            interval_margin: The default interval margin to apply to every tag that is not specified in 'by_tags'
            by_tags: The custom internal margin of each tag
            enabled_tags: if specified, only tags in enabled_tags will be shown

        Raises:
            ValueError: if the provided hop size is not supported

        Example:
            ... code-block:: python

            print(results.to_summarized_result(
                interval_margin=1,
                by_tags={'Speech': 5, 'Sing': 3}
            ))
        """
        result_summary = ResultSummary(
            hop_size=WindowHop.HOP_1s,
            default_im=interval_margin,
            tags_im=by_tags,
        )
        summarized_results = result_summary.minimize_details(self.window_results, enabled_tags)
        return summarized_results


class ResultSummary:
    """
    Example:

        ... code-block:: python

        result_summary = ResultSummary(
            tags_im={'Speech': 2}
        )
        summary = result_summary.minimize_details(window_results)
    """

    def __init__(
        self,
        default_im=DEFAULT_IM,
        hop_size=WindowHop.HOP_1s,
        tags_im: dict[str, int] = None,
    ):
        """
        Args:
            default_im: The default interval margin to apply to every tag that is not specified in 'tags_im'
            hop_size: The hop size that was used for inference
            tags_im: The custom internal margin of each tag

        Raises:
            ValueError: if the provided hop size is not supported
        """

        # if hop_size != WindowHop.HOP_500ms.second and hop_size != WindowHop.HOP_1s.second:
        #     raise ValueError('Hop size can only be 0.5 or 1')

        self.hop_size = hop_size
        self.default_im = default_im
        self.tags_im = tags_im
        self._buffer = {}
        self._file_mode = False
        self._tag_name_other = TAG_NAME_OTHER
        self._min_im = 0
        # if default_im == 0 and self.hop_size == WindowHop.HOP_500ms.second:
        #     self._min_im = -WindowHop.HOP_500ms.second

    def minimize_details(self, results: list[WindowResult] = None, enabled_tags: Optional[list] = None):
        """
        Used for file inference to loop over the results and provide a single result summary
        """
        if results is None:
            results = []

        if enabled_tags is None:
            enabled_tags = []

        self._file_mode = True
        output = ''

        for window_result in results:
            line = self.minimize_details_window(window_result, enabled_tags)
            if not line:
                continue

            output = self._append_line(output, line)

        for tag, (_, from_time, to_time) in self._buffer.items():
            line = f'At {from_time}-{to_time}s, [{tag}] was detected'

            if len(enabled_tags) == 0:
                output = self._append_line(output, line)
            elif tag in enabled_tags:
                output = self._append_line(output, line)
            else:
                pass

        self._file_mode = False
        return output

    def minimize_details_window(self, window_result: WindowResult, enabled_tags: Optional[list] = None):
        """
        This can be used as you loop over the results
        It will output a merge of the results in ranges
        """

        if enabled_tags is None:
            enabled_tags = []

        output = ''
        nb_line = 0

        start_time = window_result.start_time
        end_time = window_result.end_time
        treated_tags = []

        for tag in window_result.sound_tags:
            name = tag.name
            if name == self._tag_name_other:
                continue

            if len(enabled_tags) > 0 and name not in enabled_tags:
                continue

            if name in self._buffer:
                (_, from_time, _) = self._buffer[name]
                self._buffer[name] = (self._im(name), from_time, end_time)
            else:
                self._buffer[name] = (self._im(name), start_time, end_time)
            treated_tags.append(name)

        tags_to_remove = []
        for tag, (im, from_time, to_time) in self._buffer.items():
            if tag in treated_tags:
                continue

            im -= self.hop_size.second
            if im < self._min_im:
                line = f'At {from_time}-{to_time}s, [{tag}] was detected'
                nb_line += 1
                output = self._append_line(output, line)
                tags_to_remove.append(tag)
            else:
                self._buffer[tag] = (im, from_time, to_time)

        for tag in tags_to_remove:
            del self._buffer[tag]

        return output

    def clear_buffer(self):
        self._buffer.clear()

    def _im(self, tag):
        if self.tags_im is None:
            return self.default_im
        return self.tags_im.get(tag, self.default_im)

    @classmethod
    def _append_line(cls, result, line) -> str:
        if not result:
            return line
        return f'{result}\n{line}'


class SpeakerRecognitionResult:
    def __init__(self):
        self.idx: int = 0
        self.transcript: str = ''
        self.confidence: float = 0.0

        self.first_word_start_msec: int = 0
        self.first_word_start_time: str = ''

        self.last_word_end_msec: int = 0
        self.last_word_end_time: str = ''

        self.speaker_tag: int = 0
        self.speaker_name: str = ''
        self.speaker_score: float = 0.0


class Result:
    def __init__(self):
        self.events: Optional[EventDetectionResult] = None
        self.speakers: Optional[SpeakerRecognitionResult] = None

    def events_summarized(self, api_config: APIConfig):
        return self.events.to_summarized_result(api_config.default_interval_margin, api_config.tag_interval_margin,
                                                api_config.enabled_tags)
