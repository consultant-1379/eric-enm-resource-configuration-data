import pytest
from model.version import Version


def test_version_parse_psv():
    exp_result = Version('21.11.38', '21.11.38-3', (21, 11, 38, 3))
    assert Version.parse('21.11.38-3') == exp_result


def test_version_parse_ps(mocker):
    mocker.patch('model.version.get_latest_green_product_set_version',
                 return_value='21.11.38-3')
    exp_result = Version('21.11', '21.11.38-3', (21, 11, 38, 3))
    assert Version.parse('21.11') == exp_result


def test_version_parse_bad_drop_format(caplog):
    with pytest.raises(SystemExit):
        Version.parse('21.11.38.3')
    out = caplog.text
    assert 'Bad Drop format. (Must be X.Y or X.Y.Z or X.Y.Z-V)' in out


def test_version_compare():
    v1 = (21, 11, 38, 3)
    v2 = (21, 12, 28, 1)
    assert Version.compare(v1, v2) == -1


def test_operators():
    v1 = Version('21.11', '21.11.38-3', (21, 11, 38, 3))
    v2 = Version('21.12', '21.12.38-3', (21, 12, 38, 3))
    assert v1 < v2
    assert v2 > v1
    assert v1 <= v2
    assert v2 >= v1
    assert v2 != v1
