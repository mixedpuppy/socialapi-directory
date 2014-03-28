from app import createapp;

if __name__ == '__main__':
  app = createapp()
  app.run(port=8888)