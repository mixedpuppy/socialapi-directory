#!/bin/sh
pybabel extract -F babel-json.cfg -o data/templates/LC_MESSAGES/messages.pot .
for __DIR in `ls data`
do
  if [ "$__DIR" != "templates" ];
  then
    pybabel update -i data/templates/LC_MESSAGES/messages.pot -d data -l $__DIR
  fi
done
pybabel compile -f -d data
