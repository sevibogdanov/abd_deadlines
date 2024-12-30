import telebot
import datetime
import mcfg_abd
import pandas as pd
import os
from telebot import types

bot = telebot.TeleBot(mcfg_abd.bot_token)

def markup():
    commands = ['/show','/schedule']
    markups = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for each in commands:
        markups.add(types.KeyboardButton(f"{each}"))
    return markups

def log(message):
    #create table log_table (log_time timestamp,message_text text,user_id float8,user_name text); --log table
    try:
        now_time = datetime.datetime.now()
        sql = f"""insert into log_table (log_time,message_text,user_id,user_name) VALUES (
             TO_TIMESTAMP('{now_time}', 'YYYY-mm-dd HH24:MI:SS'),
            '{message.text}',
            {message.from_user.id},
            '{message.from_user.username}'
        );"""

        conn = mcfg_abd.conn2()
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        conn.close()
    except:
        pass

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
/reload - обновить данные из gs
Остальные команды:
/show - отобразить дедлайны на 15 дней
/schedule - отобразить расписание встреч на 15 дней
/showall - отобразить все дедлайны
/start - подключить себя к рассылке
/turnoff - отключить себя от рассылки
/dash - ссылка на дашборд'''
    default_message_all = '''/show - отобразить дедлайны на 15 дней
/schedule - отобразить расписание встреч на 15 дней
/showall - отобразить все дедлайны
/start - подключить себя к рассылке
/turnoff - отключить себя от рассылки
/dash - ссылка на дашборд'''
    if check_admin(message):
        bot.send_message(message.from_user.id,default_message_admin,reply_markup=markup())
    else:
        bot.send_message(message.from_user.id,default_message_all,reply_markup=markup())

def show(message,all=False):
    if not all:
        df = pd.read_sql('''select date(dtime) dt,d_nm,d_type,id,link,
dtime::date-now()::date days
from deadline_view dt 
where 
((now()::date - interval '7' day < dtime and d_type = 'кс') or (now()::date - interval '0' day <= dtime))
and 
((now()::date + interval '15' day > dtime and d_type = 'кс') or d_type != 'кс')
order by dtime''',con=mcfg_abd.conn2())
    else:
        df = pd.read_sql('''select date(dtime) dt,d_nm,d_type,id,link,
dtime::date-now()::date days
from deadline_view dt 
where now()::date - interval '7' day < dtime 
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
    bot.send_message(message.from_user.id,text, parse_mode='HTML', disable_web_page_preview=True,reply_markup=markup())

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
    conn.close()
    return flg[0][0] == 1

def reload(message):
    os.system('cd ~/deadline_bot/ && python3 gs_to_pg.py;')
    bot.send_message(message.from_user.id, 'обновлено',reply_markup=markup())

def start(message):
    if not check_user(message):
        create_user(message)
    else:
        conn = mcfg_abd.conn2()
        cur = conn.cursor()
        cur.execute(f"""update users set flg = 1 where id= {message.from_user.id};""")
        conn.commit()
        conn.close()
    bot.send_message(message.from_user.id,'Вы подключены к рассылке по дедлайнам!',reply_markup=markup())

def turnoff(message):
    conn = mcfg_abd.conn2()
    cur = conn.cursor()
    cur.execute(f"""update users set flg = 0 where id= {message.from_user.id};""")
    conn.commit()
    conn.close()
    bot.send_message(message.from_user.id,'Вы отключены от рассылки по дедлайнам!',reply_markup=markup())

def schedule(message):
    df = pd.read_sql('''select
        subject,
        tutor,
        link,
        start_dt::time tm,
        start_dt::date dt,
	    extract(isodow from start_dt) weekday
    from
        schedule_gs 
    where now()::date < start_dt 
    and now()::date > start_dt::date - interval '14' day
    order by start_dt''', con=mcfg_abd.conn2())

    weekdays = {1:'пн',2:'вт',3:'ср',4:'чт',5:'пт',6:'сб',7:'вс'}

    cnt = 1
    length = len(df)
    text = ''
    for index, row in df.iterrows():
        text += f"""{row['tutor']}
    {row['dt']} - {weekdays[row['weekday']]} ({row['tm'].strftime('%H:%M')})
    <a href="{row['link']}">{row['subject']}</a>
    """
        cnt += 1
        if cnt <= length:
            text += '-\n'
    bot.send_message(message.from_user.id, text, parse_mode='HTML', disable_web_page_preview=True,reply_markup=markup())

def scheduleon(message):
    conn = mcfg_abd.conn2()
    cur = conn.cursor()
    cur.execute(f"""update users set schedule = 1 where id= {message.from_user.id};""")
    conn.commit()
    conn.close()
    bot.send_message(message.from_user.id,'Вы подключены к рассылке по расписанию!',reply_markup=markup())

def scheduleoff(message):
    conn = mcfg_abd.conn2()
    cur = conn.cursor()
    cur.execute(f"""update users set schedule = 0 where id= {message.from_user.id};""")
    conn.commit()
    conn.close()
    bot.send_message(message.from_user.id,'Вы отключены от рассылки по расписанию!',reply_markup=markup())

def remove_deadline(message):
    try:
        vals = message.text.split('\n')
        id = int(vals[1])
        conn = mcfg_abd.conn2()
        cur = conn.cursor()
        cur.execute(f"""delete from deadline_table where id= {id};""")
        conn.commit()
        conn.close()
        bot.send_message(message.from_user.id, f'id {id} удален!',reply_markup=markup())
    except:
        bot.send_message(message.from_user.id, f'неправильный формат!',reply_markup=markup())

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


        bot.send_message(message.from_user.id, f'Дедлай {deadline_topic},{deadline_name}, до {text_date} добавлен (id {flg[0][0]})!',reply_markup=markup())
    except:
        bot.send_message(message.from_user.id, f'неправильный формат!',reply_markup=markup())

def dash(message):
    text = '''<a href="https://datalens.yandex/moq9iz7pv67a9">ссылка на дашборд</a>
<a href="https://docs.google.com/spreadsheets/d/13lHNf6xU6tZhqzVMAb8sV3RgyyDatepwo7FJ6FhZ0vY/edit?gid=1036789569#gid=1036789569">дедлайны в гугл листах</a>
<a href="https://docs.google.com/spreadsheets/d/1Y-A1r6fOZVnSD8tKFeBN3kiVCh45MFdLlEVk_zf9G2w/edit?gid=0#gid=0">расписание в гугл листах</a>'''
    bot.send_message(message.from_user.id, text, parse_mode='HTML', disable_web_page_preview=True,reply_markup=markup())