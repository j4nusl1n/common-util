import os
import yaml
import pymysql
import pymysql.cursors

__all__ = [
    'Query',
    'MySQLQuery',
    'factory_query'
]

__ROOTDIR = "/".join(os.path.abspath(__file__).split("/")[:-2])
__PACKAGE_DIR = "{}/db".format(__ROOTDIR)

class ConnectConfig(object):
    """Generate config for connecting to different database servers.\n
    This class will try to look for configuration YAML file using environ DB_CONFIG_FILE if config_path is None

    Arguments:
        db_sys {str} -- A string indicating which database system is connected to.
        host {str} -- A string indicating which database server is connected to.

    Keyword Arguments:
        config_path {str} -- Use configuration file in different path (default: {None})

    Raises:
        ValueError: Raised if argument is invalid
    """
    __config = None
    __default_config_path = '{}/config/db.yml'.format(globals()['__PACKAGE_DIR'])
    def __init__(self, db_sys, host, config_path=None):
        if config_path is None:
            config_path = self.__default_config_path
            if os.environ.get('DB_CONFIG_FILE'):
                config_path = os.environ.get('DB_CONFIG_FILE')

        with open(config_path, 'r') as f:
            self.__full_config = yaml.full_load(f)

        if db_sys not in self.__full_config:
            raise ValueError('invalid database system')

        conn_config = self.__full_config[db_sys]
        if host not in conn_config:
            raise ValueError('invalid host')

        self.__config = conn_config[host]
    
    @classmethod
    def mysql_config(cls, host):
        """Read MySQL configs to specific host environment

        Args:
            host (str): Host environment name

        Returns:
            ConnectConfig: ConnectConfig object
        """
        obj = cls('MySQL', host)
        return obj

    @classmethod
    def mysql_connect_info(cls, host):
        """Get MySQL connection required info to specific host environment

        Args:
            host (str): Host environment name

        Returns:
            tuple: A tuple consists of (host, user, pwd)
        """    
        return cls('MySQL', host).get_connect_info()

    def get_connect_info(self):
        """This method will return configs for connection

        Returns:
            tuple(str, str, str) -- 
            >>> A tuple of connection config in (host, user, password) form
        """        
        conn_config = self.__config
        connect_info = (conn_config['host'], conn_config['user'], conn_config['password'])
        return connect_info

    def get(self, key, default=None):
        return self.__config.get(key, default)

class DBConnect(object):
    def __del__(self):
        self.close()

    def connect(self):
        raise NotImplementedError
    
    def close(self):
        raise NotImplementedError

class MySQLDBConnect(DBConnect):
    """Connect to MySQL database of specific host environment

    Args:
        hostname (str, optional): Host environment name. Defaults to None.

    Raises:
        TypeError: Raised if `hostname` is not str
    """
    def __init__(self, hostname=None):
        if hostname is None:
            hostname = 'default'
        elif not isinstance(hostname, str):
            raise TypeError('argument "hostname" should be a str')

        self.config = ConnectConfig.mysql_config(hostname)

    @classmethod
    def productionConnect(cls):
        """Factory method to create connection to production environment

        Returns:
            MySQLDBConnect: Connection object
        """
        return cls(hostname='production')
    
    @classmethod
    def developmentConnect(cls):
        """Factory method to create connection to development environment

        Returns:
            MySQLDBConnect: Connection object
        """
        return cls(hostname='development')

    def connect(self, cursor_class=None):
        if cursor_class is None:
            cursor_class = pymysql.cursors.Cursor

        host, user, password = self.config.get_connect_info()
        self.connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            cursorclass=cursor_class
        )

        self.cursor = self.connection.cursor()

    def close(self):
        if hasattr(self, 'connection'):
            if isinstance(self.connection, pymysql.connections.Connection):
                if self.connection.open:
                    self.connection.close()

class Query(object):
    def __del__(self):
        raise NotImplementedError

    def query(self):
        raise NotImplementedError

class MySQLQuery(Query):
    def __init__(self, hostname: str, dict_cursor: bool=False):
        """MySQL query wrapper class

        Args:
            hostname (str): Host environment name of the database defined in db.yml
            dict_cursor (bool, optional): If set to True, this will return dict for each row of query result. Defaults to False.
        """
        factory_methods = [
            'production',
            'development',
        ]

        if dict_cursor is True:
            cursorclass = pymysql.cursors.DictCursor
        else:
            cursorclass = None

        if hostname in factory_methods:
            self.db_connect = getattr(MySQLDBConnect, '{}Connect'.format(hostname))()
        else:
            self.db_connect = MySQLDBConnect(hostname=hostname)

        self.db_connect.connect(cursor_class=cursorclass)
    
    def __del__(self):
        try:
            self.db_connect.close()
        except:
            pass

    def is_connection_open(self) -> bool:
        """Check whether the connection is open

        Returns:
            bool: True if connection is open. Otherwise, return False
        """
        return self.db_connect.connection.open

    def reconnect(self):
        """Reconnect to database
        """
        self.db_connect.connection.ping(reconnect=True)

    def query(self, sql: str, is_dml: bool=False, args: tuple=None) -> list:
        """Send SQL query to database. Returns query result if is selection.

        Args:
            sql (str): SQL query string
            is_dml (bool, optional): Set True if the query string is a data manipulation language (INSERT, UPDATE, DELETE). Defaults to False.
            args (tuple, optional): Query parameters to escape. Defaults to None.

        Raises:
            e: Raised if querying failed. This will do a rollback if {is_dml} is True.

        Returns:
            list: Query results
        """
        is_dml = (is_dml is True)
        if args is None:
            args = tuple()

        if not self.is_connection_open():
            self.reconnect()
        
        try:
            if is_dml:
                self.db_connect.connection.begin()
            
            result = self.db_connect.cursor.execute(sql, args)

            if is_dml:
                self.db_connect.connection.commit()

        except Exception as e:
            if is_dml:
                self.db_connect.connection.rollback()
            
            raise e

        if is_dml:
            return result
        else:
            return self.db_connect.cursor.fetchall()

def factory_query(query_type: str, *args, **kwarg) -> Query:
    """Factory function for creating Query instance

    Args:
        query_type (str): Type of the Query class

    Raises:
        ValueError: Raised if {query_type} is invalid

    Returns:
        Query: Query instance
    """
    type_mapping = {
        'MySQL': MySQLQuery
    }

    if query_type in type_mapping:
        return type_mapping[query_type](*args, **kwarg)
    else:
        raise ValueError('Argument "query_type" not supported')
