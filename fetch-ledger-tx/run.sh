#!/bin/bash
# set -x

export MSYS_NO_PATHCONV=1

# --- Set program name here ---
program_name="fetch_ledger_tx"

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

function isInstalled() {
  (
    if [ -x "$(command -v ${@})" ]; then
      return 0
    else
      return 1
    fi
  )
}

function echoYellow (){
  (
  _msg=${1}
  _yellow='\e[33m'
  _nc='\e[0m' # No Color
  echo -e "${_yellow}${_msg}${_nc}" >&2
  )
}

JQ_EXE=jq
if ! isInstalled ${JQ_EXE}; then
  echoYellow "The ${JQ_EXE} executable is required and was not found on your path."

  cat <<-EOF
  The recommended approach to installing the required package(s) is to use either [Homebrew](https://brew.sh/) (MAC)
  or [Chocolatey](https://chocolatey.org/) (Windows).  For more information visit https://stedolan.github.io/jq/

  Windows:
    - chocolatey install ${JQ_EXE}
  MAC:
    - brew install ${JQ_EXE}
EOF
  exit 1
fi

# fetch_status can have long running commands.
# Detect any existing containers running the same command and exit.
runningContainers=$(docker ps | grep ${program_name} | awk '{print $1}')
if [ ! -z "${runningContainers}" ]; then
  for runningContainer in ${runningContainers}; do
    runningContainerCmd=$(docker inspect ${runningContainer} | ${JQ_EXE} -r '.[0]["Config"]["Cmd"][0]')
    if [[ "${runningContainerCmd}" == "${@}" ]]; then 
      echoYellow "There is an instance of $program_name already running the same command.  Please wait for it to complete ..."
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

docker build -t $program_name . > /dev/null 2>&1

cmd="${terminalEmu} docker run --rm ${DOCKER_INTERACTIVE} \
  -e "GENESIS_PATH=${GENESIS_PATH}" \
  -e "GENESIS_URL=${GENESIS_URL}" \
  -e "SEED=${SEED}" "


# Dynamically mount directories if they exists.
if [ -d "./conf" ]; then
  cmd+=$(getVolumeMount "./conf")
fi

if [ -d "./ledger_data" ]; then
  cmd+=$(getVolumeMount "./ledger_data")
fi

if [ -d "./plugins" ]; then
  cmd+=$(getVolumeMount "./plugins")
fi

if [ -d "./logs/" ]; then
  cmd+=$(getVolumeMount "./logs/")
fi

cmd+="$program_name \"$@\""
eval ${cmd}