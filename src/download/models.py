from typing import List, Dict


class Channel:
    # for saving memory space
    __slots__ = "_channel_id", \
                "_channel_url", \
                "_creator", \
                "_channel_theme", \
                "_vid_id_list"

    def __init__(self,
                 channel_id: str,
                 creator: str,
                 channel_theme: str,
                 vid_id_list: list):
        # key
        self._channel_id = channel_id

        self._channel_url = "http://www.youtube.com/channel/{}"\
                            .format(channel_id)

        self._creator = creator

        self._channel_theme = channel_theme

        # no reference to actual video objects
        # just reference video id's here. (in case there are too many videos to download)
        self._vid_id_list = vid_id_list

    # accessor methods
    # property decorator allows you to
    # access protected variable by just using the name of
    # the method.
    @property
    def channel_id(self):
        return self._channel_id

    @property
    def channel_url(self):
        return self._channel_url

    @property
    def creator(self):
        return self._creator

    @property
    def channel_theme(self):
        return self._channel_theme

    @property
    def vid_id_list(self):
        return self._vid_id_list

    def __str__(self) -> str:
        """
        overrides the dunder string method
        """
        return self._creator


class Track:
    __slots__ = '_track_comp_key', \
                '_start', \
                '_duration', \
                '_text'

    def __init__(self,
                 track_comp_key: str,
                 duration: float,
                 text: str):
        # comp key
        self._track_comp_key = track_comp_key
        self._start: float = float(track_comp_key.split("|")[-1])  # extract start
        self._duration = duration
        self._text = text

    # accessor methods
    @property
    def track_comp_key(self):
        return self._track_comp_key

    @property
    def start(self):
        return self._start

    @property
    def duration(self):
        return self._duration

    @property
    def text(self):
        return self._text

    # overrides dunder string method
    def __str__(self) -> str:
        """
        overrides the dunder string method
        """
        return self._track_comp_key


class Caption:

    __slots__ = '_caption_comp_key', \
                '_caption_type', \
                '_lang_code', \
                '_caption_url', \
                '_tracks'

    def __init__(self,
                 caption_comp_key: str,
                 caption_url: str,
                 tracks: List[Track]):
        """
        :param caption_url: the url from which the tracks can be downloaded
        :param tracks: the list of tracks that belongs to this caption (1 to 1)
        """
        self._caption_comp_key = caption_comp_key
        self._caption_type = caption_comp_key.split("|")[1]
        self._lang_code = caption_comp_key.split("|")[2]
        self._caption_url = caption_url
        # download the tracks on init of caption
        # list of track objects.
        self._tracks = tracks

    # accessor methods
    @property
    def caption_comp_key(self):
        return self._caption_comp_key

    @property
    def caption_type(self):
        return self._caption_type

    @property
    def lang_code(self):
        return self._lang_code

    @property
    def caption_url(self):
        return self._caption_url

    @property
    def tracks(self):
        return self._tracks

    # overrides dunder string method
    def __str__(self) -> str:
        """
        overrides the dunder string method
        """
        return self._caption_comp_key


class Video:

    # to save RAM space
    __slots__ = '_vid_id', '_vid_url', '_title', '_channel_id', '_upload_date', '_captions'

    def __init__(self,
                 vid_id: str,
                 title: str,
                 channel_id: str,
                 upload_date: str,
                 captions: Dict[str, Caption]):
        """
        :param vid_id: the unique id at the end of the vid url
        :param title: the title of the youtube video
        :param channel_id: the id of the channel this video belongs to
        :param upload_date: the uploaded date of the video
        :param captions: the dictionary of captions. keys are either auto or manual
        """
        # key
        self._vid_id = vid_id

        # build the url yourself... save the number of parameters.
        self._vid_url = "https://www.youtube.com/watch?v={}"\
                        .format(vid_id)

        self._title = title
        self._channel_id = channel_id
        self._upload_date = upload_date
        self._captions = captions

    # accessor methods
    @property
    def vid_id(self):
        return self._vid_id

    @property
    def vid_url(self):
        return self._vid_url

    @property
    def title(self):
        return self._title

    @property
    def channel_id(self):
        return self._channel_id

    @property
    def upload_date(self):
        return self._upload_date

    @property
    def captions(self):
        return self._captions

    # overrides the dunder string method
    def __str__(self):
        return self._title


# 이것도 재미있을 듯!
class Chapter:
    pass