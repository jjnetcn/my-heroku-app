import os
import threading
import mysql.connector
from flask import Flask

app = Flask(__name__)

# 全局变量
ramcnt = 0
wramcnt = 0
bramcnt = 0
ramscnt = 0
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
    global ramcnt,wramcnt,bramcnt,ramscnt,distcnt
    try:
        # 连接数据库
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # 查询1：ramcnt
        query1 = "SELECT COUNT(*) FROM eos_USERRES WHERE ram_bytes >= 1024 * 1024"
        cursor.execute(query1)
        result1 = cursor.fetchone()
        ramcnt = result1[0] if result1 else 0
        print(f"ram: {ramcnt}")

        # 查询2：wramcnt
        query2 = "select  count(*) from eos_CURRENCY_BAL where  contract = 'eosio.wram' and currency = 'WRAM' and amount >=1024*1024  "
        cursor.execute(query2)
        result2 = cursor.fetchone()
        wramcnt = result2[0] if result2 else 0
        print(f"wramcnt: {wramcnt}")

        # 查询3：bramcnt
        query3 = "SELECT COUNT(*) FROM eos_CURRENCY_BAL WHERE contract = 'ram.defi' AND currency = 'BRAM' AND amount >= 1024 * 1024"
        cursor.execute(query3)
        result3 = cursor.fetchone()
        bramcnt = result3[0] if result3 else 0
        print(f"bramcnt: {bramcnt}")

        # 查询4：ramscnt
        query4 = "SELECT COUNT(*) FROM eos_CURRENCY_BAL WHERE contract = 'newrams.eos' AND currency = 'RAMS' AND amount > 21226"
        cursor.execute(query4)
        result4 = cursor.fetchone()
        ramscnt = result4[0] if result4 else 0
        print(f"ramscnt: {ramscnt}")
        
        # 查询5：distcnt
        query5 = """
        SELECT COUNT(*) FROM (
            SELECT account_name FROM eos_USERRES WHERE ram_bytes >= 1024 * 1024 
            UNION
            select account_name from eos_CURRENCY_BAL where  contract = 'eosio.wram' and currency = 'WRAM' and amount >=1024*1024  
            UNION
            SELECT account_name FROM eos_CURRENCY_BAL WHERE contract = 'ram.defi' AND currency = 'BRAM' AND amount >= 1024 * 1024
            UNION
            SELECT account_name FROM eos_CURRENCY_BAL WHERE contract = 'newrams.eos' AND currency = 'RAMS' AND amount > 21226
        ) a
        """
        cursor.execute(query5)
        result5 = cursor.fetchone()
        distcnt = result5[0] if result5 else 0
        print(f"distcnt: {distcnt}")
        
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        ramcnt = 0
    
    # 1分钟后再次执行
    threading.Timer(60, refresh).start()

# 程序启动时首先执行一次
refresh()


@app.route('/')
def display_ramcnt():
    return (f'RAM Holders larger than 1M: {ramcnt}<br>'
            f'WRAM Holders larger than 1M: {wramcnt}<br>'
            f'BRAM Holders larger than 1M: {bramcnt}<br>'
            f'RAMS Holders larger than 1M (~=21226): {ramscnt}<br>'
            f'Distinct Holders: {distcnt}')

if __name__ == '__main__':
    # 从环境变量获取端口
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
