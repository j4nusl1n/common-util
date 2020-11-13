import os
import sys
import unittest

import pytest

from ..datacommon import db

class Test_MySQL(unittest.TestCase):
    def setUp(self):
        pass
    
    @pytest.mark.development
    def test_dev_connect(self):
        conn = db.MySQLDBConnect.developmentConnect()
        configs = conn.config.get_connect_info()
        self.assertEqual(configs[1], 'janus')
        conn.connect()
        conn.close()
    
    @pytest.mark.production
    def test_prod_connect(self):
        conn = db.MySQLDBConnect.productionConnect()
        configs = conn.config.get_connect_info()
        self.assertEqual(configs[1], "tripresso")
        conn.connect()
        conn.close()

    @pytest.mark.development
    def test_dev_query(self):
        query = db.MySQLQuery('development')
        self.assertTrue(query.is_connection_open())

    @pytest.mark.production
    def test_prod_query(self):
        query = db.MySQLQuery('production')
        self.assertTrue(query.is_connection_open())

    def test_factory_method(self):
        query = db.factory_query('MySQL', 'development')
        self.assertIsInstance(query, (db.MySQLQuery,))

if __name__ == "__main__":
    unittest.main(verbosity=2)
