import os

from timhatdiehandandermaus_sdk import TimApi

token = os.getenv("API_TOKEN")
api = TimApi(token)
queue = api.queue()

print(*api.fuzzy_search_movie(query="Grizzly"), sep="\n")
# print(api.mark_movie_as_watched(queue_id="b8638990-9965-4a3d-a8a5-d156a41bdae4"))
