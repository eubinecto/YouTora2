from elasticsearch_dsl import (
    Document,
    Object,
    InnerDoc,
    Double,
    Text,
    Keyword,
    Boolean,
    RankFeature)
from elasticsearch_dsl.connections import connections

from config.settings import ELASTICSEARCH_DSL

# create a default connection to the host

es_client = connections.create_connection(hosts=ELASTICSEARCH_DSL['default']['hosts'])


class ChannelInnerDoc(InnerDoc):
    id = Keyword(required=True)
    subs = RankFeature()
    lang_code = Keyword()


class VideoInnerDoc(InnerDoc):
    id = Keyword(required=True)
    views = RankFeature()
    # likes = RankFeature()
    # dislikes = RankFeature()
    # like_ratio = RankFeature()
    publish_date_int = RankFeature()
    category = Keyword()  # should be a keyword
    title = Text()  # might come in handy for context2def later
    channel = Object(ChannelInnerDoc)


class CaptionInnerDoc(InnerDoc):
    id = Keyword(required=True)
    is_auto = Boolean()
    lang_code = Keyword()
    video = Object(VideoInnerDoc)


class GeneralDoc(Document):
    # define the fields here
    start = Double()
    duration = Double()
    content = Text()
    prev_id = Keyword()
    next_id = Keyword()
    context = Text()
    caption = Object(CaptionInnerDoc)

    class Index:
        name = "general_doc"
        # using the default settings for now.

    def save(self, **kwargs):
        # do something before save here, if you wish
        return super().save(**kwargs)


GeneralDoc.init()