#coding=utf-8
from models import UserHomeLayout
import hashlib


if __name__ == "__main__":


    for i in xrange(679000,1000000):
        guid = hashlib.md5(str(i)).hexdigest()
        value = {"index":i}
        user_layout = UserHomeLayout(guid, value)
        user_layout.set()
        if i % 1000 == 0:
            print i


        
