#coding:utf8


__author__ = 'wsdevotion'




def keysearch(psw):
    passwords = []
    f = open("psw.txt", "r")
    while True:
        line = f.readline()
        if line:
            passwords.append(line[:-3])
        else:
            f.close()
            break


    if psw in passwords:

        return "你的密码不安全，请更改密码"


    return "你的密码安全"

