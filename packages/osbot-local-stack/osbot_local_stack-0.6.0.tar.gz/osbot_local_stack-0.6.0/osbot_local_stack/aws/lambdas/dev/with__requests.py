import requests

def run(event, context):
    url = event.get('url', 'https://www.google.com')
    return requests.get(url).text