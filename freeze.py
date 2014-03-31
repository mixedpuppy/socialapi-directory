from flask_frozen import Freezer
from app import createapp;

if __name__ == '__main__':
  app = createapp()
  freezer = Freezer(app)

  #@freezer.register_generator
  #def product_url_generator():
  #    # Return a list. (Any iterable type will do.)
  #    return [
  #        '/',
  #        '/en_US/',
  #        '/js_JP/mixi',
  #    ]

  freezer.freeze()
