import re, os
from flask import Flask, request
# set the project root directory as the static folder, you can set others.
app = Flask(__name__, static_folder='')

@app.route('/')
def root():
  return app.send_static_file('index.html')

@app.route('/<root>')
@app.route('/<root>/')
def rootname(root):
  return app.send_static_file('index.html')

import os
@app.route('/<root>/<path:path>')
def static_proxy(root, path):
  # if root is locale, capture that, but use the same local file paths
  if re.search('\w{2}_\w{2}', root):
    locale = root
    root, path = path.split("/", 2)

  # send_static_file will guess the correct MIME type
  if root in ["css", "images", "fonts", "js"]:
    return app.send_static_file(os.path.join(root, path))
  return app.send_static_file('index.html')

if __name__ == '__main__':
  app.run(debug=True)