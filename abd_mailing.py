import telebot
import datetime
import mcfg_abd
import time
import pandas as pd

bot = telebot.TeleBot(mcfg_abd.bot_token)

conn = mcfg_abd.conn2()
cur = conn.cursor()
cur.execute(f"""select id from users where flg = 1;""")
ids = cur.fetchall()
conn.close()
ids = [int(i[0]) for i in ids]

df = pd.read_sql('''select
	date(dtime) dt,
	d_nm,
	d_type,
	id,
	link,
	dtime::date-now()::date days
from
	deadline_view dt
where
dtime::date = now()::date
or 
dtime::date - interval '3' day = now()::date
order by dtime'''
,con=mcfg_abd.conn2())

if len(df) > 0:
    cnt=1
    length = len(df)
    text = 'Дедлайны:\n'
    for index,row in df.iterrows():
        if row['days']==0:
            deadline = 'Сегодня!'
        elif row['days']==3:
            deadline = '3 дня!'
        text += f"""{row['d_type']} ({deadline})
{row['dt']}
<a href="{row['link']}">{row['d_nm']}</a>
    """
        cnt+=1
        if cnt <= length:
            text+='-\n'


    for id in ids:
        time.sleep(1)
        try:
            bot.send_message(id,text, parse_mode='HTML')
        except:
            pass