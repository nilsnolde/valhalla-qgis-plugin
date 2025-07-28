#!/bin/bash

# Usage: ./qgis_test_setup.sh 3.44.1 /opt

set -euo pipefail

# Check if version argument is provided
if [ -z "$1" ] || [ -z "$2" ]; then
  echo "Usage: $0 <QGIS docker version, e.g., 3.44.1> <plugin name, e.g. valhalla>"
  exit 1
fi

# Convert docker version to branch name
DOCKER_VERSION="$1"
BRANCH=""
if [[ "$DOCKER_VERSION" == "latest" ]]; then
  BRANCH=master
elif [[ "$DOCKER_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  BRANCH="final-${DOCKER_VERSION//./_}"
fi

PLUGIN_NAME="$2"

SETUP_SCRIPT_URL="https://raw.githubusercontent.com/qgis/QGIS/${BRANCH}/.docker/qgis_resources/test_runner/qgis_setup.sh"
SETUP_SCRIPT_PATH="/usr/bin/$(basename ${SETUP_SCRIPT_URL})"
STARTUP_SCRIPT_URL="https://raw.githubusercontent.com/qgis/QGIS/${BRANCH}/.docker/qgis_resources/test_runner/qgis_startup.py"
STARTUP_SCRIPT_PATH="/usr/bin/$(basename ${STARTUP_SCRIPT_URL})"

echo "Downloading qgis_setup.sh and friends from branch ${BRANCH}..."

wget -q -O "$SETUP_SCRIPT_PATH" "$SETUP_SCRIPT_URL"
wget -q -O "$STARTUP_SCRIPT_PATH" "$STARTUP_SCRIPT_URL"

chmod +x "$SETUP_SCRIPT_PATH"
chmod +x "$STARTUP_SCRIPT_PATH"

# do the setup
$SETUP_SCRIPT_PATH "$PLUGIN_NAME"
rm -rf "/root/.local/share/QGIS/QGIS3/profiles/default/python/plugins/$PLUGIN_NAME"
ln -s "/tests_directory/$PLUGIN_NAME" "/root/.local/share/QGIS/QGIS3/profiles/default/python/plugins/$PLUGIN_NAME"
apt-get update && apt-get install -y pre-commit python3-coverage
git config --global --add safe.directory /tests_directory

# run the linter/formatter & tests
cd tests_directory
pre-commit run --all-files
python3 -m coverage run -m unittest discover
python3 -m coverage report
python3 -m coverage lcov --include "valhalla/*"
