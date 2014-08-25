import re, os, sys
import flask
from flask import Flask, Blueprint, g, request, json, render_template, redirect, url_for
from flask.ext.babel import Babel
from werkzeug.routing import BaseConverter
import copy
import collections

TRANSLATIONS = ['en-US', 'zh-TW', 'fr', 'gl', 'de', 'it', 'ja', 'ru', 'es']

class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

def createapp():
  demo = '-d' in sys.argv
  #app.config["APPLICATION_ROOT"] = "/socialapi-directory"
  app = Flask(__name__)
  app.debug = True
  #app.config.from_pyfile('babel.cfg')
  babel = Babel(app)

  app.url_map.converters['regex'] = RegexConverter

  bp = Blueprint('bp', __name__)

  def get_supported_locales():
    langs = {}
    for b in babel.list_translations():
      if not demo and str(b) not in TRANSLATIONS:
        continue
      if b.territory:
        langs["%s-%s" % (b.language, b.territory)] = b.display_name
      else:
        langs[b.language] = b.display_name
    return langs

  @babel.localeselector
  def get_locale():
    #print [str(b) for b in babel.list_translations()]
    lang = request.path[1:].split('/', 1)[0].replace('-', '_')
    langs = {}
    for b in babel.list_translations():
      if not demo and str(b) not in TRANSLATIONS:
        continue
      if b.territory:
        langs["%s_%s" % (b.language, b.territory)] = str(b)
      else:
        langs[b.language] = str(b)
    print lang, langs
    if lang in langs.keys():
      return lang
    else:
      return 'en_US'

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
            p['manifest'][n] = v.replace('_T__BASEURL__', os.path.dirname(flask.request.base_url))

    p['manifestData'] = json.dumps(p['manifest'])
    return p
  
  def firefoxReleases(schedule):
    from datetime import datetime
    today = datetime.today()
    last = []
    for d, a in schedule.iteritems():
        last = a
        if today > datetime.strptime(d, "%Y-%m-%d"):
            return a
    return last

  def renderTemplate(template, data, locale, path=None, base=""):
    data["production"] = not demo
    basehref = ""
    if path:
        baseurl = os.path.dirname(path)
    if base:
      basehref = "/".join([base, locale]) + '/'
    elif locale:
      basehref = locale + '/'
    # add localized strings
    data["locale"] = locale

    if path:
      path = os.path.splitext(path)[0]
    if path and path in data["source"]:
      # on a detail page, just copy the specific data we need
      d = dataFixup(path, data["source"][path], locale)
      d['translations'] = get_supported_locales()
      d['locale'] = data['locale']
      d['production'] = data['production']
      d["basehref"] = basehref
      #print >> sys.stdout, json.dumps(d)
      d["releases"] = firefoxReleases(data["firefox-releases"])
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

      data["shareProviders"] = []
      if locale in data["sharePanel"]:
        names = data["sharePanel"][locale]
      else:
        names = data["sharePanel"]["en-US"]
      for name in names:
        data["shareProviders"].append(data["source"][name])

      keys = data["source"].keys()
      keys.sort()
      data["source"] = [data["source"][key] for key in keys]
      data["basehref"] = basehref
      data["releases"] = firefoxReleases(data["firefox-releases"])
      data['translations'] = get_supported_locales()
      return render_template(template, **data)
  
  @bp.route('/<regex("\w{2}(?:-\w{2})?"):locale>/<path:path>')
  def static_proxy(base, locale=None, path=None):
    # if root is locale, capture that, but use the same local file paths
    try:
      root, path = path.split('/', 1)
    except ValueError, e:
      root = locale
    # send_static_file will guess the correct MIME type
    if root in ["css", "images", "fonts", "js"]:
      return app.send_static_file(os.path.join(root, path))
    if path == "index.html":
      template = path
    else:
      template = path and "provider.html" or "index.html"
    appData = json.load(app.open_resource('data.json'), object_pairs_hook=collections.OrderedDict)
    return renderTemplate(template, appData, locale, path, base)

  @bp.route('/<regex("\w{2}(?:-\w{2})?"):locale>/activated/')
  @bp.route('/<regex("\w{2}(?:-\w{2})?"):locale>/activated/<path:path>')
  def bp_activated(base, locale=None, path=None):
    # if root is locale, capture that, but use the same local file paths
    appData = json.load(app.open_resource('data.json'), object_pairs_hook=collections.OrderedDict)
    template = path and "activated.html" or "activatedIndex.html"
    return renderTemplate(template, appData, locale, path, base=base)
  @app.route('/<regex("\w{2}(?:-\w{2})?"):locale>/activated/')
  @app.route('/<regex("\w{2}(?:-\w{2})?"):locale>/activated/<path:path>')
  def app_activated(locale=None, path=None):
    appData = json.load(app.open_resource('data.json'), object_pairs_hook=collections.OrderedDict)
    template = path and "activated.html" or "activatedIndex.html"
    return renderTemplate(template, appData, locale, path)

  @bp.route('/<regex("\w{2}(?:-\w{2})?"):locale>/sharePanel.html')
  def bp_sharePanel(base, locale=None):
    # if root is locale, capture that, but use the same local file paths
    appData = json.load(app.open_resource('data.json'), object_pairs_hook=collections.OrderedDict)
    return renderTemplate('sharePanel.html', appData, locale, base=base)
  @app.route('/<regex("\w{2}(?:-\w{2})?"):locale>/sharePanel.html')
  def app_sharePanel(locale=None):
    appData = json.load(app.open_resource('data.json'), object_pairs_hook=collections.OrderedDict)
    return renderTemplate('sharePanel.html', appData, locale)

  @app.route('/<regex("\w{2}(?:-\w{2})?"):locale>/<path>')
  def app_static_proxy(locale=None, path=None):
    return static_proxy(None, locale, path)

  @bp.route('/<path:path>')
  def static_files(base=None, path=None):
    if base and not path:
      return index(None, locale)
    if base in ["css", "images", "fonts", "js"]:
      path = base + "/" + path
    return app.send_static_file(path)

  @bp.route('/<regex("\w{2}(?:-\w{2})?"):locale>/')
  def index(base, locale):
    # if root is locale, capture that, but use the same local file paths
    if not demo and locale not in TRANSLATIONS:
        return app.send_static_file("redir.html")
    appData = json.load(app.open_resource('data.json'), object_pairs_hook=collections.OrderedDict)
    return renderTemplate('index.html', appData, locale, base=base)

  @app.route('/<regex("\w{2}(?:-\w{2})?"):locale>/')
  def app_index(locale):
    if not demo and locale not in TRANSLATIONS:
        return app.send_static_file("redir.html")
    return index(None, locale)

  @bp.route("/redirect.html")
  @app.route("/redirect.html")
  def redirectpage(base=None):
    # the server should handle a redirect. Since the frozen static pages will be
    # served on github pages for testing, we have a redirect located in the top
    # level index page.  We use that here to ensure that works as well.
    return app.send_static_file("redirect.html")

  @bp.route("/")
  @app.route("/")
  def root(base=None):
    # the server should handle a redirect. Since the frozen static pages will be
    # served on github pages for testing, we have a redirect located in the top
    # level index page.  We use that here to ensure that works as well.
    return app.send_static_file("index.html")

  app.register_blueprint(bp, url_prefix="/<path:base>")


  return app


if __name__ == '__main__':
  app = createapp()
  app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8888)))
