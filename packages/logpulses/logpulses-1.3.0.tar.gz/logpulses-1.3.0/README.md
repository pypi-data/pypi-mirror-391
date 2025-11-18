# FastAPI Request Logger with Storage

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![PyPI](https://img.shields.io/pypi/v/logpulses)](https://pypi.org/project/logpulses/)

A comprehensive, production-ready logging middleware for FastAPI applications that provides detailed insights into every request and response with **zero configuration** and **multiple storage options**.

## ✨ Features

- 🚀 **Zero Configuration** - Just add one line of middleware
- 💾 **Multiple Storage Options** - Local files, MongoDB, MySQL, PostgreSQL, SQLite
- 🧹 **Automatic Cleanup** - Delete old logs based on retention days
- 📊 **Comprehensive Logging** - Captures everything:
  - Request details (method, route, headers, body, query params)
  - Response details (status, body, size)
  - Performance metrics (execution time, memory usage)
  - Database operations (queries, connections, execution time)
  - System metrics (CPU, memory)
  - Network information (interface type - WiFi/Ethernet, IP, traffic)
- 🔄 **Works with All Request Types** - GET, POST, PUT, PATCH, DELETE
- 🗃️ **Database Operation Tracking** - Automatically monitors:
  - MongoDB operations (find, insert, update, delete)
  - MySQL queries (SELECT, INSERT, UPDATE, DELETE)
  - PostgreSQL queries
  - Redis commands
  - SQLAlchemy operations
- 💪 **No Body Consumption Issues** - Routes can freely use `request.json()` and `request.body()`
- 🎯 **Smart Network Detection** - Automatically identifies WiFi vs Ethernet
- 📝 **Beautiful JSON Output** - Pretty-printed, structured logs
- ⚡ **High Performance** - Minimal overhead using ASGI-level interception
- 🛡️ **Production Ready** - Error handling and edge case coverage

## 📦 Installation

### Basic Installation

```bash
pip install logpulses
```

### With Database Storage Support

```bash
# For MongoDB storage
pip install logpulses pymongo

# For MySQL storage
pip install logpulses mysql-connector-python

# For PostgreSQL storage
pip install logpulses psycopg2-binary

# For automatic log cleanup (recommended)
pip install logpulses schedule

# Install all at once
pip install logpulses pymongo mysql-connector-python psycopg2-binary schedule
```

Or install from source:

```bash
git clone https://github.com/Hari-vasan/logpulses.git
cd logpulses
pip install -e .
```

## 🚀 Quick Start

### 1. Console Logging Only (Default)

```python
from fastapi import FastAPI
from logpulses.logger import RequestLoggingMiddleware

app = FastAPI()

# Enable comprehensive logging (console output)
app.add_middleware(RequestLoggingMiddleware, enable_db_monitoring=True)

@app.get("/users")
async def get_users():
    return {"users": [...]}
```

### 2. Local File Storage

```python
from fastapi import FastAPI
from logpulses.logger import RequestLoggingMiddleware

app = FastAPI()

# Store logs in local files with automatic cleanup
app.add_middleware(
    RequestLoggingMiddleware,
    storage_type='local',           # Store in local files
    log_dir='logs',                 # Directory for log files
    cleanup_days=7,                 # Delete logs older than 7 days
    print_logs=True,                # Also print to console
    enable_db_monitoring=True
)

@app.get("/users")
async def get_users():
    return {"users": [...]}
```

**Result**: Creates daily log files like `logs/logs_2025-11-04.jsonl`

### 3. MongoDB Storage

```python
app.add_middleware(
    RequestLoggingMiddleware,
    storage_type='mongodb',
    connection_string='mongodb://localhost:27017',
    database_name='logs_db',        # Database name
    collection_name='logs',         # Collection name
    cleanup_days=30,                # Keep logs for 30 days
    print_logs=True,
    enable_db_monitoring=True
)
```

### 4. MySQL Storage

```python
app.add_middleware(
    RequestLoggingMiddleware,
    storage_type='mysql',
    connection_string='mysql://user:password@localhost:3306/logs_db',
    table_name='logs',              # Table name
    cleanup_days=7,
    print_logs=True,
    enable_db_monitoring=True
)
```

### 5. PostgreSQL Storage

```python
app.add_middleware(
    RequestLoggingMiddleware,
    storage_type='postgresql',
    connection_string='postgresql://user:password@localhost:5432/logs_db',
    table_name='logs',
    cleanup_days=14,
    print_logs=True,
    enable_db_monitoring=True
)
```

### 6. SQLite Storage (Simple & Local)

```python
app.add_middleware(
    RequestLoggingMiddleware,
    storage_type='sqlite',
    db_path='logs.db',              # SQLite database file
    table_name='logs',
    cleanup_days=7,
    print_logs=True,
    enable_db_monitoring=True
)
```

## 🔧 Configuration Options

### Common Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `storage_type` | str | `None` | Storage type: `'local'`, `'mongodb'`, `'mysql'`, `'postgresql'`, `'sqlite'` |
| `connection_string` | str | `None` | Database connection string |
| `cleanup_days` | int | `7` | Days to retain logs |
| `print_logs` | bool | `True` | Print logs to console |
| `exclude_paths` | list | `[]` | Paths to exclude from logging |
| `enable_db_monitoring` | bool | `True` | Monitor database operations |

### Storage-Specific Parameters

**Local File Storage:**
- `log_dir` (str): Directory for log files (default: `'logs'`)

**MongoDB:**
- `database_name` (str): Database name (default: `'logs_db'`)
- `collection_name` (str): Collection name (default: `'logs'`)

**MySQL/PostgreSQL/SQLite:**
- `table_name` (str): Table name (default: `'logs'`)

**SQLite:**
- `db_path` (str): Path to SQLite database file (default: `'logs.db'`)

## 📊 Complete Example with Database Operations

```python
from fastapi import FastAPI
from logpulses.logger import RequestLoggingMiddleware
import mysql.connector
from pymongo import MongoClient

app = FastAPI()

# Configure with MongoDB storage
app.add_middleware(
    RequestLoggingMiddleware,
    storage_type='mongodb',
    connection_string='mongodb://localhost:27017',
    database_name='logs_db',
    cleanup_days=30,
    enable_db_monitoring=True
)

# MongoDB setup
mongo_client = MongoClient("mongodb://localhost:27017/")
users_collection = mongo_client.testdb.users

# MySQL setup
def get_mysql_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="testing"
    )

@app.get("/mysql/users")
async def get_mysql_users():
    """MySQL SELECT - Automatically tracked"""
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM test")
        results = cursor.fetchall()
        return {"test": results, "count": len(results)}
    finally:
        cursor.close()
        conn.close()

@app.post("/mysql/users")
async def create_mysql_user(name: str, employee_id: str):
    """MySQL INSERT - Automatically tracked"""
    conn = get_mysql_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO test (name, empolyeid) VALUES (%s, %s)", 
            (name, employee_id)
        )
        conn.commit()
        return {
            "message": "User created", 
            "id": cursor.lastrowid, 
            "rows_affected": cursor.rowcount
        }
    finally:
        cursor.close()
        conn.close()

@app.get("/mongo/users")
async def get_mongo_users():
    """MongoDB find - Automatically tracked"""
    users = list(users_collection.find())
    # Convert ObjectId to string for JSON serialization
    for user in users:
        user["_id"] = str(user["_id"])
    return {"users": users, "count": len(users)}

@app.post("/mongo/users")
async def create_mongo_user(name: str, age: int):
    """MongoDB insert - Automatically tracked"""
    document = {"name": name, "age": age}
    result = users_collection.insert_one(document)
    document["_id"] = str(result.inserted_id)
    return {"message": "User created", "document": document}

@app.get("/mixed-query")
async def mixed_database_query():
    """Query both MySQL and MongoDB - Both tracked"""
    # MySQL count
    conn = get_mysql_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM test")
    mysql_count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    
    # MongoDB count
    mongo_count = users_collection.count_documents({})
    
    return {
        "mysql_users": mysql_count,
        "mongo_users": mongo_count,
        "total": mysql_count + mongo_count
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 📋 Log Output Example

```json
{
  "timestamp": "2025-11-04 11:31:55",
  "request": {
    "route": "/mysql/users",
    "method": "GET",
    "fullUrl": "http://localhost:8000/mysql/users",
    "clientIp": "127.0.0.1",
    "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "size": "0 bytes",
    "body": "No query parameters"
  },
  "response": {
    "status": 200,
    "success": true,
    "size": "204 bytes",
    "body": {
      "test": [
        {
          "id": 1,
          "name": "hari",
          "empolyeid": "123",
          "position": "developer"
        }
      ],
      "count": 3
    }
  },
  "performance": {
    "processingTime": "167.09 ms",
    "memoryUsed": "18.79 KB"
  },
  "system": {
    "cpuUsage": "5.7%",
    "memoryUsage": {
      "total": "15.73 GB",
      "used": "11.43 GB",
      "available": "4.30 GB",
      "percent": "72.7%"
    }
  },
  "network": {
    "interface": "Wi-Fi",
    "type": "WiFi",
    "ip": "172.168.15.27",
    "netmask": "255.255.248.0",
    "isActive": true,
    "bytesSent": "129.19 MB",
    "bytesRecv": "1104.35 MB"
  },
  "server": {
    "instanceId": "00000000-0000-0000-0000-8469935957e0",
    "platform": "Windows",
    "hostname": "HARIHARAN-PEN349"
  },
  "database": {
    "totalOperations": 1,
    "totalDuration": "126.45 ms",
    "totalConnectionTime": "126.45 ms",
    "databaseTypes": ["MySQL"],
    "operationsByType": {
      "MySQL": {
        "count": 1,
        "totalDuration": "126.45 ms",
        "operations": [
          {
            "type": "MySQL",
            "operation": "connect",
            "duration_ms": "126.45",
            "timestamp": "2025-11-04T11:31:55.904996",
            "status": "success",
            "connection_time_ms": "126.45",
            "metadata": {
              "host": "localhost",
              "database": "testing"
            }
          }
        ]
      }
    },
    "failedOperations": 0,
    "percentageOfRequestTime": "75.7%"
  }
}
```

## 🗃️ Database Storage Schema

### SQL Databases (MySQL, PostgreSQL, SQLite)

```sql
CREATE TABLE logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    route VARCHAR(500),
    method VARCHAR(10),
    status_code INT,
    processing_time_ms FLOAT,
    log_data JSON,              -- Stores complete log as JSON
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_created_at (created_at),
    INDEX idx_route (route),
    INDEX idx_status (status_code)
);
```

### MongoDB

```javascript
{
  _id: ObjectId,
  timestamp: "2025-11-04 11:31:55",
  request: { ... },
  response: { ... },
  performance: { ... },
  database: { ... },
  system: { ... },
  network: { ... },
  server: { ... },
  created_at: ISODate("2025-11-04T11:31:55.000Z")
}
```

**TTL Index**: Automatically created to delete documents after `cleanup_days`

## 🧹 Automatic Log Cleanup

LogPulses automatically cleans up old logs based on the `cleanup_days` parameter:

- **Background Scheduler**: Runs cleanup daily at 2:00 AM
- **Retention Period**: Configurable via `cleanup_days` parameter
- **Safe Deletion**: Only deletes logs older than specified days

### Cleanup Behavior by Storage Type

**Local Files**: Deletes log files based on filename date
```
logs_2025-10-28.jsonl  ← Deleted if older than cleanup_days
logs_2025-11-03.jsonl  ← Kept
logs_2025-11-04.jsonl  ← Kept (today)
```

**MongoDB**: Uses TTL index for automatic deletion (no manual intervention needed)

**MySQL/PostgreSQL/SQLite**: Scheduled DELETE queries remove old records
```sql
DELETE FROM logs WHERE created_at < (NOW() - INTERVAL 7 DAY);
```

### Manual Cleanup

```python
from logpulses.log_storage import create_log_storage

