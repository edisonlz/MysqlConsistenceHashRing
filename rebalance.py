#coding=utf-8
from models import UserHomeLayout
import hashlib

import os,sys
PROJECT_ROOT = os.path.realpath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(PROJECT_ROOT, os.pardir))

import MySQLdb
from consistent import MysqlHashClient
from  MysqlConsistenceHashRing import settings
import logging
from multiprocessing import Pool
import copy


class Rebalance(object):
    """
    Rebalance add or remove db
    """

    def __init__(self, new_config, old_config, table_name):
        self.old_config = old_config
        self.new_config = new_config
        self.table_name = table_name
        self.new_client = MysqlHashClient(copy.deepcopy(new_config))
        self.old_client = MysqlHashClient(copy.deepcopy(old_config))
        self.init_old_host(copy.deepcopy(old_config))


    def init_old_host(self, hosts_config):
        self.old_mysql_list = []
        self.i_old_mysql_list = []
        self.hosts = hosts_config.get("hosts")
        self.pool = Pool(len(self.hosts))
        i = 0
        print "###### rabalance load ######"
        for h in self.hosts:
            for p in h.pop("partitions", [""]):
                conn = MySQLdb.connect(**h)
                print "%s:%s:%s" % (h["host"], h["port"], p)
                self.old_mysql_list.append({"conn": conn, "partition_id": p})
                self.i_old_mysql_list.append(i)
                i += 1
        print "###### end rabalance load ######"


    def run_work(self):
        print  self.i_old_mysql_list
        self.pool.map(self.run, self.i_old_mysql_list)

    
    def gen_table_name(self, p, table_name=""):
        if not table_name:
            raise Exception("table name must set!")

        table_name = "%s_p%s" % (table_name, p)
        return table_name


    def run(self):
        for host_config in self.old_mysql_list:

            host = host_config.get("conn")
            partition_id = host_config.get("partition_id")

            print host.get_host_info()
            limit = 100
            offset = 0

            while True:
                table_name = self.gen_table_name(partition_id, self.table_name)
                sql = "select ikey,value from %s limit %s offset %s" % (table_name, limit, offset)
                logging.info(sql)
                cursor = host.cursor()
                cursor.execute(sql)
                rows = cursor.fetchall()

                if not rows:
                    cursor.close()
                    print "* " * 20
                    break

                move_count = 0
                for row in rows or []:
                    guid = row[0]
                    value = row[1]

                    nc = self.new_client.get_client(guid)
                    oc = self.old_client.get_client(guid)

                    np = self.new_client.get_partition_id(guid)
                    op = self.old_client.get_partition_id(guid)
                    #print nc.__dict__
                    if nc.get_host_info() == oc.get_host_info() and np == op:
                        pass
                    else:
                        print "move form %s:%s to %s:%s" % (oc.get_host_info(), np, nc.get_host_info(), op), guid, value
                        #key in old and new not same
                        self.move(guid, value)
                        move_count += 1

                #next page
                offset += limit - move_count


    def move(self, key, value):
        self.old_client.delete(key, table_name=self.table_name)
        self.new_client.set(key, value, table_name=self.table_name)


if __name__ == "__main__":
    logging.basicConfig(level="INFO")

    rb = Rebalance(settings.host_config, settings.old_host_config, settings.rebalance_db_table)
    rb.run()
    
#    nc = rb.new_client.get_client("bdbb8cb597f1299d252389ea69c0a436")
#    oc = rb.old_client.get_client("bdbb8cb597f1299d252389ea69c0a436")
#    print nc.get_host_info(),oc.get_host_info()