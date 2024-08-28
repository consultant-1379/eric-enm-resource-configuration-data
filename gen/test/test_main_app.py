import json
import main_app
from main_app import post_new_product_set, validate_request_json, post_new_release_product_set
from mock import patch
from flask import (
    request, Response
)

URL = '/addproductset'
RELEASE_URL='/addreleaseproductset'
AUTHORIZATION_HEADER='Basic eC1hdXRoLXRva2Vu=='
EIC = 'EIC'
MOCK_REQUEST_HEADER = {
    'Authorization': AUTHORIZATION_HEADER,
    'Content-Type': 'application/json'
}


def test_invalid_route():
    with main_app.app.test_client() as client:
        response = client.get(URL)
        assert response.status_code == 405

def test_bad_request_error_non_release_endpoint():
    mock_request_headers = {
        'Authorization': AUTHORIZATION_HEADER
    }
    with main_app.app.test_client() as client:
        response = client.post(URL, headers=mock_request_headers)
        assert response.status_code == 500


def test_bad_request_error_release_endpoint():
    mock_request_headers = {
        'Authorization': AUTHORIZATION_HEADER
    }
    with main_app.app.test_client() as client:
        response = client.post(RELEASE_URL, headers=mock_request_headers)
        assert response.status_code == 500


@patch('main_app.provision_rcd')
def test_post_success(m_get_provision_rcd):
    mock_request_data = {
        'is_release': False,
        'productset': '21.10'
    }
    m_get_provision_rcd.return_value = 0
    post_new_product_set()
    with main_app.app.test_client() as client:
        response = client.post(URL, data=json.dumps(
            mock_request_data), headers=MOCK_REQUEST_HEADER)
        assert response.status_code == 200


@patch('main_app.provision_eic_rcd')
def test_eic_post_success(m_provision_eic_rcd):
    mock_request_data = {
        'is_release': False,
        'productset': '2.23.0-120',
        'product': EIC
    }
    m_provision_eic_rcd.return_value = 0
    post_new_product_set()
    with main_app.app.test_client() as client:
        response = client.post(URL, data=json.dumps(
            mock_request_data), headers=MOCK_REQUEST_HEADER)
        assert response.status_code == 200


@patch('main_app.ProvisionRcdThread')
def test_post_internal_error(m_get_provision_rcd):
    mock_request_data = {
        'is_release': False,
        'productset': '21.10'
    }
    m_get_provision_rcd.side_effect = Exception()
    post_new_product_set()
    with main_app.app.test_client() as client:
        response = client.post(URL, data=json.dumps(
            mock_request_data), headers=MOCK_REQUEST_HEADER)
        assert response.status_code == 500


@patch('main_app.provision_rcd')
def test_release_post_success(m_get_provision_rcd):
    mock_request_data = {
        'is_release': True,
        'productset': '21.10'
    }
    m_get_provision_rcd.return_value = 0
    post_new_product_set()
    with main_app.app.test_client() as client:
        response = client.post(RELEASE_URL, data=json.dumps(
            mock_request_data), headers=MOCK_REQUEST_HEADER)
        assert response.status_code == 200


@patch('main_app.provision_eic_rcd')
def test_release_eic_post_success(m_provision_eic_rcd):
    mock_request_data = {
        'is_release': True,
        'productset': '2.23.0-121',
        'product': EIC
    }
    m_provision_eic_rcd.return_value = 0
    post_new_product_set()
    with main_app.app.test_client() as client:
        response = client.post(URL, data=json.dumps(
            mock_request_data), headers=MOCK_REQUEST_HEADER)
        assert response.status_code == 200


def test_valid_request():
    _, status_code = validate_request_json({'productset':'22.03.95'}, AUTHORIZATION_HEADER)
    assert status_code == 200


def test_eic_valid_request():
    _, status_code = validate_request_json({'productset':'2.23.0-121', 'product': EIC}, AUTHORIZATION_HEADER)
    assert status_code == 200


def test_un_authorized_request():
    _, status_code = validate_request_json({'productset':'22.03.95'}, '')
    assert status_code == 401


def test_bad_request_empty_request():
    _, status_code = validate_request_json({},'')
    assert status_code == 400


def test_bad_request_no_product_set():
    _, status_code = validate_request_json({'':''}, AUTHORIZATION_HEADER)
    assert status_code == 400


def test_bad_request_is_release_str():
    _, status_code = validate_request_json(None, AUTHORIZATION_HEADER)
    assert status_code == 400
