#!/bin/bash
SCRIPT_NAME=$(basename "$0")
OPTION_H=0
GEN_TAG="NOT_SET"
FE_TAG="NOT_SET"
DOCKER_REPO="armdocker.rnd.ericsson.se/proj-eric-enm-resource-configuration-data"
RCD_FE_CONTAINER_NAME='rcdfe'
RCD_FE_INTERNAL_CONTAINER_NAME='rcdfe_internal'
RCD_GENERATOR_CONTAINER_NAME='rcd_generator'


usage(){
    echo -e "\nUsage: $SCRIPT_NAME [-g <tag>] [-f <tag>] [-h] \\
    Parameters:
        -g   Generator image version tag.
        -f   Front End image version tag
        -h   Print the script usage help.
    "
    [[ $OPTION_H == 0 ]] && exit 1
    exit 0
}


pull_docker_images(){
    echo "Pulling RCD docker images"
    docker pull "${GEN_IMAGE}"
    docker pull "${FE_IMAGE}"
    docker pull "${FE_INTERNAL_IMAGE}"
}


remove_container()
{
    echo "Stopping container $1"
    docker stop "$1"
    echo "Removing container $1"
    docker rm "$1"
}


while getopts "g:f:h" opt; do
   case $opt in
    g) # Generator image version tag.
        GEN_TAG="$OPTARG"
        ;;
    f) # Front End image version tag.
        FE_TAG="$OPTARG"
        ;;
    h) # Print help
        OPTION_H=1
        usage
        ;;
    ?) # Invalid option
        echo
        echo "${SCRIPT_NAME}: Invalid command line option [${OPTARG}]"
        echo
        usage
        ;;
  esac
done

GEN_IMAGE="${DOCKER_REPO}/generator:${GEN_TAG}"
FE_IMAGE="${DOCKER_REPO}/server:${FE_TAG}"
FE_INTERNAL_IMAGE="${DOCKER_REPO}/server_internal:${FE_TAG}"

pull_docker_images

if [[ ${GEN_TAG} == "NOT_SET" ]]; then
    echo "No Generator image tag specified."
else
    echo "Restart running RCD Generator container with new image: ${GEN_IMAGE}"
    [[ $(docker ps | grep ${RCD_GENERATOR_CONTAINER_NAME}) ]] && remove_container "${RCD_GENERATOR_CONTAINER_NAME}"
    docker run -d --net=host --restart always -v /rcd/data:/data -v /rcd/logs:/rcd/logs -v /rcd/ssl_certs/:/ssl_certs --name "${RCD_GENERATOR_CONTAINER_NAME}" "${GEN_IMAGE}"
fi

if [[ ${FE_TAG} == "NOT_SET" ]]; then
    echo "No Front End image tag specified."
else
    echo "Restart running RCD container with new image: ${FE_IMAGE}"
    [[ $(docker ps | grep ${RCD_FE_CONTAINER_NAME}) ]] && remove_container "${RCD_FE_CONTAINER_NAME}"
    docker run --restart always -d -v /rcd/ssl_certs/:/ssl_certs -v /rcd/data:/srv/rcd-fe/data:ro -p 443:443 --name "${RCD_FE_CONTAINER_NAME}" "${FE_IMAGE}"

    echo "Restart running RCD internal container with new image: ${FE_INTERNAL_IMAGE}"
    [[ $(docker ps | grep ${RCD_FE_INTERNAL_CONTAINER_NAME}) ]] && remove_container "${RCD_FE_INTERNAL_CONTAINER_NAME}"
    docker run --restart always -d -v /rcd/ssl_certs/:/ssl_certs -v /rcd/data:/srv/rcd-fe/data:ro -p 8888:443 --name "${RCD_FE_INTERNAL_CONTAINER_NAME}" "${FE_INTERNAL_IMAGE}"
fi
