#!/bin/bash
echo 'Copying data'
mkdir -p /web/ /gen/ /rcd/logs/ /web/res/data/
cp -r /webmount/* /web/
cp -r /genmount/* /gen/
cp -r /testdatamount/* /web/res/data/
touch /rcd/logs/generator.log

# Start main_app.py to start API endpoints
echo 'Starting main_app.py to start API endpoints'
python3 -m pip install --upgrade pip
pip3 install -r /gen/requirements.txt -r /gen/test/requirements.txt
export RCD_DATA_PATH='/web/res/data/' RCD_SSL_ADHOC=true
echo VITE_APP_RCD_URL='https://localhost:5000/api/' >> .env
python3 /gen/main_app.py -n &

cd /web/

## Tests for external RCD
echo 'Running build external RCD'
npm run build

echo 'Starting npm tests-srv'
npm run tests-srv &
server=$!
sleep 5
echo 'Started npm tests-srv'

echo 'Running test cases'
npm run tests-run-external
npm_test_ext_rc=$?
echo 'Stopping test srv'
kill ${server}


## Tests for internal RCD
echo 'Running build internal RCD'
echo  VITE_APP_ENV_TYPE=pdu >> .env
echo VITE_APP_RCD_URL='https://localhost:5000/api/' >> .env
npm run build

echo 'Starting npm tests-srv'
npm run tests-srv &
server=$!
sleep 5
echo 'Started npm tests-srv'

echo 'Running test cases'
npm run tests-run-internal
npm_test_int_rc=$?
echo 'Stopping test srv'
rm -f .env
kill ${server}

if [[ "${npm_test_ext_rc}" != 0 || "${npm_test_int_rc}" != 0 ]]; then
    exit 1
fi