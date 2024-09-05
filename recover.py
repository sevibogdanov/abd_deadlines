import subprocess
import os

if True:#deadline bot
    health = subprocess.check_output("pgrep -f -c deadline_bot.py",shell=True)
    if int(health)==1:
        os.system('cd  ~/deadline_bot/  && python3 deadline_bot.py;')
