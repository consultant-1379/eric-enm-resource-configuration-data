'''
This file is the starting point for RCD and hosts a flask rest endpoint.
This endpoint receives the release and non-release product set versions.
'''
import argparse
import json
import logging
import os
import threading
import traceback

from _version import __version__
from api.resource_calculation import (get_resource_overview,
                                      prepare_data,
                                      prepare_excel_data,
                                      prepare_agg_data,
                                      prepare_data_comparison)
from cleanup import cleanup_intermediate_pdu_product_sets
from flask import Flask, Response, request, send_file, make_response
from generator import provision_rcd, provision_eic_rcd
from output.output_json import MyEncoder
from utils import cache
from utils.logconfig import setup_logging
from io import BytesIO

log = logging.getLogger('app')
app = Flask(__name__)
API = '/api/'
BAD_REQUEST_PRODUCT_SET = 'Bad request : No product set version'
BAD_REQUEST_IS_RELEASE = 'Bad Request: is_release param should be true/false/integer'
RELEASE_COMPARIISON_ENDPOINT = 'getReleaseDataComparison'
RELEASE_DATA_ENDPOINT = 'getReleaseData'
RELEASE_OVERVIEW_ENDPOINT = 'getReleaseOverview'
EXCEL_DATA_ENDPOINT = 'getExcelData'
EIC = 'EIC'
C_ENM = 'cENM'
PRODUCT='product'

def parse_args():
    '''
    This function parses the arguments for the RCD.
    '''
    parser = argparse.ArgumentParser(
        description='Generates the "Cloud Native ENM Resource Configuration Data (RCD)" from'
                         'the released (or release candidate) helm charts.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('-n', '--no-cache', action='store_true',
                        help='Do not use cached values')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Set log-level to DEBUG')
    parser.add_argument('-V', '--version', action='version',
                        version='%(prog)s v' + __version__)
    args = parser.parse_args()

    cache.IGNORE_CACHE = args.no_cache
    setup_logging(logging.DEBUG if args.debug else logging.INFO)
    return args


class ProvisionRcdThread(threading.Thread):
    '''
    This class is used to provision a product set in RCD as separate thread.
    This helps us to achieve provisioning multiple cENM product sets simultaneously in RCD.
    '''
    def __init__(self, product_name, product_set_version, is_release) -> None:
        super().__init__(name=product_set_version)
        self.product_name = product_name
        self.product_set_version = product_set_version
        self.is_release = is_release

    def run(self):
        '''
        This method has implementation of run method in thread.
        A Separate thread will be created to provision product set in RCD.
        '''
        try:
            if self.product_name is None or self.product_name == C_ENM:
                provision_rcd(self.product_set_version, self.is_release)
            else:
                provision_eic_rcd(self.product_set_version, self.is_release)
        except Exception:
            log.error(traceback.print_exc())
            traceback.print_exc()


def validate_request_json(request_json, authorization_header):
    '''
    This method validates the API requests.
    '''
    if not request_json:
        return 'Bad request' , 400

    if authorization_header != 'Basic eC1hdXRoLXRva2Vu==':
        log.info('Authorization failed. authorization header received: %s' , authorization_header)
        return 'Unauthorized' , 401

    if not request_json.get('productset', None):
        log.info(BAD_REQUEST_PRODUCT_SET)
        return BAD_REQUEST_PRODUCT_SET, 400
    return None, 200


@app.route("/addreleaseproductset", methods=['POST'])
def post_new_release_product_set():
    '''
    This is POST API endpoint for release candidates.
    '''
    try:
        request_json_object = request.json
        authorization_header = request.headers.get("Authorization", None)
        status_message, status_code = validate_request_json(request_json_object,
                                                             authorization_header)
        if status_code != 200:
            return Response(status_message, status=status_code)

        product_name = request_json_object.get(PRODUCT, C_ENM)
        product_set_version = request_json_object.get('productset', None)
        log.info('Received Release candidate product name:  %s product set: %s ',
                  product_name, product_set_version)

        if product_name == C_ENM:
            provision_rcd(product_set_version, True)
            cleanup_intermediate_pdu_product_sets(product_set_version)
        else:
            provision_eic_rcd(product_set_version, True)

        return Response("Success", status=200)
    except Exception:
        log.error(traceback.print_exc())
        traceback.print_exc()
        return Response("Internal Server Error", status=500)


@app.route("/addproductset", methods=['POST'])
def post_new_product_set():
    '''
    This is POST API endpoint for non-release candidates.
    '''
    try:
        request_json_object = request.json
        authorization_header = request.headers.get("Authorization", None)
        status_message, status_code = validate_request_json(request_json_object,
                                                                     authorization_header)
        if status_code != 200:
            return Response(status_message, status=status_code)

        product_name = request_json_object.get(PRODUCT, C_ENM)
        product_set_version = request_json_object.get('productset', None)
        log.info('Received product name: %s product set: %s is not a release candidate',
                 product_name, product_set_version)
        rcd_thread = ProvisionRcdThread(product_name, product_set_version, False)
        rcd_thread.start()
        return Response("Success", status=200)
    except Exception:
        log.error(traceback.print_exc())
        traceback.print_exc()
        return Response("Internal Server Error", status=500)


