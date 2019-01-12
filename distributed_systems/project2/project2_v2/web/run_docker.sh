#!/usr/bin/env bash
#cd web
docker build -t pub_sub .
docker run -p 8081:8081 -t pub_sub