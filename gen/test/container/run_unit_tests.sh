#!/bin/bash
echo 'Install python packages'
pip3 install -r /workspace/gen/requirements.txt -r /workspace/gen/test/requirements.txt
mkdir -p /rcd/gen/
cp -r /workspace/gen/ /rcd/
echo "Start test http server"
cd /rcd/gen/test/resources/
python3 -m http.server 5005 --bind localhost  &> /dev/null &
server=$!
sleep 5

echo "Create log file"
mkdir -p /rcd/logs/
touch /rcd/logs/generator.log

echo "Check pytest coverage"
cd /rcd/
export PYTHONPATH=.
pytest_args=$@
export RCD_DATA_PATH='/workspace/test/data/' RCD_SSL_ADHOC=true

echo "Pytest args --> ${pytest_args}"
pytest --cov=gen/ "${pytest_args}"
pytest_rc=$?
echo "Stop test http server"
kill ${server}

exit ${pytest_rc}