# Create storage instance
storage = create_log_storage('local', cleanup_days=7)

# Manually trigger cleanup
deleted_count = storage.cleanup_old_logs(days=7)
print(f"Deleted {deleted_count} old logs")

# Close storage
storage.close()
```

## 🎭 Production Examples

### High-Traffic API (PostgreSQL)

```python
app.add_middleware(
    RequestLoggingMiddleware,
    storage_type='postgresql',
    connection_string='postgresql://user:pass@postgres:5432/logs_db',
    cleanup_days=90,              # Compliance requirement
    print_logs=False,             # Silent in production
    exclude_paths=['/health', '/metrics'],  # Skip monitoring endpoints
    enable_db_monitoring=True
)
```

### Development Setup (Local Files + Console)

```python
app.add_middleware(
    RequestLoggingMiddleware,
    storage_type='local',
    log_dir='dev_logs',
    cleanup_days=3,               # Short retention in dev
    print_logs=True,              # Verbose logging
    enable_db_monitoring=True
)
```

### Microservices (MongoDB with Service Name)

```python
SERVICE_NAME = "user-service"

app.add_middleware(
    RequestLoggingMiddleware,
    storage_type='mongodb',
    connection_string='mongodb://mongo:27017',
    database_name='microservices_logs',
    collection_name=f'logs_{SERVICE_NAME}',
    cleanup_days=30,
    enable_db_monitoring=True
)
```

### Embedded Systems (SQLite)

```python
app.add_middleware(
    RequestLoggingMiddleware,
    storage_type='sqlite',
    db_path='/data/logs.db',
    cleanup_days=7,               # Limited storage
    print_logs=False,
    enable_db_monitoring=True
)
```

## 🔐 Connection String Formats

### MongoDB
```
mongodb://localhost:27017
mongodb://user:password@localhost:27017
mongodb://user:password@host1:27017,host2:27017/?replicaSet=mySet
```

### MySQL
```
mysql://user:password@localhost:3306/database
mysql://root:password@127.0.0.1:3306/logs_db
```

### PostgreSQL
```
postgresql://user:password@localhost:5432/database
postgresql://postgres:password@db.example.com:5432/logs_db
```

## 🔍 Querying Stored Logs

### MongoDB

```python
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017')
db = client['logs_db']

