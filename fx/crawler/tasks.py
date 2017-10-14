import psycopg2
import numpy as np
import pandas as pd
import time,datetime
from sqlalchemy import create_engine

def say_Hello():
    print('hello world!!')

def get_latest_rates():
    try:
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        print('***Opened database successfully***')
        
        conn = psycopg2.connect(database="fx", user="fx", password="password", host="localhost", port="5432")
        cur = conn.cursor()
        cur.execute("SELECT time  FROM currency_rate ORDER BY time DESC")
        rows = cur.fetchall()
        if len(rows)!=0:
            latest_time = rows[0][0]
        else:
            latest_time = datetime.datetime.strptime(today,'%Y-%m-%d')
        # pandas datetime not include tzinfo
        latest_time = latest_time.replace(tzinfo=None)
        print('Last Update:{}'.format(latest_time))

        cur.execute("SELECT code  FROM currency_currency")
        rows = cur.fetchall()
        engine = create_engine('postgresql://fx:password@localhost/fx')
        for row in rows:
            currency = row[0]
            dfs = pd.read_html('http://rate.bot.com.tw/xrt/quote/{}/{}/spot'.format(today,currency))
            cur_df = dfs[0]
            cur_df = cur_df.iloc[:,0:6]
            cur_df.columns = ['time','currency_id','cash_buying','cash_selling','spot_buying','spot_selling']
            cur_df['time'] = pd.to_datetime(cur_df['time'])
            if cur_df.size != 0:
                cur_df['currency_id'] = cur_df['currency_id'].str.extract('\((\w+)\)',expand=True)
            cur_df['bank_id'] = '004'
            # data cleaning
            cur_df.replace(to_replace=[0,'-'], value=np.nan, inplace=True)

            mask = (cur_df['time'] > latest_time)
            df = cur_df.loc[mask]
            df.to_sql('currency_rate',engine,if_exists='append', index=False)
            print(currency+' done')
        print('***Operation done successfully***')
        conn.commit()
        cur.close()
    except psycopg2.DatabaseError as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
