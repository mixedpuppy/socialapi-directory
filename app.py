import re, os, sys
from flask import Flask, request, json, render_template, redirect
from werkzeug.routing import BaseConverter
from pystache.renderer import Renderer
import collections

class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

def createapp():
  app = Flask(__name__, static_folder='')
  app.debug = True

  app.url_map.converters['regex'] = RegexConverter

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
        dataFixup(k, p, locale)

      if locale in data["carousel"]:
        names = data["carousel"][locale]
      else:
        names = data["carousel"]["en_US"]
      data["slider"] = []
      for name in names:
        data["slider"].append(data["source"][name])
  
      return render_template(template, **data)
  
  @app.route('/<regex("\w{2}_\w{2}"):locale>/<path>')
  def static_proxy(locale, path):
    # if root is locale, capture that, but use the same local file paths
    print "root in ", locale
    print "path in ", path
    try:
      root, path = path.split('/', 2)
    except ValueError, e:
      root = None
    print "locale is ", locale
    print "root is ", root
    print "path is ", path
    # send_static_file will guess the correct MIME type
    if root in ["css", "images", "fonts", "js"]:
      return app.send_static_file(os.path.join(root, path))
    if path == "index.html":
      template = path
    else:
      template = path and "provider.html" or "index.html"
    print "template is ", template
    return renderTemplate(template, dict(data), locale, path)

  @app.route('/<regex("\w{2}_\w{2}"):locale>/<path:path>')
  def static_files(locale, path):
    return app.send_static_file(path)
  

  @app.route('/<regex("\w{2}_\w{2}"):locale>/')
  def rootname(locale):
    print "rendering ", locale
    # if root is locale, capture that, but use the same local file paths
    return renderTemplate('index.html', dict(data), root)

  @app.route('/')
  def root():
    # the server should handle a redirect. Since the frozen static pages will be
    # served on github pages for testing, we have a redirect located in the top
    # level index page.  We use that here to ensure that works as well.
    return app.send_static_file("index.html")


  return app
