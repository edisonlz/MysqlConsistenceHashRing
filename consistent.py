#coding=utf-8

#
# you are right in this statement
# http://www.tokutek.com/2010/07/why-insert-on-duplicate-key-update-may-be-slow-by-incurring-disk-seeks/
#

import bisect
import hashlib
import MySQLdb
import time
import logging
import json


class ConsistentHashRing(object):
    """Implement a consistent hashing ring."""

    def __init__(self, replicas=160):
        """Create a new ConsistentHashRing.

        :param replicas: number of replicas.

        """
        self.replicas = replicas
        self._keys = []
        self._nodes = {}


    def _hash(self, key):
        """Given a string key, return a hash value."""

        return long(hashlib.md5(key).hexdigest(), 16)

    def _repl_iterator(self, nodename):
        """Given a node name, return an iterable of replica hashes."""

        return (self._hash("%s:%s" % (nodename, i))
        for i in xrange(self.replicas))


    def __setitem__(self, nodename, node):
        """Add a node, given its name.
            The given nodename is hashed
            among the number of replicas.
        """

        for hash_ in self._repl_iterator(nodename):
            if hash_ in self._nodes:
                raise ValueError("Node name %r is "
                                 "already present" % nodename)
            self._nodes[hash_] = node
            bisect.insort(self._keys, hash_)


    def __delitem__(self, nodename):
        """Remove a node, given its name."""

        for hash_ in self._repl_iterator(nodename):
            # will raise KeyError for nonexistent node name
            del self._nodes[hash_]
            index = bisect.bisect_left(self._keys, hash_)
            del self._keys[index]

    def __getitem__(self, key):
        """Return a node, given a key.

        The node replica with a hash value nearest
        but not less than that of the given
        name is returned.   If the hash of the
        given name is greater than the greatest
        hash, returns the lowest hashed node.

        """
        hash_ = self._hash(key)
        start = bisect.bisect(self._keys, hash_)
        if start == len(self._keys):
            start = 0
        return self._nodes[self._keys[start]]


class MysqlHashClient(object):
    """
        Consistent Hash Redis Client
    """


    def __init__(self, hosts_config):
        self.consistent_ring = ConsistentHashRing()
        self.mysql_list = []
        self.hosts = hosts_config.get("hosts")

        for h in self.hosts:
            nodename = "%s:%s" % (h["host"], h["port"])
            conn = MySQLdb.connect(**h)
            self.mysql_list.append(conn)
            self.consistent_ring[nodename] = conn


    def get_client(self, key):
        client = self.consistent_ring[key]
        return client


    def delete(self, key, table_name=""):
        if not table_name:
            raise Exception("table name must set!")

        client = self.consistent_ring[key]
        try:
            cursor = client.cursor()
            sql = "delete from %s where ikey='%s'" % (table_name, key)
            n = cursor.execute(sql)
            logging.debug(sql)
            client.commit()
            cursor.close()
            return n
        except Exception, e:
            logging.error(e)


    def set(self, key, value, table_name=""):
        if not table_name:
            raise Exception("table name must set!")

        client = self.consistent_ring[key]
        #print "set client into", client.get_host_info(),key
        try:
            value = json.dumps(value)
            cursor = client.cursor()
            #            sql = "insert into %s(ikey,value) VALUES('%s','%s') \
            #                 ON DUPLICATE KEY UPDATE value='%s'" % (table_name, key, value, value)
            #why use replace into look this file head
            sql = "replace into %s(ikey,value) VALUES('%s','%s')" % (table_name, key, value)
            logging.debug(sql)
            n = cursor.execute(sql)
            cursor.close()
            client.commit()
            return n
        except Exception, e:
            logging.error(e)
            client.rollback()
            return None

    def get(self, key, table_name=""):
        if not table_name:
            raise Exception("table name must set!")

        client = self.consistent_ring[key]
        try:
            cursor = client.cursor()
            sql = "select value from %s where ikey='%s'" % (table_name, key)
            logging.debug(sql)
            cursor.execute(sql)
            data = cursor.fetchone()
            if data:
                data = json.loads(data[0])
                return data
            cursor.close()
        except Exception, e:
            logging.error(e)
            return None


if __name__ == "__main__":
    from settings import host_config

    now = time.time()
    myclient = MysqlHashClient(host_config)
    print "initial use:", time.time() - now

    key = "35aee8e85ffb518e70e44ee06bcc4479"
    value = [1, 2, 3, 4]

    now = time.time()
    myclient.set(key, value, table_name="user_home_layout")
    print "set use:", time.time() - now
    print "result:", myclient.get(key, table_name="user_home_layout")

    now = time.time()
    value = [1, 2, 3, 6]
    myclient.set(key, value, table_name="user_home_layout")
    print "set dup use:", time.time() - now

    now = time.time()
    print "result:", myclient.get(key, table_name="user_home_layout")
    print "get use:", time.time() - now

    now = time.time()
    myclient.delete(key, table_name="user_home_layout")
    print "del use:", time.time() - now

    now = time.time()
    print "result:", myclient.get(key, table_name="user_home_layout")
    print "get use:", time.time() - now
    



    


    