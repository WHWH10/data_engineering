import sys
import requests
import base64
import json
import logging

client_id = ""
client_secret = ""


def main():
    headers = get_headers(client_id, client_secret)
    print(headers)

    params = {
        "q": "BTS",
        "type": "artist"
    }

    r = requests.get("https://api.spotify.com/v1/search",
                     params=params, headers=headers)

    print('----API SEARCH START-----')
    print(r.status_code)
    print(r.text)
    print(r.headers)


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
