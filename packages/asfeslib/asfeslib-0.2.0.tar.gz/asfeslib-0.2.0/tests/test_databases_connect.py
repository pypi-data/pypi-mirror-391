import pytest
from asfeslib.databases.MongoDB import MongoConnectScheme
from asfeslib.databases.PostgreSQL import PostgresConnectScheme
from asfeslib.databases.MySQL import MariaConnectScheme


def test_mongo_url_build():
    cfg = MongoConnectScheme(host="127.0.0.1", db_name="testdb")
    assert "mongodb://" in cfg.assemble_url()


def test_postgres_url_build():
    cfg = PostgresConnectScheme(username="user", password="pass", host="db.local")
    url = cfg.assemble_url()
    assert url.startswith("postgresql://user:pass@db.local")


def test_mariadb_url_build():
    cfg = MariaConnectScheme(username="root", password="1234", host="db.local")
    url = cfg.assemble_url()
    assert "mysql://" in url
