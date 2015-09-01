import re, os, sys
from datetime import datetime
import flask
from flask import Flask, request, json, render_template, redirect, url_for, abort
from flask.ext.babel import Babel
from werkzeug.routing import BaseConverter
import collections

TRANSLATIONS = ['cs', 'de', 'en-US', 'en_US', 'en-GB', 'en_GB', 'es', 'fr', 'gl',
                'hu', 'it', 'ja', 'nl', 'pt-BR', 'pt_BR', 'ru', 'sl', 'uk',
                'zh-CN', 'zh_CN', 'zh-Hans-CN', 'zh_Hans_CN',
                'zh-Hant-TW', 'zh_Hant_TW', 'zh-TW', 'zh_TW']

# creating a data url for an image
import base64
_imageCache = {}
def createDataURL(imagePath):
  if imagePath[:5] in ["data:", "http:"] or imagePath[:6] == "https:":
    return imagePath
  if imagePath in _imageCache:
    return _imageCache[imagePath]
  print "converting", imagePath
  with open("static/"+imagePath, "rb") as image_file:
      encoded_string = base64.b64encode(image_file.read())
      if imagePath[-3:] == "png":
        _imageCache[imagePath] = "data:image/png;base64,"+encoded_string
      elif imagePath[-3:] == "jpg":
        _imageCache[imagePath] = "data:image/jpg;base64,"+encoded_string
      else:
        raise "unknown image type"
  return _imageCache[imagePath]

def getImages(k, locale):
  imagePath = "static/images/"+k
  images = {}
  names = ["logo", "fulllogo", "detaillogo", "share", "carousel", "sidebarmenu", "sidebarbutton"]
  for name in names:
    filenames = ["%s.%s.png" % (name, locale), "%s.%s.jpg" % (name, locale), "%s.png" % name, "%s.jpg" % name, "%s.en-US.png" % name, "%s.en-US.jpg" % name]
    for fn in filenames:
      fn = os.path.join("images", k, fn)
      if os.path.exists(os.path.join("static", fn)):
        images[name] = fn
        break
  # get detail images
  details = []
  for i in range(1,3):
    filenames = ["detail.%d.%s.png" % (i, locale), "detail.%d.%s.jpg" % (i, locale), "detail.%d.png" % i, "detail.%d.jpg" % i, "detail.%d.gif" % i, "detail.%d.en-US.png" % i, "detail.%d.en-US.jpg" % i]
    for fn in filenames:
      fn = os.path.join("images", k, fn)
      if os.path.exists(os.path.join("static", fn)):
        details.append(fn)
        break
  if len(details) == 1:
    images["detail"] = details[0]
  elif len(details) > 1:
    images["details"] = details
  #print k, repr(images)
  return images

# creating a data url for an image
import base64
_imageCache = {}
def createDataURL(imagePath):
  if imagePath[:5] in ["data:", "http:"] or imagePath[:6] == "https:":
    return imagePath
  if imagePath in _imageCache:
    return _imageCache[imagePath]
  #print "converting", imagePath
  with open("static/"+imagePath, "rb") as image_file:
      encoded_string = base64.b64encode(image_file.read())
      if imagePath[-3:] == "png":
        _imageCache[imagePath] = "data:image/png;base64,"+encoded_string
      elif imagePath[-3:] == "jpg":
        _imageCache[imagePath] = "data:image/jpg;base64,"+encoded_string
      else:
        raise "unknown image type"
  return _imageCache[imagePath]

class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

