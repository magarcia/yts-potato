import requests
from datetime import datetime

from flask import Flask, jsonify, request
from werkzeug.contrib.cache import SimpleCache


url = "https://yts.ag/api/v2/list_movies.json?query_term="

def get_torrents(query):
    response = {"results": [], "total_results": 0}
    if query is None:
        return response

    r = requests.get(url + query)

    if r.status_code != 200:
        return {}

    data = r.json()['data']

    if data['movie_count'] < 1:
        return response

    for movie in data['movies']:
        for torrent in movie['torrents']:
            response['results'].append({
                "release_name": movie['title'] + " (DVD-Rip)",
                "torrent_id": movie['id'],
                "details_url": "http://www.imdb.com/title/" + movie['imdb_code'],
                "download_url": torrent['url'],
                "imdb_id": movie["imdb_code"],
                "freeleech": True,
                "type": "movie",
                "size": torrent["size_bytes"] * 1e-6,
                "leechers": torrent['peers'],
                "seeders": torrent['seeds'],
                "publish_date": datetime.strptime(torrent["date_uploaded"], "%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%dT%H:%M:%SZ')
            })
    response['total_results'] = len(response['results'])

    return response

app = Flask(__name__)
cache = SimpleCache()


@app.route('/')
def index():
    query = request.args.get('imdbid')
    if query is None:
        query = request.args.get('search')

    res = cache.get(query)
    if res != None:
        return res

    res = jsonify(get_torrents(query))
    cache.set(query, res, timeout=24 * 60 * 60)
    return res


if __name__ == '__main__':
    app.run(host= '0.0.0.0', debug=False)
