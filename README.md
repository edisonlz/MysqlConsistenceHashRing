MysqlConsistenceHashRing
========================

Consistence Hash Ring Mysql For Mysql
[code]

How to Use:

class UserChannelLayout(BaseLayout):
    TABLE_NAME = "user_channel_layout"
    
    def __init__(self, guid, value):
        super(UserChannelLayout, self).__init__(guid, value)


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
[/code]