@app.route(API + EXCEL_DATA_ENDPOINT, methods=['GET'])
def get_excel_data():
    '''
    This is a GET API endpoint to get data for generating excel.
    '''
    try:
        response = make_response(process_request(request.args, EXCEL_DATA_ENDPOINT))
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response
    except Exception:
        log.error(traceback.print_exc())
        traceback.print_exc()
        return Response("Internal Server Error", status=500)


@app.route(API + RELEASE_DATA_ENDPOINT, methods=['GET'])
def get_release_requiremets():
    '''
    This is a GET API endpoint to get all details of a release.
    '''
    try:
        response = Response(process_request(request.args, RELEASE_DATA_ENDPOINT))
        response.status=200
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Content-Type"] = "application/json"
        return response
    except Exception:
        log.error(traceback.print_exc())
        traceback.print_exc()
        return Response("Internal Server Error", status=500)


@app.route(API + RELEASE_OVERVIEW_ENDPOINT, methods=['GET'])
def get_release_overview():
    '''
    This is a GET API endpoint to get overview details of a release.
    '''
    try:
        response = Response(process_request(request.args, RELEASE_OVERVIEW_ENDPOINT))
        response.status=200
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Content-Type"] = "application/json"
        return response
    except Exception:
        log.error(traceback.print_exc())
        traceback.print_exc()
        return Response("Internal Server Error", status=500)


@app.route(API + RELEASE_COMPARIISON_ENDPOINT, methods=['GET'])
def compare_releases():
    '''
    This is a GET API endpoint to compare 2 application versions.
    '''
    try:
        response = Response(process_request(request.args, RELEASE_COMPARIISON_ENDPOINT))
        response.status = 200
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Content-Type"] = "application/json"
        return response
    except Exception:
        log.error(traceback.print_exc())
        traceback.print_exc()
        return Response("Internal Server Error", status=500)


def process_request(req_args, request_type):
    '''
    Process request arguements and call the relevant function based on request_type.
    Return a json object of the response data.
    '''
    variant = req_args.get('deployment_size', type=str).lower()
    ip_version = req_args.get('ip_version', type=str, default='').lower()
    product_name = req_args.get(PRODUCT, None)

    if request_type == RELEASE_COMPARIISON_ENDPOINT:
        from_version = req_args.get('from_release_version', type=str)
        to_version = req_args.get('to_release_version', type=str)
        from_optional_apps = req_args.get('from_optional_apps', type=str, default='').split(',')
        to_optional_apps = req_args.get('to_optional_apps', type=str, default='').split(',')
        return json.dumps(prepare_data_comparison(variant, from_version, to_version,
                                                  ip_version, from_optional_apps,
                                                  to_optional_apps), cls=MyEncoder)
    version = req_args.get('release_version', type=str)
    optional_apps = req_args.get('optional_apps', type=str, default='').split(',')
    if request_type == RELEASE_OVERVIEW_ENDPOINT:
        return json.dumps(get_resource_overview(variant, version, ip_version, optional_apps),
                          cls=MyEncoder)
    if request_type == EXCEL_DATA_ENDPOINT:
        if product_name is None or product_name != EIC:
            file = BytesIO()
            workbook = prepare_excel_data(variant, version, ip_version, optional_apps)
            workbook.save(file)
            file.seek(0)
            return send_file(file, download_name="file.xlsx", mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True)
    if request_type == RELEASE_DATA_ENDPOINT:
        if product_name is None or product_name != EIC:
            return json.dumps(prepare_data(variant, version, ip_version, optional_apps),
                            cls=MyEncoder)

        return json.dumps(prepare_agg_data(variant, version, ip_version, optional_apps),
                          cls=MyEncoder)


def main():
    '''
    This function initializes the port on which this flask service will be hosted.
    '''
    ssl_cert_path = '/ssl_certs/cabundle.crt'
    ssl_key_path = '/ssl_certs/resourceconfigurationdata_internal_ericsson_com.key'
    parse_args()
    port = int(os.environ.get('PORT', 5000))
    if 'RCD_USE_HTTP' in os.environ:
        app.run(host='0.0.0.0', port=port)
    elif 'RCD_SSL_ADHOC' in os.environ:
        app.run(host='0.0.0.0', port=port, ssl_context='adhoc')
    else:
        app.run(host='0.0.0.0', port=port, ssl_context=(ssl_cert_path, ssl_key_path))


if __name__ == '__main__':
    main()
