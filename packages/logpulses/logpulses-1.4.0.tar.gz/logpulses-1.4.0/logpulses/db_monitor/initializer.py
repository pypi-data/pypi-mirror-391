from logpulses.db_monitor.mongodb_monitor import MongoDBMonitor
from logpulses.db_monitor.mysql_monitor import MySQLMonitor
from logpulses.db_monitor.postgresql_monitor import PostgreSQLMonitor
from logpulses.db_monitor.sqlalchemy_monitor import SQLAlchemyMonitor
from logpulses.db_monitor.redis_monitor import RedisMonitor
from logpulses.db_monitor.cassandra_monitor import CassandraMonitor


def initialize_db_monitoring():
    """
    Initialize all database monitoring patches
    Call this once at application startup
    """
    print("\n" + "=" * 80)
    print("🔧 Initializing Database Monitoring...")
    print("=" * 80)

    MongoDBMonitor.patch_pymongo()
    MySQLMonitor.patch_mysql()
    PostgreSQLMonitor.patch_postgresql()
    SQLAlchemyMonitor.patch_sqlalchemy()
    RedisMonitor.patch_redis()
    CassandraMonitor.patch_cassandra()

    print("=" * 80)
    print("✅ Database Monitoring Initialization Complete!")
    print("=" * 80 + "\n")
