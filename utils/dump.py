import json
import logging
import subprocess
import os
import dill as pickle

from dotenv import load_dotenv

load_dotenv()

user_bd = os.getenv('USER_BD')
password = os.getenv('PASSWORD')
host = os.getenv('HOST')
database = os.getenv('DATABASE')

async def dump_dict(carts, word_list):
    try:
        with open('backups/dump.pkl', 'wb') as file:
            pickle.dump(carts, file)
        with open('backups/word_list.pkl', 'wb') as file:
            pickle.dump(word_list, file)
        logging.info('Dump dict_of_profiles')
        return 1
    except Exception as e:
        logging.error(f'Ошибка дампа dict_of_profiles: {e}')
        return 0

async def backup_bd():
    try:
        backup_path = 'backups/database.sql'
        os.environ['MYSQL_PWD'] = password
        subprocess.run(['mysqldump', '-u', user_bd, database, '--result-file', backup_path])
        logging.info('Dump database')
    except Exception as e:
        logging.error(f'Ошибка дамба базы данных: {e}')
    finally:
        del os.environ['MYSQL_PWD']


