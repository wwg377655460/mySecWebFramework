#coding:utf8
__author__ = 'wsdevotion'

def filter_SQL(url):
    url = url.lower()
    print url.find('select')!=-1
    #判断是否有sql语句
    if url.find('select')!=-1 or  url.find('union')!=-1 or url.find('insert')!=-1 or url.find('update')!=-1 or url.find('delete')!=-1:
        return False
    return True