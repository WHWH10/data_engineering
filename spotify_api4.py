import sys
import requests
import base64
import json
import logging
import pymysql

client_id = ""
client_secret = ""

host = "localhost"
port = 3306
username = "root"
database = "production"
password = ""

# 2021.04.15(목)
# FastCampus : Format


def main():

    try:
        conn = pymysql.connect(host=host, user=username, passwd=password,
                               db=database, port=port, use_unicode=True, charset='utf8')
        cursor = conn.cursor()
    except:
        logging.error("coult not connect to RDS")
        sys.exit(1)

    cursor.execute("SHOW TABLES")
    print(cursor.fetchall())

    # artist_id, genre 파라미터로 받아서 사용 많이 함
    # query = "INSERT INTO artist_genres (artist_id, genre) VALUES ('%s', '%s')" % (
    #     '2345', 'pop')
    query = "INSERT INTO artist_genres (artist_id, genre) VALUES ('{}', '{}')".format(
        '2345', 'hip-hop')
    cursor.execute(query)
    conn.commit()

    sys.exit(0)

    headers = get_headers(client_id, client_secret)

    params = {
        "q": "BTS",
        "type": "artist",
        "limit": "5"
    }

    r = requests.get("https://api.spotify.com/v1/search",
                     params=params, headers=headers)

    # print(r.text)
    # sys.exit(0)

    # print('----API SEARCH START-----')
    # print(r.status_code)
    # print(r.text)
    # print(r.headers)
    # sys.exit(0)

    try:
        r = requests.get("https://api.spotify.com/v1/search",
                         params=params, headers=headers)
    except:
        logging.error(r.text)
        sys.exit(1)

    r = requests.get("https://api.spotify.com/v1/search",
                     params=params, headers=headers)

    if r.status_code != 200:
        logging.error(json.loads(r.text))

        if r.status_code == 429:

            retry_after = json.loads(r.headers)['Retry-After']
            time.sleep(int(retry_after))

            r = requests.get("https://api.spotify.com/v1/search",
                             params=params, headers=headers)

        # access_token expired
        elif r.status_code == 401:

            headers = get_headers(client_id, client_secret)
            r = requests.get("https://api.spotify.com/v1/search",
                             params=params, headers=headers)

        else:
            sys.exit(1)

    # GET BTS ALBUMS
    # BTS ID : 3Nrfpe0tUJi4K4DXYWgMUX

    r = requests.get(
        "https://api.spotify.com/v1/artists/3Nrfpe0tUJi4K4DXYWgMUX/albums", headers=headers)

    raw = json.loads(r.text)

    total = raw['total']
    offset = raw['offset']
    limit = raw['limit']
    next = raw['next']

    # print(total)
    # print(offset)
    # print(limit)
    # print(next)
    # sys.exit(0)

    albums = []
    # print(len(raw['items']))
    albums.extend(raw['items'])

    # # 100개만 뽑아오겠음
    count = 0
    # while count < 100 and next:
    while next:

        r = requests.get(raw['next'], headers=headers)
        raw = json.loads(r.text)
        next = raw['next']
        print(next)

        albums.extend(raw['items'])
        count = len(albums)

    print(len(albums))


def get_headers(client_id, client_secret):
    print('working-----')

    endpoint = "https://accounts.spotify.com/api/token"
    encoded = base64.b64encode("{}:{}".format(
        client_id, client_secret).encode('utf-8')).decode('ascii')

    headers = {
        "Authorization": "Basic {}".format(encoded)
    }

    payload = {
        "grant_type": "client_credentials"
    }

    r = requests.post(endpoint, data=payload, headers=headers)

    # print(r.status_code)
    # print(r.text)
    # print(r.headers)
    # sys.exit(0)

    access_token = json.loads(r.text)['access_token']

    headers = {
        "Authorization": "Bearer {}".format(access_token)
    }

    return headers


if __name__ == '__main__':
    main()
else:
    print('this script is being imported')
