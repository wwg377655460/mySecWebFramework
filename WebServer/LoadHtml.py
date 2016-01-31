import os

__author__ = 'wsdevotion'

def loadFile(name):
    if os.path.exists(name):
        file = open(name, 'r')
        return file.read()
    else:
        return '404 Not Found'
