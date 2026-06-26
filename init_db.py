import os
from DataBase import DataBaseManager
from config import config

def init_database():
    print("Подключение к базе данных...")
    db = DataBaseManager(config)
    
    sql_path = os.path.join(os.path.dirname(__file__), 'DataBase', 'tables.sql')
    print(f"Выполнение SQL скрипта: {sql_path}")
    db.init_db(sql_path)
    
    print("База данных успешно инициализирована!")
    db.close()

if __name__ == '__main__':
    init_database()
