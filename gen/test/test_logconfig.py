from utils.logconfig import CustomFormatter, setup_logging
import logging

def test_logging_with_formatter():
    logger = logging.getLogger('main')
    setup_logging(logging.DEBUG)
    custom_formatter = CustomFormatter()

    expected_log_output = '| main                   | MainThread      | INFO     | Handling \x1b[1m21.13.18\x1b[0m\x1b[0m'

    binary_msg = 'Handling \x1b[1m%s\x1b[0m'
    new_record = logging.LogRecord(name='main', level=logging.INFO, pathname="", lineno=0,
                                   msg=binary_msg,
                                   args=('21.13.18'), exc_info=None)

    custom_formatter_record = custom_formatter.format(record=new_record)
    assert expected_log_output in custom_formatter_record
    assert id(logger) == id(logging.getLogger('main'))