def createapp():
  demo = '-d' in sys.argv
  app = Flask(__name__)
  if '--debug' in sys.argv:
    app.debug = True
  app.url_map.converters['regex'] = RegexConverter
  babel = Babel(app)

  config = json.load(app.open_resource('config.json'), object_pairs_hook=collections.OrderedDict)

  @app.context_processor
  def utility_processor():
    return dict(createDataURL=createDataURL)

  def get_supported_locales():
    langs = {}
    for b in babel.list_translations():
      if not demo and str(b) not in TRANSLATIONS:
        # print str(b)," is not in ",TRANSLATIONS
        continue
      if b.territory:
        langs["%s-%s" % (b.language, b.territory)] = b.display_name
      else:
        langs[b.language] = b.display_name
    return langs

  @babel.localeselector
  def get_locale():
    print [str(b) for b in babel.list_translations()]
    lang = request.path[1:].split('/', 1)[0].replace('-', '_')
    langs = {}
    for b in babel.list_translations():
      if not demo and str(b) not in TRANSLATIONS:
        continue
      if b.territory:
        langs["%s_%s" % (b.language, b.territory)] = str(b)
      else:
        langs[b.language] = str(b)
    #print lang, langs
    if lang in langs.keys():
      return lang
    else:
      return 'en_US'

  def dataFixup(k, p, locale):
    images = getImages(k, locale)
    p['key'] = k
    #if locale in p["lang"]:
    #  p["lang"]["default"] = p["lang"][locale]
    #else:
    #  p["lang"]["default"] = p["lang"]["en-US"]

    # make manifest icons data urls
    for image in ["iconURL", "icon32URL", "icon64URL", "unmarkedIcon", "markedIcon"]:
      if image in p['manifest']:
        p['manifest'][image] = createDataURL(p['manifest'][image])
      #else:
      #  print "WARNING: ",image,"missing from manfiest for",p['manifest']['origin']

    # for demo site purposes, massage the data
    # various lang pack fixups, use manifest entries for missing lang entries
    #d = p["lang"]["default"]
    d = p["viewData"]
    d['images'] = getImages(k, locale)
    if 'images' not in d:
      d['images'] = {}
    if 'logo' not in d['images']:
      d['images']['logo'] = p['manifest']['icon64URL'] or p['manifest']['icon32URL']
    if 'description' not in d:
      d['description'] = p['manifest']['description'];

    # make manifest icons data urls
    for image in ["iconURL", "icon32URL", "icon64URL", "unmarkedIcon", "markedIcon"]:
      if image in p['manifest']:
        p['manifest'][image] = createDataURL(p['manifest'][image])
      #else:
      #  print "WARNING: ",image,"missing from manfiest for",p['manifest']['origin']

    # aid activated providers in knowing what locale a user installed from
    for n,v in p['manifest'].iteritems():
        if isinstance(v, (str, unicode)):
            p['manifest'][n] = v.replace('__T_LOCALE__', locale)
            p['manifest'][n] = v.replace('_T__BASEURL__', os.path.dirname(flask.request.base_url))

    p['manifestData'] = json.dumps(p['manifest'])
    return p
  
  def firefoxReleases(schedule):
    today = datetime.today()
    last = []
    for d, a in schedule.iteritems():
        if today < datetime.strptime(d, "%Y-%m-%d"):
            return a
        last = a
    return last

  def renderTemplate(template, locale, path=None):
    locales = get_supported_locales()
    #if locale not in locales:
    #  abort(404)

    out = render_template('data-en.json')
    data = json.loads(out, object_pairs_hook=collections.OrderedDict)

    data["production"] = not demo
    basehref = ""
    if locale:
      basehref = locale + '/'
    # add localized strings
    data["locale"] = locale

    if path:
      path = os.path.splitext(path)[0]
      if path not in data["source"]:
        abort(404)
    if path:
      # on a detail page, just copy the specific data we need
      d = dataFixup(path, data["source"][path], locale)
      d['translations'] = get_supported_locales()
      d['locale'] = data['locale']
      d['production'] = data['production']
      d["basehref"] = basehref
      #print >> sys.stdout, json.dumps(d)
      d["releases"] = firefoxReleases(config["firefox-releases"])
      d['current_year'] = datetime.now().year
      d['config'] = config
      return render_template(template, **d)
    else:
      for k, p in data["source"].iteritems():
        dataFixup(k, p, locale)
      if locale in config["carousel"]:
        names = config["carousel"][locale]
      else:
        names = config["carousel"]["en-US"]
      data["slider"] = []
      for name in names:
        data["slider"].append(data["source"][name])

      data["shareProviders"] = []
      if locale in config["sharePanel"]:
        names = config["sharePanel"][locale]['providers']
      else:
        names = config["sharePanel"]["en-US"]['providers']
      for name in names:
        data["shareProviders"].append(data["source"][name])

      keys = data["source"].keys()
      keys.sort()
      data["source"] = [data["source"][key] for key in keys]
      data["basehref"] = basehref
      data["releases"] = firefoxReleases(config["firefox-releases"])
      data['translations'] = get_supported_locales()
      data['current_year'] = datetime.now().year
      data['config'] = config
      return render_template(template, **data)

  @app.route('/<regex("\w{2}(?:-\w{2})?"):locale>/<path:path>')
  def static_proxy(locale=None, path=None):
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
    return renderTemplate(template, locale, path)

  @app.route('/<regex("\w{2}(?:-\w{2})?"):locale>/activated/')
  @app.route('/<regex("\w{2}(?:-\w{2})?"):locale>/activated/<path:path>')
  def app_activated(locale=None, path=None):
    template = path and "activated.html" or "activatedIndex.html"
    return renderTemplate(template, locale, path)

  @app.route('/<regex("\w{2}(?:-\w{2})?"):locale>/sharePanel.html')
  def app_sharePanel(locale=None):
    return renderTemplate('sharePanel.html', locale)

  @app.route('/<regex("\w{2}(?:-\w{2})?"):locale>/<path>')
  def app_static_proxy(locale=None, path=None):
    return static_proxy(locale, path)

  @app.route('/<path:path>')
  def static_files(path=None):
    if not path:
      return redirectpage()
    return app.send_static_file(path)

  @app.route('/<regex("\w{2}(?:-\w{2})?"):locale>/')
  def app_index(locale):
    if not demo and locale not in TRANSLATIONS:
        return app.send_static_file("redir.html")
    return renderTemplate('index.html', locale)

  @app.route("/redirect.html")
  def redirectpage(base=None):
    # the server should handle a redirect. Since the frozen static pages will be
    # served on github pages for testing, we have a redirect located in the top
    # level index page.  We use that here to ensure that works as well.
    return app.send_static_file("redirect.html")

  @app.route("/")
  def root(base=None):
    # the server should handle a redirect. Since the frozen static pages will be
    # served on github pages for testing, we have a redirect located in the top
    # level index page.  We use that here to ensure that works as well.
    return app.send_static_file("index.html")

  return app


if __name__ == '__main__':
  app = createapp()
  app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8888)))
