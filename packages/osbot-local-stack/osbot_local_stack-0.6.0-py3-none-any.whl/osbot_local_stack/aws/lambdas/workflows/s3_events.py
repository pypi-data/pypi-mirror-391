import requests

def run(event, context):
    local_ip = '192.168.1.154' # '192.168.0.165
    url = f'http://{local_ip}:5005/dev/flow-testing-tasks'
    data = {'event': event }
    result = requests.post(url, json=data)
    return f'{result.text}'
