#!/bin/sh
rm -rf jp-JP/mixi.html en-US css js images index.html
wget -nH -erobots=off -p http://localhost:8888/socialapi-directory/index.html
wget -r -nH -erobots=off http://localhost:8888/socialapi-directory/en-US/activated/
wget -r -nH -erobots=off http://localhost:8888/socialapi-directory/en-US/
wget -r -nH -erobots=off http://localhost:8888/socialapi-directory/en-US/sharePanel.html
wget -nH -erobots=off -p http://localhost:8888/socialapi-directory/jp-JP/mixi.html
wget -nH -erobots=off -p http://localhost:8888/socialapi-directory/de/goal.html
wget -nH -erobots=off -p http://localhost:8888/socialapi-directory/fr/goal.html
wget -nH -erobots=off -p http://localhost:8888/socialapi-directory/es-AR/goal.html
wget -nH -erobots=off -p http://localhost:8888/socialapi-directory/es-ES/goal.html
wget -nH -erobots=off -p http://localhost:8888/socialapi-directory/pt-BR/goal.html
wget -nH -erobots=off -p http://localhost:8888/socialapi-directory/it/goal.html
wget -nH -erobots=off -p http://localhost:8888/socialapi-directory/id/goal.html
wget -nH -erobots=off -p http://localhost:8888/socialapi-directory/ja/goal.html
wget -nH -erobots=off -p http://localhost:8888/socialapi-directory/nl/goal.html
cp -rf socialapi-directory/* .
rm -rf socialapi-directory
rm en-US/activated/
