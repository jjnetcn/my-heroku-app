import os
import threading
import mysql.connector
from flask import Flask

app = Flask(__name__)

# 全局变量
ramcnt = 0

# 数据库连接配置
db_config = {
    'host': 'pubdb.eu.eosamsterdam.net',
    'port': 3301,
    'user': 'lightapiro',
    'password': 'lightapiro',
    'database': 'lightapi'
}

def refresh():
    global ramcnt
    try:
        # 连接数据库
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # 执行查询
        query = "SELECT COUNT(*) FROM eos_USERRES WHERE ram_bytes >= 1024 * 1024"
        cursor.execute(query)
        result = cursor.fetchone()
        
        if result:
            ramcnt = result[0]
        else:
            ramcnt = 0
        
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        ramcnt = 0
    
    # 1分钟后再次执行
    threading.Timer(60, refresh).start()

# 程序启动时首先执行一次
refresh()
print(f"ramholders: {ramcnt}")

@app.route('/')
def display_ramcnt():
    return f'RAM Holders larger than 1M: {ramcnt}'

if __name__ == '__main__':
    # 从环境变量获取端口
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
