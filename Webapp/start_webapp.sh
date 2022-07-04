#!/bin/bash

echo "Starting application on port $PORT and uplink key $KEY..."

anvil-app-server --app DrkSrch --uplink-key $KEY --port $PORT
