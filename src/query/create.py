
# for creating youtora
from src.es.restAPIs.idxAPIs.idxManagement import CreateIdxAPI


def create_youtora_idx():
    """
    creates the youtora index with the given configurations
    """
    # keyword data type: only searchable by tis exact value
    # https://www.elastic.co/guide/en/elasticsearch/reference/current/keyword.html
    # schema for the index above is defined here
    mappings = {
        "properties": {
            "channel": {
                "properties": {
                    "channel_url": {
                        "type": "keyword"  # 이건 필요없을 수도.
                    },
                    "uploader": {
                        "type": "keyword"
                    },  # creator
                    "subs": {
                        # is used with ranking
                        "type": "rank_feature"
                    }  # subs
                }  # properties
            },  # channel
            "video": {
                "properties": {
                    "vid_title": {
                        "type": "text"
                    },  # vid_title
                    "upload_date": {
                        "type": "date"
                    },  # upload_date
                    "views": {
                        "type": "rank_feature"
                    },  # views
                    "likes": {
                        "type": "rank_feature",
                    },  # likes
                    "dislikes": {
                        "type": "rank_feature",
                        # correlates negatively
                        "positive_score_impact": False
                    },  # dislikes
                    "l_to_d": {
                        "type": "rank_feature",
                    }
                }  # properties
            },  # video
            "caption": {
                "properties": {
                    "caption_url": {
                        "type": "keyword"
                    },
                    "caption_type": {
                        "type": "keyword"
                    },
                    "lang_code": {
                        "type": "keyword"
                    }
                }  # properties
            },  # caption
            "track": {
                "properties": {
                    "start": {
                        "type": "double"
                    },
                    "duration": {
                        "type": "double"
                    },
                    "text": {
                        "type": "text"
                    }
                }  # properties
            },  # track
            # note: the _parent thing is deprecated in elastic search 7.
            "youtora_relations": {
                "type": "join",  # join data type
                "relations": {
                    # a channel is a parent of video
                    "channel": "video",
                    "video": "caption",
                    "caption": "track"
                }  # relations
            }  # youtora_relations
        }  # properties
    }  # mappings_config

    # call to es
    CreateIdxAPI.create_idx(index="youtora",
                            mappings=mappings)