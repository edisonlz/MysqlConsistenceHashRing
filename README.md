MysqlConsistenceHashRing
========================

Consistence Hash Ring Mysql For Mysql , and it is client end implement, not proxy! why doesn't use proxy optimise connection number， because not want reduce performance, join it!



How to Use, you can also bind django models:

```
#coding=utf-8
from  consistent import MysqlHashClient
from settings import host_config
import time
import logging

class BaseLayout(object):
    #mysql consistence ring static class object
    client = MysqlHashClient(host_config)
    #mysql table name must extend
    TABLE_NAME = ""

    def __init__(self, guid, value):
        self.guid = guid
        self.value = value

    def set(self):
        return self.client.set(key=self.guid,\
                        value=self.value, table_name=self.TABLE_NAME)

    @classmethod
    def delete(cls, guid):
        return cls.client.delete(guid, table_name=cls.TABLE_NAME)


    @classmethod
    def get(cls, guid):
        return cls.client.get(guid, table_name=cls.TABLE_NAME)


class UserHomeLayout(BaseLayout):
    TABLE_NAME = "user_channel_layout"
    
    def __init__(self, guid, value):
        super(UserHomeLayout, self).__init__(guid, value)


if __name__ == "__main__":

    now = time.time()
    guid = "35aee8e85ffb518e70e44ee06bcc4479"
    value = [1, 2, 3, 4]
    user_layout = UserHomeLayout(guid, value)
    print "initial use:", time.time() - now

    now = time.time()
    user_layout.set()
    print "set use:", time.time() - now
    print "result:", UserHomeLayout.get(guid)

    now = time.time()
    value = [1, 2, 3, 6]
    user_layout = UserHomeLayout(guid, value)
    user_layout.set()
    print "set dup use:", time.time() - now

    now = time.time()
    print "result:", UserHomeLayout.get(guid)
    print "get use:", time.time() - now

    now = time.time()
    UserHomeLayout.delete(guid)
    print "del use:", time.time() - now

    now = time.time()
    print "result:", UserHomeLayout.get(guid)
    print "get use:", time.time() - now
```

Mysql DB Config use settings.py

```

host_config = {
        "hosts": [{
            'db': 'youku_mobile_user', # Or path to database file if using sqlite3.
            'user': 'root', # Not used with sqlite3.
            'passwd': '', # Not used with sqlite3.
            'host': 'localhost', # Set to sempty string for localhost. Not used with sqlite3.
            'port': 3306, # Set to empty string for default. Not used with sqlite3.
            'init_command': 'SET storage_engine=INNODB;set SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED; set autocommit=0;set  names "utf8";'
        }]
    }
```


Add or Remove Server , Rebalance python script!
```
#config use settings
python rebalance.py
```


```
Test for 2 nodes


mysql one> select count(*) from user_home_layout;
+----------+
| count(*) |
+----------+
|     5283 |


mysql two> select count(*) from user_home_layout;
+----------+
| count(*) |
+----------+
|     4717 |
+----------+

```


```
Test for add one node , now 3 nodes
> python rebalance.py


New node mysql> select count(*) from user_home_layout;
+----------+
| count(*) |
+----------+
|     3479 |
+----------+

mysql one> select count(*) from user_home_layout;
+----------+
| count(*) |
+----------+
|     3322 |
+----------+

mysql two> select count(*) from user_home_layout;
+----------+
| count(*) |
+----------+
|     3199 |
+----------+

```


```
so ...
>>> 3322 + 3199 + 3479
10000
```