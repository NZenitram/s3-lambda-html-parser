from __future__ import print_function
import os
import time
import json
from urllib.parse import quote
import boto3
from bs4 import BeautifulSoup

print('Loading function')

s3 = boto3.client('s3')


def lambda_handler(event, context):
    # print("Received event: " + json.dumps(event, indent=2))
    bucket = event['Records'][0]['s3']['bucket']['name']
    # print(bucket)
    key = quote(event['Records'][0]['s3']['object']['key'].encode('utf8'))
    # print(key)
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        # print(response)
        # print("CONTENT TYPE: " + response['ContentType'])
        soup = BeautifulSoup(response['Body'].read(), "html.parser")
        soup.style.decompose()
        soup.section.decompose()
        soup.header.decompose()
        for tag in soup():
            for attribute in ["style"]:
                del tag[attribute]
        html = soup.prettify()
        s = '-'
        seq = key.split('_')[1].split('-')[:-1]
        end_path = s.join(seq) + '.html'
        s3.put_object(Body=html, Bucket=bucket, Key=end_path, ContentType='text/html')
        # print(html)
        # print(end_path)
        return response['ContentType']
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e
