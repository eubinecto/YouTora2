import logging
from logging import Logger
from typing import List

from pymongo.collection import Collection

from .builders import CaptionBuilder
from .dloaders import VideoDownloader
from .models import Channel, Video
from .parsers import HTMLParser, ChannelHTMLParser, MLGlossRawHTMLParser

from ..elastic.main import Index
from ..mongo.settings import YoutoraDB, CorporaDB

# for splitting the videos into batches.
import numpy as np

from pymongo.errors import DuplicateKeyError, BulkWriteError

import sys

# global logger setting
# https://stackoverflow.com/questions/20333674/pycharm-logging-output-colours/45534743
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class Store:
    """
    all the main scripts for storing youtora_coll
    """
    # process batch size
    BATCH_SIZE = 10

    youtora_db: YoutoraDB = None
    corpora_db: CorporaDB = None

    @classmethod
    def store_corpora_db(cls):
        """
        1. ml gloss raw
        2. ml gloss
        3. (later) idiom dict.
        """
        # init the client
        logger = logging.getLogger("store_corpora_db")
        cls.corpora_db = CorporaDB()
        # get the from parser
        ml_gloss_raw_list = MLGlossRawHTMLParser.parse_ml_gloss_raw()
        docs = [
            {
                '_id': ml_gloss_raw.id,
                'word': ml_gloss_raw.word,
                "desc": ml_gloss_raw.desc,
                "category": ml_gloss_raw.category
            }
            for ml_gloss_raw in ml_gloss_raw_list
        ]
        cls._store_many(cls.corpora_db.ml_gloss_raw_coll,
                        docs=docs,
                        rep_id="ml_gloss_raw",
                        logger=logger)

    @classmethod
    def store_youtora_db(cls,
                         channel_url: str,
                         lang_code: str,
                         os: str = "mac"):
        """
        scrapes the desired information from the given channel url
        this is the main function to be used
        and stores it in the local mongoDB.
        :param channel_url:
        :param lang_code: the language of the channel. need this info on query time.
        :param os:
        """
        # check  pre-condition
        assert lang_code in CaptionBuilder.LANG_CODES_TO_COLLECT, "the lang code is invalid"
        logger = logging.getLogger("store_youtora_db")
        # init the clients
        cls.youtora_db = YoutoraDB()

        # get the driver
        driver = HTMLParser.get_driver(is_silent=True,
                                       is_mobile=True,
                                       os=os)
        try:
            # try scraping the channel
            # this will get the video ids of all uploaded videos
            channel = ChannelHTMLParser.parse_channel(channel_url, lang_code, driver=driver)
        finally:
            # always quit the driver regardless of what happens
            logger.info("quitting the selenium driver")
            driver.quit()

        # split the video ids into batches
        batches = np.array_split(channel.vid_id_list, cls.BATCH_SIZE)
        for idx, batch in enumerate(batches):
            vid_gen = VideoDownloader.dl_videos_lazy(vid_id_list=batch,
                                                     batch_info="current={}/total={}"
                                                     .format(idx + 1, len(batches)))
            for video in vid_gen:   # dl and iterate over each video in this batch
                if not video.captions:
                    logger.info("SKIP: skipping storing the video because it has no captions at all")
                    continue
                # store video, captions, and tracks
                cls._store_video(video)
                cls._store_captions_of(video)
                cls._store_tracks_of(video)
                # on storing everything, store the indices as well
                # this should be done on mongo db side, but as of right now, do it this way
                Index.index_tracks(channel=channel, videos=[video])
        else:
            # on storing all batches, store the channel. channel is stored at the end.
            cls._store_channel(channel=channel)

    @classmethod
    def _store_channel(cls, channel: Channel):
        """
        store the given channel in MongoDB.
        :param channel:
        :return:
        """
        logger = logging.getLogger("_store_channel")
        # build the doc
        doc = {
            "_id": channel.id,
            "url": channel.url,
            "title": channel.title,
            "subs": channel.subs,
            "lang_code": channel.lang_code
        }
        # store the channel
        cls._store_one(coll=cls.youtora_db.channel_coll,
                       doc=doc,
                       rep_id=channel.id,
                       logger=logger)

    @classmethod
    def _store_video(cls, video: Video):
        """
        store the given video in MongoDB.
        :param video:
        :return:
        """
        logger = logging.getLogger("_store_videos")
        # downloading the video will be initiated here
        doc = {
            # should add this field
            "_id": video.id,
            "parent_id": video.parent_id,
            "url": video.url,
            "title": video.title,
            "publish_date": video.publish_date,
            "views": video.views,
            "likes": video.likes,
            "dislikes": video.dislikes,
            "category": video.category
        }  # doc

        # store the video
        cls._store_one(coll=cls.youtora_db.video_coll,
                       doc=doc,
                       rep_id=video.id,
                       logger=logger)

    @classmethod
    def _store_captions_of(cls, video: Video):
        """
        store all tracks of the given video in MongoDB.
        :param video:
        :return:
        """
        logger = logging.getLogger("_store_captions_of")
        docs = list()
        for caption in video.captions:
            doc = {
                # video is the parent of caption
                "_id": caption.id,
                "parent_id": caption.parent_id,
                "url": caption.url,
                "lang_code": caption.lang_code,
                "is_auto": caption.is_auto
            }
            docs.append(doc)
            del caption  # memory management
        # store all captions
        cls._store_many(coll=cls.youtora_db.caption_coll,
                        docs=docs,
                        rep_id=video.id,
                        logger=logger)

    @classmethod
    def _store_tracks_of(cls, video: Video):
        """
        store all tracks of the given video in MongoDB.
        """
        logger = logging.getLogger("_store_tracks_of")
        docs = list()
        for caption in video.captions:
            for track in caption.tracks:
                doc = {
                        "_id": track.id,
                        "parent_id": track.parent_id,
                        "start": track.start,
                        "duration": track.duration,
                        "content": track.content,
                        "prev_id": track.prev_id,
                        "next_id": track.next_id,
                        "context": track.context
                }
                docs.append(doc)
                del track  # memory management
        # store all tracks
        cls._store_many(coll=cls.youtora_db.track_coll,
                        docs=docs,
                        rep_id=video.id,
                        logger=logger)

    @classmethod
    def _store_one(cls,
                   coll: Collection,
                   doc: dict,
                   rep_id: str,
                   logger: Logger):
        try:
            coll.insert_one(document=doc)
        except DuplicateKeyError:
            # logger.warning(str(dke))
            # delete the channel and then reinsert
            coll.delete_one(filter={"_id": doc["_id"]})
            coll.insert_one(document=doc)
            logger.warning("overwritten: " + rep_id)
        else:
            logger.info("stored: " + rep_id)

    @classmethod
    def _store_many(cls,
                    coll: Collection,
                    docs: List[dict],
                    rep_id: str,
                    logger: Logger):
        try:
            # insert all tracks
            coll.insert_many(documents=docs)
        except BulkWriteError:
            # logger.warning(str(bwe))
            # delete and overwrite tracks
            coll.delete_many(filter={"_id": {"$in": [doc["_id"] for doc in docs]}})
            coll.insert_many(documents=docs)
            logger.warning("all overwritten for: " + rep_id)
        else:
            logger.info("all stored for: " + rep_id)
