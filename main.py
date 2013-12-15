import tornado.ioloop
import tornado.web
import tornado.websocket
import identicon
import tornado.options
from tornado.options import define

import StringIO



id_cookie_key = "warp"
name_cookie_key = "username"

class MainHandler(tornado.web.RequestHandler):
  def verify(self):
    secret = self.get_secure_cookie(id_cookie_key)
    if secret and secret == self.get_cookie(name_cookie_key):
      return True
    else:
      return False


  def get(self):
    if not self.verify():
      self.set_cookie(name_cookie_key, "harry")
      self.set_secure_cookie(id_cookie_key, "harry")
      self.write("fail")
    else:
      self.write("pass")


class IdenticonHandler(tornado.web.RequestHandler):
  def get(self, name):
    buffer = StringIO.StringIO()
    auth = False
    width = 60
    height = 60
    if self.get_secure_cookie(id_cookie_key) == name:
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


# routes
application = tornado.web.Application([
  (r"/", MainHandler),
  (r"/rush/.*", RealTimeRocker),
  (r'/identicon/(.*)', IdenticonHandler),
  (r'/upload', VerificationHandler),
  #(r'/(.*)', tornado.web.StaticFileHandler, {"path":"."})
])

application.settings['cookie_secret'] = \
    "afe96cbb5b5c05bb5514490c2f44f3297a925acca8548b330b2125a745dd4cf8"


define("port", default=8888, help="run on given port", type=int)
define("mongourl", default='mongodb://localhost:27017/')


if __name__ == "__main__":
  tornado.options.parse_command_line()
  application.listen(tornado.options.options.port)
  tornado.ioloop.IOLoop.instance().start()