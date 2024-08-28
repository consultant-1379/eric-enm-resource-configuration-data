#!/bin/bash

# for links to work correctly execute script from eric-enm-resource-configuration-data/web directory

trap 'rm res/data' SIGINT
# Update output_folder to data in gen/config/variant_config.yaml

mkdir ../data/eric-enm-integration-production-values ../data/eric-enm-integration-extra-large-production-values ../data/eric-enm-multi-instance-functional-integration-values ../data/eric-enm-single-instance-production-integration-values
ln -sf ../data/*/ res/data
export VITE_APP_RCD_URL='http://localhost:5000/api/'
export VITE_APP_ENV_TYPE='pdu'
npm run dev &

# Start main_app.py
cd ../
export RCD_LOG_FILE='rcd/logs/generator.log' RCD_DATA_PATH='./web/res/data/' RCD_USE_HTTP=true
mkdir -p /rcd/logs/
touch /rcd/logs/generator.log
python3.8 gen/main_app.py &

#Curl command to build a JSON file locally
#request_data="{\"product\":\"cENM\", \"productset\":\"23.15.65\"}"
#response=$(curl -H "Authorization: Basic eC1hdXRoLXRva2Vu==" -k -H "Content-Type: application/json" -X POST -d "${request_data}" http://localhost:5000/addproductset)
