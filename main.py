import tornado.ioloop
import tornado.web
import tornado.websocket
import identicon
from array import array
import StringIO

#import jinja2
import json


class MainHandler(tornado.web.RequestHandler):
  def get(self, name):
    self.write("<html>" + "<img src=\"/identicon/" + name + "\">" + "</html>")


class IdenticonHandler(tornado.web.RequestHandler):
  def get(self, name):
    buffer = StringIO.StringIO()
    auth = False
    width = 60
    height = 60
    if self.get_secure_cookie("warp") == name:
      auth = True
      width = 180
      height = 180

    identicon.genIdenticonFromStringIntoFile(buffer, name, auth, width, height)
    #buffer.close()
    #self.clear()
    self.write(buffer.getvalue())
    self.set_header('Content-Type', 'image/png')
    #self.finish()


class VerificationHandler(tornado.web.RequestHandler):
  def post(self, *args, **kwargs):
    file1 = self.request.files['file1'][0]
    name = self.request.arguments["name"][0]
    if identicon.verify(name, file1["body"]):
      self.write("Pass")
    else:
      self.write("Fail")


class RealTimeRocker(tornado.websocket.WebSocketHandler):
    def open(self):
        self.close()
        return

    def on_message(self, message):
        self.write_message(message + u", hello")


application = tornado.web.Application([
  (r"/json/(.*)", MainHandler),
  (r"/ws/.*", RealTimeRocker),
  (r'/identicon/(.*)', IdenticonHandler),
  (r'/upload', VerificationHandler),
  (r'/(.*)', tornado.web.StaticFileHandler, {"path":"."})
])

application.settings['cookie_secret'] = \
    "afe96cbb5b5c05bb5514490c2f44f3297a925acca8548b330b2125a745dd4cf8"

if __name__ == "__main__":
    application.listen(80)
    tornado.ioloop.IOLoop.instance().start()