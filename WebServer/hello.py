#coding:utf8
import hashlib
import json
import socket
import urllib2
from urlparse import parse_qs
import re
import uuid
import redis
import requests
from Filter_SQL import filter_SQL
from Filter_XSS import parsehtml, parsehtmlAll
from LoadHtml import loadFile
from findType import filetype
from mysqlsec import keysearch

__author__ = 'wsdevotion'

def application(environ, start_response):
    r = redis.Redis(host='127.0.0.1', port=6379, db=1)
    method = environ['REQUEST_METHOD']
    path = environ['PATH_INFO']
    # body = environ['REQUEST_BODY']
    # print start_response
    # print environ
    #防止同一ip多次登录
    ip = environ['REMOTE_ADDR']
    num = r.get(ip)
    # print num
    if num:
        if int(num) < 3:
            num = str(int(num) + 1)
            r.setex(ip, num, 1)
        else:
            start_response('200 OK', [('Content-Type', 'text/html;charset=utf-8')])
            return '不要多次访问'
    else:
        r.setex(ip, '1', 1)

    #用户登录
    if method=='POST' and path=='/login':
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        except (ValueError):
            request_body_size = 0
        request_body = environ['wsgi.input'].read(request_body_size)

        #读取密码
        file = open('password.txt', 'r')
        password = file.readline()[:-1]
        salt = file.readline()
        m2 = hashlib.md5()
        m2.update(request_body)
        m = m2.hexdigest()
        file.close()

        #加密随机字符串和盐实现单点登录
        mes = uuid.uuid1()
        m2.update(str(mes) + salt)
        mes = m2.hexdigest()

        if m == password:
            r.setex('test', 'test123123', 360000)
            r.setex('password', mes, 360000)
            start_response('200 OK', [('Content-Type', 'text/html')])
            return mes
        elif password == '':
            start_response('200 OK', [('Content-Type', 'text/html')])
            return '请设置密码'
        else:
            start_response('200 OK', [('Content-Type', 'text/html')])
            return '密码错误'
    else:
        #判断用户是否登录
        s = r.get('test')
        if s!='test123123':
            start_response('200 OK', [('Content-Type', 'text/html;charset=utf-8')])
            return '请登录后使用'
    print path[:path.find('/', 1)]

    if method=='POST' and path=='/filterXSS':
        html = filterXSS(environ)
    elif method=='POST' and path=='/filterAll':
        html = filterAll(environ)
    elif method=='POST' and path=='/sendSQL':
        html = sendSQL(environ)
    elif method=='POST' and path[:path.find('/', 1)]=='/formSerach':
        file = path[path.find('/', 1):len(path)-2][1:]
        m = path[-1:]
        html = formSerach(environ, file, m)
    elif method=='POST' and path=='/sendFile':
        html = sendFile(environ)
    elif method=='GET' and path=='/':
        # html = '<div align="center"><h1>WELCOME</h1></div>'
        html = loadFile('index.html')
    elif method=='GET' and path=='/list':
        #加载安全工具
        html = loadFile('list.html')
    elif method=='GET' and path=='/list/1':
        #加载弱口令检测工具
        html = loadFile('list1.html')
    elif method=='POST' and path=='/list/1':
        request_body = getText(environ)
        d = parse_qs(request_body)
        try:
            psw = d.get('password')[0]
        except Exception:
            psw = ''
        message = keysearch(psw)
        #将信息放入html文件中展示
        html = loadFileD(environ, 'mes.html', message)
    elif method=='GET' and path=='/list/2':
        #ip获取工具
        html = loadFile('list2.html')
    elif method=='POST' and path=='/list/2':
        request_body = getText(environ)
        d = parse_qs(request_body)
        try:
            address = d.get('address')[0]
            ip = socket.gethostbyname(address)
            # address = "http://" + address
        except Exception:
            address = 'http://localhost'
            ip = ''

        #将信息放入html文件中展示
        html = loadFileD(environ, 'mes.html', "你要获取的ip:" + ip)
    elif method=='GET' and path=='/list/3':
        #MD5加密工具
        html = loadFile('list3.html')
    elif method=='POST' and path=='/list/3':
        request_body = getText(environ)
        d = parse_qs(request_body)
        try:
            message = d.get('message')[0]
            # address = "http://" + address
        except Exception:
            message = ''
        m2 = hashlib.md5()
        m2.update(message)
        m = m2.hexdigest()
        #将信息放入html文件中展示
        html = loadFileD(environ, 'mes.html', "你要获取的MD5:" + m)
    elif method=='GET' and path=='/':
        pass;
    elif method=='POST' and path=='/signin':
        print 123
    # print html


    try:
        start_response('200 OK', [('Content-Type', 'text/html;charset=utf-8')])
        return html
    except Exception:
        return 'Error'


        # return handle_signin(environ, start_response)
    # start_response('200 OK', [('Content-Type', 'text/html')])
    # return '<h1>Hello, %s!</h1>' % (environ['PATH_INFO'][1:] or 'web')

def filterXSS(environ):
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError):
        request_body_size = 0
    request_body = environ['wsgi.input'].read(request_body_size)
    # lenf = len(request_body)
    return parsehtml(request_body)

def filterAll(environ):
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError):
        request_body_size = 0
    request_body = environ['wsgi.input'].read(request_body_size)
    return parsehtmlAll(request_body)

def sendSQL(environ):
    request_body = getText(environ)
    if filter_SQL(request_body):
        r =requests.get(request_body)
        content = r.content
        return content
    return ''

def formSerach(environ, file, m):
    request_body = getText(environ)
    d = parse_qs(request_body)
    print d
    print file
    url = d.get('url')[0]
    file = open(file + '.txt', 'r')
    flag = True
    while 1:
        line = file.readline()
        line = line[0:line.find('\n')]
        r = line.split(':')
        value = d.get(r[0], [''])[0] # 返回第一个age的值
        if value != '':
            if not re.match(r[1], value):
                flag = False
                break

        if not line:
            break

    file.close()
    if flag == True:
        #如果选择2转换成json
        if m == '2':
            request_body = str(d).replace('[', '').replace(']', '')
            # print request_body
            # return request_body
        req = urllib2.urlopen(url, request_body)

        #获取提交后返回的信息
        content = req.read()
        return content
    else:
        return 'False'

def sendFile(environ):
    request_body = getText(environ)
    # print request_body
    # d = parse_qs(request_body)
    # print d
    # file = d.get('file')
    file = open("file1.jpg", 'wb')
    file.write(request_body)
    file.close()
    type = filetype('file1.jpg')
    return type

def getText(environ):
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError):
        request_body_size = 0
    request_body = environ['wsgi.input'].read(request_body_size)
    return request_body

def loadFileD(environ, name, mes):
    html = loadFile(name)
    html = html.replace("Example page header", mes)
    return html
