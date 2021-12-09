#!/usr/bin/python3

import urllib.request
import json
import os
from dotenv import load_dotenv
import boto3
import botocore.exceptions
from unidecode import unidecode

load_dotenv()


def main():
    domain = os.getenv('TARGET_DOMAIN')
    nodeid = os.getenv('TARGET_ID')
    lang = os.getenv('TARGET_LANG')
    bucket = os.getenv('AWS_BUCKET_NAME')
    tmpdir = os.getenv('TMP_DIR')

    # the authentication data is read from the environment variables AWS_ACCESS_KEY_ID & AWS_SECRET_ACCESS_KEY
    s3 = boto3.client('s3')

    # get the paragraphs via drupals json api
    paragraph_json = json.loads(get_url_data('https://' + domain + lang
                                             + '/jsonapi/node/articulo?filter[drupal_internal__nid]=' + nodeid))
    for paragraph in paragraph_json['data'][0]['relationships']['field_adjuntos']['data']:
        if paragraph['type'] == 'paragraph--es7_media':
            media_json = json.loads(get_url_data('https://' + domain + lang + '/jsonapi/paragraph/es7_media/'
                                                 + paragraph['id']))
            for file in media_json['data']['relationships']['portales7_files']['data']:
                file_json = json.loads(get_url_data('https://' + domain + lang + '/jsonapi/file/file/' + file['id']))

                # collect the needed attributes
                page = paragraph_json['data'][0]['attributes']['title']
                category = media_json['data']['attributes']['portales7_fc_name']
                title = file['meta']['description']
                filename = file_json['data']['attributes']['filename']
                url = 'https://' + domain + file_json['data']['attributes']['uri']['url']
                file_id = str(file_json['data']['attributes']['drupal_internal__fid'])
                last_change = file_json['data']['attributes']['changed']

                print('File: ' + title)

                # while the file name will be human readable, it may not be unique, so we create a unique filename by
                # adding the unique id we get from the drupal page
                unique_filename = file_id + '_' + filename

                do_upload = True

                # let's check if the file alredy exists
                try:
                    # this will throw a 404 if the file does not exist:
                    head = s3.head_object(Bucket=bucket, Key=unique_filename)

                    print('  file exists already...')

                    # the file exists - we should only replace it if it was changed in drupal
                    do_upload = head['Metadata']['last_change'] != last_change

                    if do_upload:
                        print('  ...file changed since last upload!')
                    else:
                        print('  ...file did not change since last upload - skip it!')

                except botocore.exceptions.ClientError as err:
                    # if we got an 404, the file does not exist - we will ignore this error and upload it
                    if err.response['Error']['Code'] != '404':
                        # another error occured - let's re-raise it
                        raise err
                    else:
                        print('  file does not exist yet!')

                if do_upload:
                    # we can't upload the file directly from the url, so we have to donwload it first
                    filecontent = get_url_data('https://' + domain + file_json['data']['attributes']['uri']['url'],
                                               decode=False)
                    f = open(tmpdir + file_id, 'wb')
                    f.write(filecontent)
                    f.close()

                    # now lets upload it!
                    # we'll have to use unidecode for the metadata, as s3 will only accept ascii characters
                    s3.upload_file(tmpdir + file_id, bucket, unique_filename, {'Metadata': {
                        'page': unidecode(page),
                        'category': unidecode(category),
                        'title': unidecode(title),
                        'filename': unidecode(filename),
                        'file_id': unidecode(file_id),
                        'original_url': unidecode(url),
                        'last_change': unidecode(last_change)
                    }})

                    # now delete the temporary file
                    os.remove(tmpdir + file_id)


def get_url_data(url, decode=True):
    request = urllib.request.Request(url)

    # add user agent (server will return an empty response without it  ¯\_(ツ)_/¯)
    request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                       + '(KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36')
    request.add_header('Accept', '*/*')

    with urllib.request.urlopen(request) as url:
        # read data from url
        if decode:
            data = url.read().decode()
        else:
            data = url.read()

    return data


if __name__ == '__main__':
    main()
