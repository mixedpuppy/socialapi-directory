#!/bin/sh
rm -rf jp-JP en-US css js images index.html
wget -nH -erobots=off -p http://localhost:8888/socialapi-directory/index.html
wget -r -nH erobots=off http://localhost:8888/socialapi-directory/en-US/
wget -nH -erobots=off -p http://localhost:8888/socialapi-directory/jp-JP/mixi.html
cp -rf socialapi-directory/* .
rm -rf socialapi-directory
