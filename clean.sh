#!/bin/bash

docker stop jmessage
docker stop jmessage_db

docker rm jmessage
docker rm jmessage_db
docker rmi jmessage/server
