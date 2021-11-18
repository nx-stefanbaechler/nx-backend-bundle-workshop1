#!/usr/bin/python3

import urllib.request
import json
import os
from dotenv import load_dotenv
import boto3

load_dotenv()


def main():
    domain = os.getenv('TARGET_DOMAIN')
    nodeid = os.getenv('TARGET_ID')
    lang = os.getenv('TARGET_LANG')

    #    s3 = boto3.resource('s3',
    #                        aws_access_key_id=ACCESS_ID,
    #                   aws_secret_access_key=ACCESS_KEY
    #                   )

    # get the paragraphs via drupals json api
    paragraph_json = json.loads(get_url_data('https://' + domain + lang
                                             + '/jsonapi/node/articulo?filter[drupal_internal__nid]=' + nodeid))
    for paragraph in paragraph_json['data'][0]['relationships']['field_adjuntos']['data']:
        if paragraph['type'] == 'paragraph--es7_media':
            media_json = json.loads(get_url_data('https://' + domain + lang + '/jsonapi/paragraph/es7_media/'
                                                 + paragraph['id']))
            for file in media_json['data']['relationships']['portales7_files']['data']:
                file_json = json.loads(get_url_data('https://' + domain + lang + '/jsonapi/file/file/' + file['id']))
                print('Page:     ' + paragraph_json['data'][0]['attributes']['title'])
                print('Category: ' + media_json['data']['attributes']['portales7_fc_name'])
                print('Title:    ' + file['meta']['description'])
                print('Filename: ' + file_json['data']['attributes']['filename'])
                print('Filetype: ' + file_json['data']['attributes']['filemime'])
                print('URL:      https://' + domain + file_json['data']['attributes']['uri']['url'])
                print('File ID:  ' + str(file_json['data']['attributes']['drupal_internal__fid']))
                print('Change:   ' + file_json['data']['attributes']['changed'])
                print('===========================================================================')

                #s3.meta.client.upload_file('/tmp/or1-2018.pdf', 'backend-bundle-workshop1', 'hello.txt', {
                #    'Metadata': {
                #        'page': paragraph_json['data'][0]['attributes']['title'],
                #        'category': media_json['data']['attributes']['portales7_fc_name'],
                #        'title': file['meta']['description'],
                #        'change': file_json['data']['attributes']['changed']
                #    }
                #})


def get_url_data(url):
    request = urllib.request.Request(url)

    # add user agent (server will return an empty response without it  ¯\_(ツ)_/¯)
    request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                       + '(KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36')
    request.add_header('Accept', '*/*')

    with urllib.request.urlopen(request) as url:
        # read data from url
        data = url.read().decode()

    return data


if __name__ == '__main__':
    main()
