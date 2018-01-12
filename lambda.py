from __future__ import print_function
import os
import time
import json
from urllib.parse import quote
import boto3
from bs4 import BeautifulSoup, NavigableString

s3 = boto3.client('s3')

def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = quote(event['Records'][0]['s3']['object']['key'].encode('utf8'))
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        soup = BeautifulSoup(response['Body'].read(), "html.parser")
        remove_elements(soup)
        html = soup.prettify()
        end_path = path(key)
        s3_upload_article(html, bucket, end_path)
        puts_index(bucket, key, end_path)
        return response['ContentType']
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e

def puts_index(bucket, key, end_path):
    url, text, markup = create_markup(end_path)
    index_response_www, index_bucket_www, index_key = get_object()
    soup_www = BeautifulSoup(index_response_www['Body'].read(), "html5lib")
    soup_www.ul.insert(-1, markup)
    html2 = soup_www.prettify()
    s3_upload_article(html2, index_bucket_www, index_key)

def get_object():
    index_key = 'index.html'
    index_bucket_www = 'www.nzenitram.com'
    index_response_www = s3.get_object(Bucket=index_bucket_www, Key=index_key)
    return index_response_www, index_bucket_www, index_key

def remove_elements(soup):
    soup.style.decompose()
    soup.section.decompose()
    soup.header.decompose()
    soup.footer.decompose()
    remove_style_tags(soup)
    center_figures(soup)

def remove_style_tags(soup):
    for tag in soup():
        for attribute in ["style"]:
            del tag[attribute]

def center_figures(soup):
    figures = soup.findAll('figure')
    for fig in figures:
        fig['style'] = "text-align:center"

def s3_upload_article(html, bucket, end_path):
    s3.put_object(Body=html, Bucket=bucket, Key=end_path, ContentType='text/html', ACL='public-read')

def path(key):
    s = '-'
    seq = key.split('_')[1].split('-')[:-1]
    end_path = s.join(seq) + '.html'
    return end_path

def create_markup(end_path):
    url = 'https://s3-us-west-1.amazonaws.com/nzenitram-medium-posts/' + end_path
    text = ' '.join(end_path.split('.'[:1])[0].split('-'))
    markup = BeautifulSoup("<li><a class='waves-effect blog' name={}>{}</a></li>".format(url, text), 'html5lib').body.next
    return url, text, markup
