__author__ = 'ye'

import png
import StringIO
from hashlib import md5

class PngImageGen:
  GRAY_COLOR = (240, 240, 240, 255)
  WHITE_COLOR = (255,255,255,255)

  @classmethod
  def trueWidthAndHeight(cls, width, _):
    (iw, p) = cls.innerWidthAndPadding(width)
    return iw + 2 * p

  @classmethod
  def innerWidthAndPadding(cls, width):
    padding = width / 8
    return ((width - 2 * padding) / 5 * 5, padding)

  def __init__(self, str, width, height, auth):
    self.secret = hash(str)
    self.auth = auth
    self.row = 0
    self.padding = width / 8
    (self.width, self.padding) = self.innerWidthAndPadding(width)
    self.height = self.width
    self.true_width = self.trueWidthAndHeight(width, height)
    self.block_size = self.width / 5
    colorByte = self.secret[-1]
    self.color = (colorByte % 7 * 36, colorByte % 11 * 23, colorByte % 5 * 63, 255)
    return


  def __iter__(self):
    return self


  def pixelAt(self, row, col):
    if self.auth and row == 0 and col <= 15:
      # SECRET EMBEDDED in the first 16 bytes of the first row
      return (self.secret[col], 240, 240, 0)
    if row == 0 or col == 0 or row == self.true_width - 1 or col == self.true_width - 1:
      return (240,240,240,255)
    if (row < self.padding) or (row >= self.padding + self.height) or \
            (col < self.padding) or (col >= self.padding + self.width):
      return self.GRAY_COLOR
    elif col >= 3 * self.block_size + self.padding:
      return self.pixelAt(row, self.true_width - 1 - col)
    else:
      idx = (row - self.padding) / self.block_size + 5 * ((col - self.padding) / self.block_size)
      if self.secret[idx] % 2 == 0:
        return self.color
      else:
        return self.WHITE_COLOR


  def next(self):
    if self.row >= self.height + 2 * self.padding:
      raise StopIteration
    else:
      self.row = self.row + 1
      return flatten([self.pixelAt(self.row - 1, x) for x in xrange(0,self.true_width)])

def flatten(ls):
  return [x for l in ls for x in l]


def genIdenticonFromStringIntoFile(file, str, auth = False, width = 60, height = 60):
  t = PngImageGen.trueWidthAndHeight(width, height)
  writer = png.Writer(width = t, height = t, planes = 4, alpha=True)
  writer.write(file, PngImageGen(str, width, height, auth = auth))


def hash(name):
  print name
  print type(name)
  return map(ord, md5(str(name)).digest())

def verify(name, bytes):
  print len(bytes)
  reader = png.Reader(bytes = bytes)
  sec = hash(name)
  #buffer = StringIO.StringIO()
  #genIdenticonFromStringIntoFile(buffer, name, 180, 180)
  #buffer.close()
  #val = buffer.getvalue()
  #print len(val)
  #print len(bytes)
  #for i in xrange(881):
  #  if bytes[i] != val[i]:
  #    print "FAIL"

  #return buffer.getvalue() == bytes
  (_,_,s,_) = reader.asDirect()
  s = s.next()
  ex = [s[x * 4] for x in xrange(0,16)]
  print sec
  print ex
  return ex == sec
  print "exception"
  return False