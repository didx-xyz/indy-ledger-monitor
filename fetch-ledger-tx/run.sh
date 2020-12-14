##!/bin/bash
## set -x
#
#export MSYS_NO_PATHCONV=1
#
## Running on Windows?
#if [[ "$OSTYPE" == "msys" ]]; then
#  # Prefix interactive terminal commands ...
#  terminalEmu="winpty"
#fi
#
## IM is for "interactive mode" so Docker is run with the "-it" parameter. Probably never needed
## but it is there. Use "IM=1 run.sh <args>..." to run the Docker container in interactive mode
#if [ -z "${IM+x}" ]; then
#  export DOCKER_INTERACTIVE=""
#else
#  export DOCKER_INTERACTIVE="-it"
#fi
#
#docker build -t fetch_ledger_tx . > /dev/null 2>&1
#
#cmd="${terminalEmu} docker run --rm ${DOCKER_INTERACTIVE} \
#  -e "GENESIS_PATH=${GENESIS_PATH}" \
#  -e "GENESIS_URL=${GENESIS_URL}" \
#  -e "SEED=${SEED}" "
#
## Dynamically mount teh 'conf' directory if it exists.
#if [ -d "./ledger_data" ]; then
#  cmd+=$(getVolumeMount "./ledger_data")
#fi
#
#cmd+="fetch_ledger_tx \"$@\""
#eval ${cmd}
##echo ${cmd}
#
##${terminalEmu} docker run --rm ${DOCKER_INTERACTIVE} \
##    -e "GENESIS_PATH=${GENESIS_PATH}" \
##    -e "GENESIS_URL=${GENESIS_URL}" \
##    -e "SEED=${SEED}" \
##    fetch_ledger_tx "$@"
#
#
#

#!/bin/bash
# set -x

export MSYS_NO_PATHCONV=1

function getVolumeMount() {
  path=${1}
  path=$(realpath ${path})
  path=${path%%+(/)}
  mountPoint=${path##*/}
  if [[ "$OSTYPE" == "msys" ]]; then
    # When running on Windows, you need to prefix the path with an extra '/'
    path="/${path}"
  fi
  echo "  --volume='${path}:/home/indy/${mountPoint}:Z' "
}

# fetch_status can have long running commands.
# Detect any existing containers running the same command and exit.
runningContainers=$(docker ps | grep fetch_status | awk '{print $1}')
if [ ! -z "${runningContainers}" ]; then
  for runningContainer in ${runningContainers}; do
    runningContainerCmd=$(docker inspect ${runningContainer} | jq -r '.[0]["Config"]["Cmd"][0]')
    if [[ "${runningContainerCmd}" == "${@}" ]]; then 
      echo "There is an instance of fetch_status already running the same command.  Please wait for it to complete ..."
      exit 0
    fi
  done
fi

# Running on Windows?
if [[ "$OSTYPE" == "msys" ]]; then
  # Prefix interactive terminal commands ...
  terminalEmu="winpty"
fi

# IM is for "interactive mode" so Docker is run with the "-it" parameter. Probably never needed
# but it is there. Use "IM=1 run.sh <args>..." to run the Docker container in interactive mode
if [ -z "${IM+x}" ]; then
  export DOCKER_INTERACTIVE=""
else
  export DOCKER_INTERACTIVE="-it"
fi

docker build -t fetch_ledger_tx . > /dev/null 2>&1

cmd="${terminalEmu} docker run --rm ${DOCKER_INTERACTIVE} \
  -e "GENESIS_PATH=${GENESIS_PATH}" \
  -e "GENESIS_URL=${GENESIS_URL}" \


# Dynamically mount the 'conf' directory if it exists.
if [ -d "./conf" ]; then
  cmd+=$(getVolumeMount "./conf")
fi

# Dynamically mount the 'ledger_data' directory if it exists.
if [ -d "./ledger_data" ]; then
  cmd+=$(getVolumeMount "./ledger_data")
fi

cmd+="fetch_ledger_tx \"$@\""
eval ${cmd}
#echo ${cmd}
