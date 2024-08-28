# RCD Back End Unit Tests

The tests are written using pytest framework

## Build unit test runner Docker base image
> This image is just used a simple runtime for the unit tests to run in the Jenkins pipeline.
> This image does not install the pip packages required for the tests. These are installed by the run_unit_tests.sh entrypoint script for the container. They are not preinstalled in the image as the requirements may change so process is simpler if these are installed at run time.
1. Build docker image locally
    ```bash
    docker build -t <registry>/unit_test_runner:<version> -f gen/test/container/Dockerfile .
    ```
2. Push image to registry
    ```bash
    docker push <registry>/unit_test_runner:<version>
    ```
3. Update unit_test_image_tag in the `<reporoot>/JenkinsfilePreCommit`
## Run tests locally on development machine
### Run tests in Docker container

```bash
docker run --rm -v <reporoot>/:/workspace/ <registry>/unit_test_runner:<version> --cov=/workspace/gen/ --cov-report=term-missing --cov-fail-under=95
```

### Run tests locally without using Docker

1. Install `<reporoot>/gen/requirements.txt` and `<reporoot>/gen/test/requirements.txt`
   ```bash
   pip3 install -r <reporoot>/gen/requirements.txt -r <reporoot>/gen/test/requirements.txt
   ```
2. Run the tests:
    ```bash
    cd <reporoot>/
    pytest --cov-report=term-missing --cov=gen/ --cov-report=term-missing --cov-fail-under=95
    ```