# Find all errors
errors = db.logs.find({'response.status': {'$gte': 400}})

# Find slow requests (> 1 second)
slow_requests = db.logs.find({
    'performance.processingTime': {'$regex': '^[1-9][0-9]{3,}'}
})

# Count requests by route
pipeline = [
    {'$group': {'_id': '$request.route', 'count': {'$sum': 1}}},
    {'$sort': {'count': -1}}
]
stats = db.logs.aggregate(pipeline)
```

### MySQL/PostgreSQL

```python
import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='user',
    password='pass',
    database='logs_db'
)
cursor = conn.cursor()

# Find all errors
cursor.execute("SELECT * FROM logs WHERE status_code >= 400")
errors = cursor.fetchall()

# Find slow requests
cursor.execute("SELECT * FROM logs WHERE processing_time_ms > 1000")
slow_requests = cursor.fetchall()

# Average processing time by route
cursor.execute("""
    SELECT route, AVG(processing_time_ms) as avg_time, COUNT(*) as count
    FROM logs
    GROUP BY route
    ORDER BY avg_time DESC
""")
stats = cursor.fetchall()
```

## 📈 Performance Considerations

| Storage Type | Best For | Pros | Cons |
|--------------|----------|------|------|
| **Local Files** | Development, Small Apps | Fast, Simple, No dependencies | Limited querying, Manual analysis |
| **MongoDB** | High-write workloads | Flexible schema, Fast writes, TTL index | Requires MongoDB instance |
| **MySQL** | Structured data needs | ACID transactions, Complex queries | Schema-based, Slower writes |
| **PostgreSQL** | Analytics, Compliance | JSONB support, Advanced queries | Schema-based, Resource intensive |
| **SQLite** | Single-instance apps | Zero config, Embedded | Single writer, Not for high concurrency |

## 🛠️ Advanced Configuration

### Exclude Specific Paths

```python
app.add_middleware(
    RequestLoggingMiddleware,
    exclude_paths=[
        '/health',
        '/metrics',
        '/favicon.ico',
        '/docs',
        '/redoc'
    ],
    storage_type='local',
    cleanup_days=7
)
```

### Storage Only (No Console Output)

```python
app.add_middleware(
    RequestLoggingMiddleware,
    storage_type='mongodb',
    connection_string='mongodb://localhost:27017',
    print_logs=False,           # Silent mode
    cleanup_days=30
)
```

### Custom Log Directory

```python
app.add_middleware(
    RequestLoggingMiddleware,
    storage_type='local',
    log_dir='/var/log/myapp',  # Custom directory
    cleanup_days=7
)
```

## 🐛 Troubleshooting

### "Failed to initialize log storage"

**Solution**: Install required database packages
```bash
pip install pymongo           # For MongoDB
pip install mysql-connector-python  # For MySQL
pip install psycopg2-binary  # For PostgreSQL
pip install schedule         # For automatic cleanup
```

### Logs not cleaning up automatically

**Solution**: Ensure `schedule` package is installed and the application runs continuously
```bash
pip install schedule
```

### Connection refused errors

**Solution**: Verify database server is running and connection string is correct
```bash
# Test MongoDB
mongosh mongodb://localhost:27017

