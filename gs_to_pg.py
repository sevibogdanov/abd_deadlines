import pandas as pd
import datetime
import mcfg_abd

df = pd.read_csv('https://docs.google.com/spreadsheets/d/e/2PACX-1vR9qLWoMIogTOWiCW4_-R8OETkR667_jyEYj57e8Auh6VkqQHfQbSpM_4-cBSPoegJcliP_SP4AcoJ6/pub?gid=1036789569&single=true&output=csv', encoding = 'utf8')
df['dtime']  = pd.to_datetime(df['Срок сдачи'] +' '+ df['Время сдачи'],format="%d.%m.%Y %H:%M")
df.rename(columns={
    'Предмет':'d_type',
    'Ссылка':'link',
    'Работа':'d_nm'
},inplace=True)

conn = mcfg_abd.conn2()
cur = conn.cursor()
cur.execute(f"""delete from deadline_gs;""")
conn.commit()
conn.close()

df[['dtime','d_nm','d_type','link']].to_sql('deadline_gs',con=mcfg_abd.my_connection(),index=False,if_exists='append')