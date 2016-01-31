#coding:utf8
import hashlib

def md5Message(mes, salt):
    m2 = hashlib.md5()
    m2.update(mes)
    m = m2.hexdigest()
    file = open('password.txt', 'w')
    # file.write(m)
    file.writelines(m + "\n")
    file.writelines(salt)
    file.close()


if __name__ == '__main__':
    mes = raw_input("请输入密码:")
    salt = raw_input("请输入MD5哈希Salt:")
    md5Message(mes, salt)
    print 'success'