#coding:utf8
from Filter_XSS import parsehtml

__author__ = 'wsdevotion'

if __name__ == '__main__':
    text = '''
     <h1 style="font-size:expression(alert('XSS'))">Hello!</h1>
     <img src='http://0.0.0.0:8080/static/test/jpg' alt='我是一副正常的图片' onerror='alert("你才不正常呢！你全家都不正常")'/>
     <a href='javascript:alert(1);'>Hello</a>
     <a href='http://www.baidu.com'<script>alert(1);</script>' title='sddasdsadsd'/>
    '''
    print parsehtml(text)