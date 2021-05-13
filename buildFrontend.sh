#!/bin/bash

cd frontend
yarn install
yarn build
cp -r public/* ../static/
cp -r dist/* ../static/
