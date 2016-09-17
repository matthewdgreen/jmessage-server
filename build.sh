#!/bin/bash

docker pull postgres

docker build -t jmessage/server .
