import os
import threading
import mysql.connector
from flask import Flask

app = Flask(__name__)

# 全局变量
ramcnt = 0
ramscnt = 0
bramcnt = 0
distcnt = 0


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
        
        # 查询1：ramcnt
        query1 = "SELECT COUNT(*) FROM eos_USERRES WHERE ram_bytes >= 1024 * 1024"
        cursor.execute(query1)
        result1 = cursor.fetchone()
        ramcnt = result1[0] if result1 else 0

        # 查询2：ramscnt
        query2 = "SELECT COUNT(*) FROM eos_CURRENCY_BAL WHERE contract = 'newrams.eos' AND currency = 'RAMS' AND amount > 21226"
        cursor.execute(query2)
        result2 = cursor.fetchone()
        ramscnt = result2[0] if result2 else 0

        # 查询3：bramcnt
        query3 = "SELECT COUNT(*) FROM eos_CURRENCY_BAL WHERE contract = 'ram.defi' AND currency = 'BRAM' AND amount >= 1024 * 1024"
        cursor.execute(query3)
        result3 = cursor.fetchone()
        bramcnt = result3[0] if result3 else 0

        # 查询4：distcnt
        query4 = """
        SELECT COUNT(*) FROM (
            SELECT account_name FROM eos_USERRES WHERE ram_bytes >= 1024 * 1024 
            UNION
            SELECT account_name FROM eos_CURRENCY_BAL WHERE contract = 'newrams.eos' AND currency = 'RAMS' AND amount > 21226
            UNION
            SELECT account_name FROM eos_CURRENCY_BAL WHERE contract = 'ram.defi' AND currency = 'BRAM' AND amount >= 1024 * 1024
        ) a
        """
        cursor.execute(query4)
        result4 = cursor.fetchone()
        distcnt = result4[0] if result4 else 0
        
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
    return (f'RAM Holders larger than 1M: {ramcnt}<br>'
            f'RAMS Holders larger than 1M (~=21226): {ramscnt}<br>'
            f'BRAM Holders larger than 1M: {bramcnt}<br>'
            f'Distinct Holders: {distcnt}')

if __name__ == '__main__':
    # 从环境变量获取端口
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