# Test MySQL
mysql -h localhost -u user -p

# Test PostgreSQL
psql -h localhost -U user -d logs_db
```

## 📚 API Reference

### `RequestLoggingMiddleware`

```python
RequestLoggingMiddleware(
    app,
    exclude_paths: list = None,
    enable_db_monitoring: bool = True,
    storage_type: str = None,
    connection_string: str = None,
    cleanup_days: int = 7,
    print_logs: bool = True,
    **storage_kwargs
)
```

**Parameters:**
- `app`: FastAPI/Starlette application instance
- `exclude_paths`: List of paths to exclude from logging
- `enable_db_monitoring`: Enable database operation tracking
- `storage_type`: Storage backend (`'local'`, `'mongodb'`, `'mysql'`, `'postgresql'`, `'sqlite'`)
- `connection_string`: Database connection string
- `cleanup_days`: Days to retain logs before deletion
- `print_logs`: Whether to print logs to console
- `**storage_kwargs`: Additional storage-specific parameters

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📧 Contact

- **Author:** Hariharan S
- **Email:** hvasan59@gmail.com
- **GitHub:** [@Hari-vasan](https://github.com/Hari-vasan)

## 🔗 Links

- [Documentation](https://github.com/Hari-vasan/logpulses#readme)
- [Issue Tracker](https://github.com/Hari-vasan/logpulses/issues)
- [PyPI Package](https://pypi.org/project/logpulses/)
- [Changelog](CHANGELOG.md)

## ⭐ Support

If you find this project useful, please consider giving it a star on GitHub! It helps others discover the project and motivates continued development.

---

**Made with ❤️ by Hariharan S**