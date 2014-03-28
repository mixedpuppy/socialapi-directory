import re, os, sys
from flask import Flask, request, json, render_template
from pystache.renderer import Renderer
import collections

def createapp():
  app = Flask(__name__, static_folder='')
  app.debug = True

  data = json.load(app.open_resource('js/data.json'), object_pairs_hook=collections.OrderedDict)

  def dataFixup(k, p, locale):
    p['key'] = k
    if locale in p["lang"]:
      p["lang"]["default"] = p["lang"][locale]
    else:
      p["lang"]["default"] = p["lang"]["en_US"]

    # for demo site purposes, massage the data
    # various lang pack fixups, use manifest entries for missing lang entries
    d = p["lang"]["default"]
    if 'images' not in d:
      d['images'] = {}
    if 'logo' not in d['images']:
      d['images']['logo'] = p['manifest']['icon64URL'] or p['manifest']['icon32URL']
    if 'description' not in d:
      d['description'] = p['manifest']['description'];
    p['manifest'] = json.dumps(p['manifest'])
    return p
  
  def renderTemplate(template, data, locale, path=None):
    # add localized strings
    data["locale"] = locale
    if locale in data['strings']:
      data['strings'] = data['strings'][locale]
    else:
      data['strings'] = data['strings']["en_US"]

    if path and path in data["source"]:
      d = dataFixup(path, data["source"][path], locale)
      d['strings'] = data['strings']
      d['locale'] = data['locale']
      #print >> sys.stdout, json.dumps(d)
      return render_template(template, **d)
    else:
      for k, p in data["source"].iteritems():
        p['key'] = k
        dataFixup(k, p, locale)

      if locale in data["carousel"]:
        names = data["carousel"][locale]
      else:
        names = data["carousel"]["en_US"]
      data["slider"] = []
      for name in names:
        data["slider"].append(data["source"][name])
  
      return render_template(template, **data)
  
  @app.route('/')
  def root():
    return renderTemplate('index.html', dict(data), "en_US")

  @app.route('/<root>/')
  def rootname(root):
    print "rendering ", root
    # if root is locale, capture that, but use the same local file paths
    if re.search('\w{2}_\w{2}', root):
      return renderTemplate('index.html', dict(data), root)
    return renderTemplate('provider.html', dict(data), "en_US", root)

  import os
  @app.route('/<root>/<path:path>')
  def static_proxy(root, path):
    # if root is locale, capture that, but use the same local file paths
    if re.search('\w{2}_\w{2}', root):
      locale = root
      path = path.split("/")[0]
      print "path is ", path
    # send_static_file will guess the correct MIME type
    if root in ["css", "images", "fonts", "js"]:
      return app.send_static_file(os.path.join(root, path))
    template = path and "provider.html" or "index.html"
    print "template is ", template
    return renderTemplate(template, dict(data), locale, path)

  return app

if __name__ == '__main__':
  app = createapp()
  app.run(port=8888)