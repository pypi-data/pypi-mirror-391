def run(event, context):
    print(f"in Hello World lambda: {event}")
    name = event.get('name', 'World')
    return f'Hello "{name}"'