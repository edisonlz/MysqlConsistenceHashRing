#coding=utf-8
from models import UserHomeLayout
import hashlib
import MySQLdb
from consistent import MysqlHashClient
import settings
import logging


class Rebalance(object):
    """
    Rebalance add or remove db
    """

    def __init__(self, new_config, old_config, table_name):
        self.old_config = old_config
        self.new_config = new_config
        self.table_name = table_name
        self.new_client = MysqlHashClient(self.new_config)
        self.old_client = MysqlHashClient(self.old_config)
        self.init_old_host(self.old_config)


    def init_old_host(self, hosts_config):
        self.old_mysql_list = []
        self.hosts = hosts_config.get("hosts")

        for h in self.hosts:
            conn = MySQLdb.connect(**h)
            self.old_mysql_list.append(conn)


    def run(self):
        for host in self.old_mysql_list:
            limit = 100
            offset = 0

            while True:
                sql = "select ikey,value from %s limit %s offset %s" % (self.table_name, limit, offset)
                logging.debug(sql)
                cursor = host.cursor()
                cursor.execute(sql)
                rows = cursor.fetchall()

                if not rows:
                    cursor.close()
                    break

                for row in rows or []:
                    guid = row[0]
                    value = row[1]

                    nc = self.new_client.get_client(guid)
                    oc = self.old_client.get_client(guid)
                    #print nc.__dict__
                    if nc.get_host_info() == oc.get_host_info():
                        pass
                    else:
                        print "move form %s to %s" % (oc.get_host_info(), nc.get_host_info()), guid, value
                        #key in old and new not same
                        self.move(guid, value)

                #next page 
                offset += limit


    def move(self, key, value):
        self.old_client.delete(key, table_name=self.table_name)
        self.new_client.set(key, value, table_name=self.table_name)


if __name__ == "__main__":
    logging.basicConfig(level="DEBUG")
    rb = Rebalance(settings.host_config, settings.old_host_config, settings.rebalance_db_table)
    rb.run()

