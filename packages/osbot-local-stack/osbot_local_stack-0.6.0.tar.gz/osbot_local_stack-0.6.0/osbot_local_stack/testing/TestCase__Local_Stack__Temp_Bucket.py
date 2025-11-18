from osbot_local_stack.local_stack.Local_Stack__Internal import DEFAULT__LOCAL_STACK__TARGET_SERVER
from osbot_utils.utils.Misc                              import random_text
from osbot_utils.decorators.methods.cache_on_self        import cache_on_self
from osbot_aws.aws.s3.S3                                 import S3
from osbot_local_stack.testing.TestCase__Local_Stack     import TestCase__Local_Stack


class TestCase__Local_Stack__Temp_Bucket(TestCase__Local_Stack):
    delete_after_run : bool = True
    s3_bucket        : str  = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        assert cls.local_stack.is_local_stack_configured_and_available() is True
        cls.s3        = S3()
        if cls.s3_bucket and cls.s3.bucket_exists(bucket_name=cls.s3_bucket):
            print()
            print(f"*** Using existing bucket: {cls.s3_bucket} ***")
            print(f"*** region name: {cls.aws_region}")
        else:
            cls.s3_bucket   = cls.temp_bucket_name()
            assert cls.s3.bucket_create(bucket=cls.s3_bucket, region=cls.aws_region).get('status') == 'ok'
        assert cls.s3.bucket_exists(bucket_name=cls.s3_bucket) is True

    @classmethod
    def tearDownClass(cls):
        assert cls.local_stack.is_local_stack_configured_and_available() is True                                    # really make sure we are still running against a "local stack"
        if cls.delete_after_run:
            assert cls.s3.client().meta.endpoint_url                         == DEFAULT__LOCAL_STACK__TARGET_SERVER
            cls.s3.bucket_delete_all_files(bucket=cls.s3_bucket)
            cls.s3.bucket_delete          (bucket=cls.s3_bucket)
            assert cls.s3.bucket_exists   (bucket_name=cls.s3_bucket) is False
        else:
            print(f"*** Skipping delete bucket ***")
            print(f"*** bucket name: {cls.s3_bucket}")
            print(f"*** region name: {cls.aws_region}")
            print()
        super().tearDownClass()
        #cls.local_stack.delete_bucket(cls.temp_bucket)

    @classmethod
    def temp_bucket_name(cls):
        return random_text('local-stack', lowercase=True).replace('_', '-')

    @cache_on_self
    def s3(self):
        return S3()

