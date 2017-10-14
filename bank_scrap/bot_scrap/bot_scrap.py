import psycopg2
import numpy as np
import pandas as pd
import time,datetime
from dateutil.rrule import rrule, MONTHLY
from sqlalchemy import create_engine
from pytz import timezone

start_date = datetime.date(2017,7,1)
# end_date = datetime.date.today()
end_date = datetime.date(2017,9,30)
def scrap():
    try:
        print('***Opened database successfully***')
        conn = psycopg2.connect(database="fx", user="fx", password="password", host="localhost", port="5432")
        cur = conn.cursor()
        cur.execute("SELECT code  FROM currency_currency")
        rows = cur.fetchall()
        for row in rows:
            currency = row[0]
            date_range = pd.date_range(start_date,end_date).strftime('%Y-%m-%d').tolist()
            histories = pd.DataFrame(columns=['time','currency_id','cash_buying','cash_selling','spot_buying','spot_selling'])
            histories['time'] = pd.to_datetime(histories['time'])
            # histories = histories.set_index('time')
            for d in date_range:
                dfs = pd.read_html('http://rate.bot.com.tw/xrt/quote/{}/{}/spot'.format(d,currency))
                cur_df = dfs[0]
                cur_df = cur_df.iloc[:,0:6]
                cur_df.columns = ['time','currency_id','cash_buying','cash_selling','spot_buying','spot_selling']
                cur_df['time'] = pd.to_datetime(cur_df['time'])
                # cur_df = cur_df.set_index('time')

                # data cleaning
                cur_df.replace(to_replace=[0,'-'], value=np.nan, inplace=True)
                histories = cur_df.append(histories)

            histories['currency_id'] = histories['currency_id'].str.extract('\((\w+)\)',expand=True)
            histories['bank_id'] = '004'
            


            engine = create_engine('postgresql://fx:password@localhost/fx')
            histories.to_sql('currency_rate',engine,if_exists='append', index=False)
            print('{} done!!'.format(currency))
        print('***Operation done successfully***')
        conn.commit()
        cur.close()
    except psycopg2.DatabaseError as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
def drop():
    try:
        print('***Opened database successfully***')
        conn = psycopg2.connect(database="fx", user="fx", password="password", host="localhost", port="5432")
        cur = conn.cursor()
        cur.execute("DELETE FROM currency_rate")
        
        print('***Operation done successfully***')
        conn.commit()
        cur.close()
    except psycopg2.DatabaseError as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

if __name__ == '__main__':
    scrap()
