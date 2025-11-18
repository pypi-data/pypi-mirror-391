from unittest                                        import TestCase
from osbot_aws.AWS_Config                            import aws_config
from osbot_aws.testing.Temp__Random__AWS_Credentials import Temp_AWS_Credentials
from osbot_local_stack.local_stack.Local_Stack       import Local_Stack


class TestCase__Local_Stack(TestCase):
    aws_region = None

    @classmethod
    def setUpClass(cls):
        cls.local_stack = Local_Stack()
        cls.temp_asw_credentials = Temp_AWS_Credentials().with_localstack_credentials()
        cls.temp_asw_credentials.set_vars()
        if cls.aws_region is None:
            cls.aws_region = aws_config.region_name()
        else:
            aws_config.set_region(cls.aws_region)
        cls.local_stack.activate()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.local_stack.deactivate()
        cls.temp_asw_credentials.restore_vars()
