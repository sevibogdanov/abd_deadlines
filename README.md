# abd_deadlines
бот и дашборд для отслеживания дедлайнов

deadline_bot.py - основной скрипт  
abd_fun.py - функции для команд  
recover.py - запускается ежеминутно кроном на сервере для восстановления бота  
gs_to_pg.py - перенос из google sheets в postgres  
abd_mailing.py - ежедневная рассылка в 8.40 утра по дедлайнам на сегодня и через 3 дня  
* mcfg_abd - содержит токен и функции подключения к постгресу  

Схема:  
![Схема бота](https://github.com/user-attachments/assets/c4059333-ea3c-4f7f-b885-a8fbf4b19ade)



