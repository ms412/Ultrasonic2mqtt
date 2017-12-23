
from configobj import ConfigObj

class configfile(object):
    def __init__(self, filename):
        self._filename = filename

    def openfile(self):
        dict = {}
        try:
            #   print('opem')
            data = ConfigObj(self._filename)

                # fh=open(self._filename, 'r')
                # with open(self._filename)as fh:
                # data = ujson.load(fh)
                # print('test',data,fh)
                # fh.close()
        except:
            data = None
            #  print('failed')

        return data
