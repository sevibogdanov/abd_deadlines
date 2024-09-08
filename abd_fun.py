import telebot
import datetime
import mcfg_abd
import pandas as pd

bot = telebot.TeleBot(mcfg_abd.bot_token)



def check_admin(message):
    admins = {'id':[
        193776212,237028854
    ],
    'login':[
        'xenia_lapatina'
    ]}

    if message.from_user.id in admins['id'] or message.from_user.username in admins['login']:
        return True
    return False

def default_message(message):
    default_message_admin ='''Команды для админов:
--
добавить
01.01.1990 23:59
название дедлайна
тема
--
убрать
id
--
Остальные команды:
/show - отобразить дедлайн (-8;+15)
/showall - отобразить дедлайны (-14;все)
/start - подключить себя к рассылке
/turnoff - отключить себя от рассылки
/dash - ссылка на дашборд'''
    default_message_all = '''/show - отобразить дедлайн (-8;+15)
/showall - отобразить дедлайны (-14;все)
/start - подключить себя к рассылке
/turnoff - отключить себя от рассылки
/dash - ссылка на дашборд'''
    if check_admin(message):
        bot.send_message(message.from_user.id,default_message_admin)
    else:
        bot.send_message(message.from_user.id,default_message_all)

def show(message,all=False):
    if not all:
        df = pd.read_sql('''select date(dtime) dt,d_nm,d_type,id,link,
dtime::date-now()::date days
from deadline_view dt 
where 
now()::date - interval '8' day < dtime
and 
((now()::date + interval '15' day > dtime and d_type = 'кс') or d_type != 'кс')
order by dtime''',con=mcfg_abd.conn2())
    else:
        df = pd.read_sql('''select date(dtime) dt,d_nm,d_type,id,link,
dtime::date-now()::date days
from deadline_view dt 
where now()::date - interval '15' day < dtime
order by dtime ''',con=mcfg_abd.conn2())
        
    cnt=1
    length = len(df)
    text = 'Дедлайны:\n'  
    for index,row in df.iterrows():
        text += f"""{row['d_type']} ({row['days']} дн.)
{row['dt']} (id {row['id']})
<a href="{row['link']}">{row['d_nm']}</a>
"""
        cnt+=1
        if cnt <= length:
            text+='-\n'
    bot.send_message(message.from_user.id,text, parse_mode='HTML')

def create_user(message):
    conn = mcfg_abd.conn2()
    cur = conn.cursor()
    cur.execute(f"""insert into users (id,flg) VALUES ({message.from_user.id},1);""")
    conn.commit()
    conn.close()

def check_user(message):
    conn = mcfg_abd.conn2()
    cur = conn.cursor()
    cur.execute(f"""select count(*) from users where id = {message.from_user.id};""")
    flg = cur.fetchall()
    return flg[0][0] == 1

def start(message):
    if not check_user(message):
        create_user(message)
    else:
        conn = mcfg_abd.conn2()
        cur = conn.cursor()
        cur.execute(f"""update users set flg = 1 where id= {message.from_user.id};""")
        conn.commit()
        conn.close()
    bot.send_message(message.from_user.id,'Вы подключены к рассылке!')

def turnoff(message):
    conn = mcfg_abd.conn2()
    cur = conn.cursor()
    cur.execute(f"""update users set flg = 0 where id= {message.from_user.id};""")
    conn.commit()
    conn.close()
    bot.send_message(message.from_user.id,'Вы отключены от рассылки!')

def remove_deadline(message):
    try:
        vals = message.text.split('\n')
        id = int(vals[1])
        conn = mcfg_abd.conn2()
        cur = conn.cursor()
        cur.execute(f"""delete from deadline_table where id= {id};""")
        conn.commit()
        conn.close()
        bot.send_message(message.from_user.id, f'id {id} удален!')
    except:
        bot.send_message(message.from_user.id, f'неправильный формат!')

def add_deadline(message):
    try:
        vals = message.text.split('\n')
        text_date = vals[1]
        deadline_name = vals[2]
        deadline_topic = vals[3]

        text_date = text_date.split(' ')
        text_date[0] = '.'.join(text_date[0].split('.')[::-1])

        if len(text_date) ==2:
            text_date = ' '.join(text_date)
        elif deadline_topic=='кс':
            text_date = ' '.join(text_date) + ' 19:00'
        else:
            text_date = ' '.join(text_date) + ' 23:59'

        conn = mcfg_abd.conn2()
        cur = conn.cursor()
        cur.execute(f"""insert into deadline_table(dtime,d_nm,d_type) 
                    VALUES (TO_TIMESTAMP('{text_date}', 'YYYY-mm-dd HH24:MI:SS'),
                            '{deadline_name}',
                            '{deadline_topic}');""")
        conn.commit()
        conn.close()

        conn = mcfg_abd.conn2()
        cur = conn.cursor()
        cur.execute(f"""select max(id) from deadline_table ;""")
        flg = cur.fetchall()


        bot.send_message(message.from_user.id, f'Дедлай {deadline_topic},{deadline_name}, до {text_date} добавлен (id {flg[0][0]})!')
    except:
        bot.send_message(message.from_user.id, f'неправильный формат!')

def dash(message):
    text = '''<a href="https://datalens.yandex/moq9iz7pv67a9">ссылка на дашборд</a>
<a href="https://docs.google.com/spreadsheets/d/13lHNf6xU6tZhqzVMAb8sV3RgyyDatepwo7FJ6FhZ0vY/edit?gid=1036789569#gid=1036789569">дедлайны в гугл листах</a>'''
    bot.send_message(message.from_user.id, text, parse_mode='HTML', disable_web_page_preview=True)
