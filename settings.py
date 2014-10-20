#coding=utf-8


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