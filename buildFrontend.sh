#!/bin/bash

mkdir -p static
rm -rf static/*
cd frontend
yarn install
yarn build
cp -r public/* ../static/
cp -r dist/* ../static/
