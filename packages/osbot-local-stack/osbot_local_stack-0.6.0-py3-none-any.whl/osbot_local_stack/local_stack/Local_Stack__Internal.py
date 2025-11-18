from osbot_utils.type_safe.Type_Safe import Type_Safe

ENV_NAME__LOCAL_STACK__TARGET_SERVER = 'LOCAL_STACK__TARGET_SERVER'
DEFAULT__LOCAL_STACK__TARGET_SERVER  = 'http://localhost:4566'

# see full list at https://docs.localstack.cloud/references/internal-endpoints/

class Local_Stack__Internal(Type_Safe):
    endpoint_url: str = None

    def __init__(self, **kwargs):
        from osbot_utils.utils.Env import get_env

        super().__init__(**kwargs)
        self.endpoint_url = get_env(ENV_NAME__LOCAL_STACK__TARGET_SERVER, DEFAULT__LOCAL_STACK__TARGET_SERVER)

    def get__aws_lambda_runtimes(self):
        return self.requests__aws__get('lambda/runtimes')

    def get__internal_diagnose(self):
        return self.requests__internal__get('diagnose')

    def get__internal_health(self):
        return self.requests__internal__get('health')

    def get__internal_init(self):
        return self.requests__internal__get('init')

    def get__internal_plugins(self):
        return self.requests__internal__get('plugins')

    def requests__aws__get(self, action):
        path = f'/_aws/{action}'
        return self.requests__get(path)

    def requests__internal__get(self, action):
        path = f'/_localstack/{action}'
        return self.requests__get(path)

    def requests__get(self, path):
        import requests
        from requests                      import RequestException
        from osbot_utils.testing.__helpers import dict_to_obj
        from osbot_utils.utils.Http        import url_join_safe

        try:
            url       = url_join_safe(self.endpoint_url, path)
            json_data = requests.get(url).json()
            obj_data  = dict_to_obj(json_data)
            return obj_data
        except RequestException:
            return {}
