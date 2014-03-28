from flask_frozen import Freezer
from app import createapp;

if __name__ == '__main__':
  app = createapp()
  freezer = Freezer(app)
  freezer.freeze()
