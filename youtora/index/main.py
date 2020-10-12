# from typing import List, Generator
#
#
# from elasticsearch import Elasticsearch
#
#
# class Search:
#     """
#     move this to the api layer. don't put this here.
#     """
#     es_client: Elasticsearch = None
#
#     @classmethod
#     def search_tracks(cls,
#                       content: str,
#                       chan_lang_code: str = None,
#                       caption_lang_code: str = None,
#                       is_auto: bool = None,
#                       views_boost: int = 2,
#                       like_ratio_boost: int = 2,
#                       subs_boost: int = 2,
#                       from_: int = 0,
#                       size: int = 10) -> dict:
#         # init the client
#         cls.es_client = Elasticsearch(HOSTS)
#         # build the search query
#         search_query = cls._build_search_query(content,
#                                                chan_lang_code,
#                                                caption_lang_code,
#                                                is_auto,
#                                                views_boost,
#                                                like_ratio_boost,
#                                                subs_boost)
#         # get the search result
#         srch_res_json = cls.es_client.search(body=search_query,
#                                              index=YOUTORA_IDX_NAME,
#                                              from_=from_,
#                                              size=size)
#         # collect all the results!
#         results = list()
#         for hit in srch_res_json['hits']['hits']:
#             # gather this up
#             tracks = list()
#             vid_id = hit['_source']['caption']['video']['_id']
#             curr_start = int(hit['_source']['start'])
#             curr_track = {
#                     'content': hit['_source']['content'],
#                     'url': "https://youtu.be/{}?t={}".format(vid_id, curr_start)
#             }  # match
#             tracks.append(curr_track)
#             # get the prev_id, next_id
#             prev_id = hit['_source'].get('prev_id', None)
#             next_id = hit['_source'].get('next_id', None)
#             if prev_id:
#                 prev_json = cls.es_client.get(index=YOUTORA_IDX_NAME, id=prev_id)
#                 prev_start = int(prev_json['_source']['start'])
#                 prev_track = {
#                     'content': prev_json['_source']['content'],
#                     'url': "https://youtu.be/{}?t={}".format(vid_id, prev_start)
#                 }
#                 tracks.insert(0, prev_track)
#
#             if next_id:
#                 next_json = cls.es_client.get(index=YOUTORA_IDX_NAME, id=next_id)
#                 next_start = int(next_json['_source']['start'])
#                 next_track = {
#                     'content': next_json['_source']['content'],
#                     'url': "https://youtu.be/{}?t={}".format(vid_id, next_start)
#                 }
#                 tracks.append(next_track)
#             res = {
#                 'tracks': tracks,
#                 'highlight': hit['highlight'],  # add highlight
#                 'features': {
#                     'caption': hit['_source']['caption'],
#                 }
#             }  # the search data
#             results.append(res)
#
#         return_dict = {
#             "meta": srch_res_json['hits']['total']['value'],
#             "data": results
#         }
#         return return_dict
#
#     @classmethod
#     def _build_search_query(cls,
#                             content: str,
#                             chan_lang_code: str,
#                             caption_lang_code: str,
#                             is_auto: bool,
#                             views_boost: int,
#                             like_ratio_boost: int,
#                             subs_boost: int) -> dict:
#         # build the filter
#         filter_list = list()
#         # if is_auto is given
#         if is_auto is not None:
#             filter_list.append(
#                 {
#                     "term": {
#                         "caption.is_auto": is_auto
#                     }
#                 }
#             )
#
#         # if a caption language is given
#         if caption_lang_code:
#             filter_list.append(
#                 {
#                     "term": {
#                         "caption.lang_code": caption_lang_code
#                     }
#                 }
#             )
#
#         # if the channel_raw language is given
#         if chan_lang_code:
#             filter_list.append(
#                 {
#                     "term": {
#                         "caption.video.channel_raw.lang_code": chan_lang_code
#                     }
#                 }
#             )
#
#         search_query = {
#             "bool": {
#                 "must": [
#                     {
#                         "match": {
#                             "content": content
#                         }
#                     },
#                     {
#                         "match": {
#                             "context": content  # match with the context as well
#                         }
#                     }
#                 ],
#                 "should": [
#                     {
#                         "rank_feature": {
#                             "field": "caption.video.views",
#                             "boost": views_boost
#                         }
#                     },
#                     {
#                         "rank_feature": {
#                             "field": "caption.video.like_ratio",
#                             "boost": like_ratio_boost
#                         }
#                     },
#                     {
#                         "rank_feature": {
#                             "field": "caption.video.channel_raw.subs",
#                             "boost": subs_boost
#                         }
#                     }
#                 ],
#                 "filter": filter_list
#             }
#         }
#
#         return {
#             "query": search_query,
#             "highlight": {
#                 "number_of_fragments": 0,
#                 "pre_tags": ["<strong>"],
#                 "post_tags": ["</strong>"],
#                 "fields": {
#                     "context": {}
#                 }
#             }
#         }
#
#
# class Index:
#     BATCH_SIZE = 100000
#     es_client: Elasticsearch = None
#
#     @classmethod
#     def index_tracks(cls,
#                      channel_raw: Channel,
#                      videos: List[Video]):
#         # init a client
#         cls.es_client = Elasticsearch(hosts=HOSTS)
#
#         for request_body in cls._gen_youtora_tracks(channel_raw, videos):
#             cls.es_client.bulk(body=request_body,
#                                index=YOUTORA_IDX_NAME,
#                                # immediately searchable
#                                refresh='true')
#
#     @classmethod
#     def _gen_youtora_tracks(cls,
#                             channel_raw: Channel,
#                             videos: List[Video]) -> Generator[list, None, None]:
#         # list of requests
#         request_body = list()
#         for video in videos:
#             for caption in video.captions:
#                 for track in caption.tracks:
#                     # build the query
#                     query = {
#                         "index": {
#                             "_index": YOUTORA_IDX_NAME,
#                             "_id": track.get_id(),
#                         }  # index
#                     }  # query
#                     # build the doc_body
#                     doc_body = {
#                         "start": track.start,
#                         "duration": track.duration,
#                         "content": track.content,
#                         "prev_id": track.prev_id,
#                         "next_id": track.next_id,
#                         "context": track.context,
#                         # "text_area_rel_img": track.text_area_rel_img,
#                         # "non_text_area_rel_img": 1 - track.text_area_rel_img,
#                         "caption": {
#                             "_id": caption.id,
#                             "is_auto": caption.is_auto,
#                             "lang_code": caption.lang_code,
#                             "video": {
#                                 "_id": video.id,
#                                 "views": video.views,
#                                 "publish_date_int": int("".join(video.publish_date.split("-"))),
#                                 "category": video.category,
#                                 "channel_raw": {
#                                     "_id": channel_raw.id,
#                                     "subs": channel_raw.subs,
#                                     "lang_code": channel_raw.lang_code
#                                 }  # channel_raw
#                             }  # video
#                         }  # caption
#                     }  # doc_body
#                     # add prev_id and next_id, only if they exist
#                     # add likes & dislikes only if they are greater than zero.
#                     if video.likes > 0 or video.dislikes > 0:
#                         if video.likes > 0:
#                             # add like cnt
#                             doc_body['caption']['video']['likes'] = video.likes
#                             # like ratio must be greater than zero as well
#                             doc_body['caption']['video']['like_ratio']: float \
#                                 = video.likes / (video.likes + video.dislikes)
#                         # dislike cnt
#                         if video.dislikes > 0:
#                             # add dislike cnt
#                             doc_body['caption']['video']['dislikes'] = video.dislikes
#                     # build the request
#                     request_body.append(query)
#                     request_body.append(doc_body)
#
#                     # if it reaches the batch size, then yield the batch
#                     if (len(request_body) / 2) == cls.BATCH_SIZE:
#                         yield request_body
#                         request_body.clear()  # empty the bucket
#         else:  # on successful iteration of all videos
#             if request_body:
#                 # if there are still more requests left, then yield it as well
#                 yield request_body