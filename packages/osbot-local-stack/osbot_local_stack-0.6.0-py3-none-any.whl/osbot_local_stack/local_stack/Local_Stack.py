from osbot_utils.type_safe.Type_Safe                     import Type_Safe
from osbot_local_stack.local_stack.Local_Stack__Internal import Local_Stack__Internal, DEFAULT__LOCAL_STACK__TARGET_SERVER


class Local_Stack(Type_Safe):
    endpoint_url__saved  : str                   = None
    local_stack__internal: Local_Stack__Internal

    def __enter__(self):
        self.activate()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.deactivate()
        return self


    def activate(self):
        from osbot_aws.AWS_Config  import ENV_NAME__AWS_ENDPOINT_URL
        from osbot_utils.utils.Env import get_env, set_env

        endpoint_url             = self.local_stack__internal.endpoint_url
        self.endpoint_url__saved = get_env(ENV_NAME__AWS_ENDPOINT_URL)
        set_env(ENV_NAME__AWS_ENDPOINT_URL, endpoint_url)
        return self

    def deactivate(self):
        from osbot_aws.AWS_Config  import ENV_NAME__AWS_ENDPOINT_URL
        from osbot_utils.utils.Env import set_env, del_env

        if self.endpoint_url__saved is None:
            del_env(ENV_NAME__AWS_ENDPOINT_URL)
        else:
            set_env(ENV_NAME__AWS_ENDPOINT_URL, self.endpoint_url__saved)
        return self

    def check__local_stack__health(self):
        return self.local_stack__internal.get__internal_health() != {}

    def check__local_stack__boto3_setup(self):
        from osbot_aws.aws.s3.S3 import S3

        return S3().client().meta.endpoint_url == DEFAULT__LOCAL_STACK__TARGET_SERVER                   # use S3 since this is the one that is currently working correctly

    def is_local_stack_configured_and_available(self):
        return self.check__local_stack__health() and self.check__local_stack__boto3_setup()

    def local_stack__health(self):
        return self.local_stack__internal.get__internal_health()


