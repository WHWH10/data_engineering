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
# FastCampus : Duplicate Record 핸들링


def main():

    try:
        conn = pymysql.connect(host=host, user=username, passwd=password,
                               db=database, port=port, use_unicode=True, charset='utf8')
        cursor = conn.cursor()
    except:
        logging.error("coult not connect to RDS")
        sys.exit(1)

    headers = get_headers(client_id, client_secret)

    params = {
        "q": "BTS",
        "type": "artist",
        "limit": "5"
    }

    r = requests.get("https://api.spotify.com/v1/search",
                     params=params, headers=headers)
    raw = json.loads(r.text)
    print(raw['artists'].keys())

    print(raw['artists']['items'][0].keys())

    artist_raw = raw['artists']['items'][0]

    if(artist_raw['name'] == params['q']):
        artist = {
            'id': artist_raw['id'],
            'name': artist_raw['name'],
            'followers': artist_raw['followers']['total'],
            'popularity': artist_raw['popularity'],
            'url': artist_raw['external_urls']['spotify'],
            'image_url': artist_raw['images'][0]['url'],
        }
    ###############################################################

    insert_row(cursor, artist, 'artists')
    conn.commit()
    sys.exit(0)

    ###############################################################

    # query = """
    #     INSERT INTO artists (id, name, followers, popularity, url, image_url)
    #     VALUES ('{}', '{}', {}, {}, '{}', '{}')
    #     ON DUPLICATE KEY UPDATE id='{}', name='{}', followers={}, popularity={}, url='{}', image_url='{}'
    # """.format(
    #     artist['id'],
    #     artist['name'],
    #     artist['followers'],
    #     artist['popularity'],
    #     artist['url'],
    #     artist['image_url'],
    #     artist['id'],
    #     artist['name'],
    #     artist['followers'],
    #     artist['popularity'],
    #     artist['url'],
    #     artist['image_url']
    # )

    # print(query)
    cursor.execute(query)
    conn.commit()

    sys.exit(0)

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

################################################################


def insert_row(cursor, data, table):

    placeholders = ', '.join(['%s'] * len(data))
    columns = ', '.join(data.keys())
    key_placeholders = ', '.join(['{0}=%s'.format(k) for k in data.keys()])
    sql = "INSERT INTO %s ( %s ) VALUES ( %s ) ON DUPLICATE KEY UPDATE %s" % (
        table, columns, placeholders, key_placeholders)
    cursor.execute(sql, list(data.values())*2)


################################################################
if __name__ == '__main__':
    main()
else:
    print('this script is being imported')
