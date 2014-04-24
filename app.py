import re, os, sys
from flask import Flask, Blueprint, request, json, render_template, redirect, url_for
from werkzeug.routing import BaseConverter
from pystache.renderer import Renderer
import copy
import collections

class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

def createapp():
  demo = '-d' in sys.argv
  #app.config["APPLICATION_ROOT"] = "/socialapi-directory"
  app = Flask(__name__)
  app.debug = True

  app.url_map.converters['regex'] = RegexConverter

  bp = Blueprint('bp', __name__)

  def dataFixup(k, p, locale):
    p['key'] = k
    if locale in p["lang"]:
      p["lang"]["default"] = p["lang"][locale]
    else:
      p["lang"]["default"] = p["lang"]["en-US"]

    # for demo site purposes, massage the data
    # various lang pack fixups, use manifest entries for missing lang entries
    d = p["lang"]["default"]
    if 'images' not in d:
      d['images'] = {}
    if 'logo' not in d['images']:
      d['images']['logo'] = p['manifest']['icon64URL'] or p['manifest']['icon32URL']
    if 'description' not in d:
      d['description'] = p['manifest']['description'];
    
    # aid activated providers in knowing what locale a user installed from
    for n,v in p['manifest'].iteritems():
        if isinstance(v, (str, unicode)):
            p['manifest'][n] = v.replace('__T_LOCALE__', locale)

    p['manifestData'] = json.dumps(p['manifest'])
    return p
  
  def renderTemplate(template, data, locale, path=None, base="/"):
    if demo:
        # add any mockup providers to our directory
        for k, p in data["demo"].iteritems():
          data["source"][k] = p
    data["production"] = not demo
    basehref = ""
    if base:
      basehref = base + '/' + locale + '/'
    elif locale:
      basehref = locale + '/'
    # add localized strings
    data["locale"] = locale
    if locale in data['strings']:
      data['strings'] = data['strings'][locale]
    else:
      data['strings'] = data['strings']["en-US"]

    if path:
      path = os.path.splitext(path)[0]
    if path and path in data["source"]:
      # on a detail page, just copy the specific data we need
      d = dataFixup(path, data["source"][path], locale)
      d['strings'] = data['strings']
      d['locale'] = data['locale']
      d['production'] = data['production']
      d["basehref"] = basehref
      #print >> sys.stdout, json.dumps(d)
      return render_template(template, **d)
    else:
      for k, p in data["source"].iteritems():
        dataFixup(k, p, locale)

      if locale in data["carousel"]:
        names = data["carousel"][locale]
      else:
        names = data["carousel"]["en-US"]
      data["slider"] = []
      for name in names:
        data["slider"].append(data["source"][name])
  
      data["basehref"] = basehref
      return render_template(template, **data)
  
  @bp.route('/<regex("\w{2}-\w{2}"):locale>/<path:path>')
  def static_proxy(base, locale=None, path=None):
    # if root is locale, capture that, but use the same local file paths
    try:
      root, path = path.split('/', 1)
    except ValueError, e:
      root = None
    # send_static_file will guess the correct MIME type
    if root in ["css", "images", "fonts", "js"]:
      return app.send_static_file(os.path.join(root, path))
    if path == "index.html":
      template = path
    else:
      template = path and "provider.html" or "index.html"
    appData = json.load(app.open_resource('data.json'), object_pairs_hook=collections.OrderedDict)
    return renderTemplate(template, appData, locale, path, base)

  @app.route('/<regex("\w{2}-\w{2}"):locale>/<path>')
  def app_static_proxy(locale=None, path=None):
    return static_proxy(None, locale, path)

  @bp.route('/<path:path>')
  def static_files(base=None, path=None):
    if base and not path:
      return index(None, locale)
    if base in ["css", "images", "fonts", "js"]:
      path = base + "/" + path
    return app.send_static_file(path)

  @bp.route('/<regex("\w{2}-\w{2}"):locale>/')
  def index(base, locale):
    # if root is locale, capture that, but use the same local file paths
    appData = json.load(app.open_resource('data.json'), object_pairs_hook=collections.OrderedDict)
    return renderTemplate('index.html', appData, locale, base=base)

  @app.route('/<regex("\w{2}-\w{2}"):locale>/')
  def app_index(locale):
    return index(None, locale)

  @bp.route("/")
  @app.route("/")
  def root(base=None):
    # the server should handle a redirect. Since the frozen static pages will be
    # served on github pages for testing, we have a redirect located in the top
    # level index page.  We use that here to ensure that works as well.
    return app.send_static_file("index.html")

  app.register_blueprint(bp, url_prefix="/<path:base>")


  return app
