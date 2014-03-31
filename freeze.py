from flask_frozen import Freezer
from flask import json
from app import createapp;
import collections

if __name__ == '__main__':
  app = createapp()
  freezer = Freezer(app)

  data = json.load(app.open_resource('static/js/data.json'), object_pairs_hook=collections.OrderedDict)

  @freezer.register_generator
  def product_url_generator():
      # Return a list. (Any iterable type will do.)
      paths = [
          '/',
          '/en_US/'
      ]
      for k, p in data["source"].iteritems():
        for lang in p['lang']:
          paths.append('/'+lang+'/images')
          paths.append('/'+lang+'/'+k+'.html')
      print paths
      return paths

  freezer.freeze()
