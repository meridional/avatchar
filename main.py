import tornado.ioloop
import tornado.web
import tornado.websocket
import identicon
import tornado.options
from tornado.options import define
import acdb
import json
import StringIO


id_cookie_key = "warp"
name_cookie_key = "username"


def verify_login(handler):
  name = handler.get_cookie(name_cookie_key)
  user = acdb.find_user(name)
  if name:
    if not user:
      return False
  else:
    return False
  secret = handler.get_secure_cookie(id_cookie_key)
  if secret and secret == name:
    return user
  else:
    return False


def confirm_login(handler, name):
  self=handler
  self.set_cookie(name_cookie_key, name)
  self.set_secure_cookie(id_cookie_key, name)


class RegisterHandler(tornado.web.RequestHandler):
  def post(self):
    if verify_login(self):
      self.redirect("/")
      print "success"
      return
    name = self.request.arguments["name"][0]
    if acdb.find_user(name):
      self.redirect("/")
    else:
      confirm_login(self, name)
      user = acdb.insert_user(name)
      self.render("./static/register_successful.html", user = user)



class MainHandler(tornado.web.RequestHandler):

  def get(self):
    if not verify_login(self):
      #self.set_cookie(name_cookie_key, "harry")
      #self.set_secure_cookie(id_cookie_key, "harry")
      self.render("./static/register.html")
    else:
      self.render("./static/chat.html")


class IdenticonHandler(tornado.web.RequestHandler):
  def get(self, name):
    if name[-1] == '/':
      name = name[0:-1]
    #buffer.close()
    #self.clear()
    self.write(acdb.get_identicon_for_user_name(name, auth=False).read(9999))
    self.set_header('Content-Type', 'image/png')
    #self.finish()


class VerificationHandler(tornado.web.RequestHandler):
  def post(self, *args, **kwargs):
    file1 = self.request.files['identicon'][0]
    name = self.request.arguments["name"][0]
    if acdb.find_user(name) and identicon.verify(name, file1["body"]):
      self.write('success')
      confirm_login(self, name)
    self.write('fail')


current_user = {}

class RealTimeRocker(tornado.websocket.WebSocketHandler):

  def open(self):
    u = verify_login(self)
    if u:
      current_user[self] = u
      return
    self.close()

  def on_message(self, message):
    #print type(message)

    msg = acdb.user_said_something(current_user[self], message)
    # broadcast
    for conn in current_user:
      print type(msg.user.img_url)
      conn.write_message(
        {"name":msg.user.name,
         "img":"/identicon/" + msg.user.name,
         "msg":message,
         "datetime":str(msg.datetime)})


  def on_close(self):
    if current_user.has_key(self):
      del current_user[self]

class SecretHandler(tornado.web.RequestHandler):
  def get(self, name):
    if name[-1] == '/':
      name = name[0:-1]
    u = verify_login(self)
    print u.name
    print u.secret_url
    if u and u.name == name:
      f = acdb.get_identicon_for_user_name(name, auth=True)
      self.write(f.read(9999))
      self.set_header('Content-Type', 'image/png')
    else:
      self.redirect(r'/identicon/' + name)


# routes
application = tornado.web.Application([
  (r"/", MainHandler),
  (r"/rush/.*/?", RealTimeRocker),
  (r'/identicon/(.*)/?', IdenticonHandler),
  (r'/secret/(.*)/?', SecretHandler),
  (r'/login/?', VerificationHandler),
  (r'/register/?', RegisterHandler),
  (r'/(.*)', tornado.web.StaticFileHandler, {"path":"./static/"})
])

application.settings['cookie_secret'] = \
    "afe96cbb5b5c05bb5514490c2f44f3297a925acca8548b330b2125a745dd4cf8"


define("port", default=8888, help="run on given port", type=int)
define("mongourl", default='mongodb://localhost:27017/')


if __name__ == "__main__":
  tornado.options.parse_command_line()
  acdb.init_db(tornado.options.options.mongourl)
  application.listen(tornado.options.options.port)
  tornado.ioloop.IOLoop.instance().start()