# the models that I'll be using.
from typing import List

from .models import Channel, Video, Caption, Track
# how do I use type aliases?
import xmltodict

# for getting the xml caption from timed text api.
import requests

# use youtube_dl for getting the automatic captions
import youtube_dl

# to be raised when no caption was found
from .errors import CaptionNotFoundError

# for escaping character reference entities
import html


# if you give it a channel url, you can get a list of videos... hopefully?
class ChannelDownloader:
    @classmethod
    def dl_channel(cls, channel_url: str) -> Channel:
        pass


class VideoDownloader:
    # get all of the captions, whether it be manual or auto.
    VIDEO_DL_OPTS = {'writesubtitles': True,
                     'allsubtitles': True,
                     'writeautomaticsub': True}

    @classmethod
    def dl_video(cls, vid_url: str) -> Video:
        """
        given a url, returns the meta data of the channel
        :param vid_url: the url of the video
        :return: a Video object
        """
        # get the info.
        with youtube_dl.YoutubeDL(cls.VIDEO_DL_OPTS) as ydl:
            info = ydl.extract_info(url=vid_url, download=False)

        # access the results
        vid_id = info['id']
        title = info['title']
        channel_id = info['channel_url']
        upload_date = info['upload_date']
        subtitles = info['subtitles']
        auto_captions = info['automatic_captions']

        # asserting: these four must not be None
        assert vid_id is not None, "vid_id is required"
        assert title is not None, "title is required"
        assert channel_id is not None, "channel_id is required"
        # I might need upload date to sort by recency.
        assert upload_date is not None, "upload_date is required"

        captions = dict()
        # try getting caption of type manual
        try:
            caption_type = 'manual'
            captions[caption_type] = CaptionDownloader.dl_caption(vid_id=vid_id,
                                                                  video_subtitles=subtitles,
                                                                  video_auto_captions=auto_captions,
                                                                  caption_type=caption_type)
        except CaptionNotFoundError as ce:
            print(ce)
        else:
            # on successful downloading
            print("MANUAL FOUND: {}".format(title))

        # try getting the caption of type manual
        try:
            caption_type = 'auto'
            captions[caption_type] = CaptionDownloader.dl_caption(vid_id=vid_id,
                                                                  video_subtitles=subtitles,
                                                                  video_auto_captions=auto_captions,
                                                                  caption_type=caption_type)
        except CaptionNotFoundError as ce:
            print(ce)
        else:
            # on successful downloading
            print("AUTO FOUND: {}".format(title))

        # returns a video object with the properties above
        return Video(vid_id,
                     title,
                     channel_id,
                     upload_date,
                     captions)


class CaptionDownloader:

    # the caption types defined
    CAPTION_TYPES = ("manual", "auto")

    # list of caption formats
    FORMAT_IDX = {
        'srv1': 0,
        'srv2': 1,
        'srv3': 2,
        'ttml': 3,
        'vtt': 4
    }

    @classmethod
    def dl_caption(cls,
                   vid_id,
                   video_subtitles,
                   video_auto_captions,
                   caption_type: str,
                   lang_code: str = 'en'):
        """
        extract the caption from the video object
        :param vid_id:
        :param video_subtitles:
        :param video_auto_captions:
        :param caption_type: manual = manually written, auto = ASR. the default is auto.
        :param lang_code: default is english
        :return: a caption object
        """
        # input check - must be either None, "auto", "manual"
        if caption_type not in cls.CAPTION_TYPES:
            raise ValueError(caption_type)

        # set the desired caption format in the CaptionScraper class.
        format_idx = cls.FORMAT_IDX[TrackDownloader.CAPTION_FORMAT]

        # this is initially None
        caption_url = None

        if caption_type == "manual":
            if lang_code in video_subtitles:  # manual exists
                caption_url = video_subtitles[lang_code][format_idx]['url']
        elif caption_type == "auto":  # auto exists
            if lang_code in video_auto_captions:
                caption_url = video_auto_captions[lang_code][format_idx]['url']

        # Note: a None is a singleton object.
        # there can only be 1 None.
        # So whatever variable that is assigned to None keyword
        # refers to the same memory location. ("NULL" in C)
        # so it makes sense to use is operator rather than equality operator.
        if caption_url is None:
            raise CaptionNotFoundError("NOT FOUND: caption type={}, lang code={}"\
                                       .format(caption_type, lang_code))

        # this will be the id of each caption
        caption_comp_key = "|".join([vid_id, caption_type, lang_code])

        # get the tracks with the given caption url
        try:
            tracks = TrackDownloader.dl_tracks(caption_comp_key=caption_comp_key,
                                               caption_url=caption_url)
        except requests.exceptions.HTTPError as he:
            # print the error message
            print(he)
            # and tracks is an empty list
            tracks = list()

        return Caption(caption_comp_key=caption_comp_key,
                       caption_url=caption_url,
                       tracks=tracks)


class TrackDownloader:

    @classmethod
    def dl_tracks(cls,
                  caption_comp_key: str,
                  caption_url: str) -> List[Track]:
        """
        :param caption_comp_key: the key of the caption.
        :param caption_url: the url to download the track from.
        :return: a list of Track objects
        """
        # first, get the response
        response = requests.get(caption_url)

        # check if the response was erroneous
        response.raise_for_status()

        # get the xml. escape the character reference entities
        tracks_xml = html.unescape(response.text)

        # deserialize the xml to dict
        tracks_dict = xmltodict.parse(tracks_xml)
        # prepare a bucket for tracks
        tracks = list()

        # get the tracks
        for trackItem in tracks_dict['transcript']['text']:
            start = trackItem["@start"]
            duration = trackItem["@dur"]
            text = trackItem["#text"]
            track = Track(caption_comp_key, start, duration, text)
            tracks.append(track)
        return tracks

    # the caption format I'll be using
    CAPTION_FORMAT = 'srv1'
