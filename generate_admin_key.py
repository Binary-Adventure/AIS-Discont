import sys
import traceback
from DataBase import DataBaseManager
from Api.key_manager import KeyManager
from config import config

def generate_admin_key():
    print("=" * 60)
    print("Генерация административного API ключа")
    print("=" * 60)
    
    try:
        print("\nПодключение к базе данных...")
        db_manager = DataBaseManager(config)
        key_manager = KeyManager(db_manager)
        
        print("Проверка таблицы API ключей...")
        key_manager.create_api_keys_table()
        
        print("\nГенерация административного ключа...")
        api_key = key_manager.create_admin_key(description="Master Admin Key")
        
        print("\n" + "=" * 60)
        print("АДМИНИСТРАТИВНЫЙ КЛЮЧ УСПЕШНО СОЗДАН!")
        print("=" * 60)
        print(f"\nВаш API ключ: {api_key}")
        print("\nВАЖНО:")
        print("   - Скопируйте этот ключ!")
        print("   - Он отображается только один раз!")
        print("\n" + "=" * 60)
        
        db_manager.close()
        return api_key
        
    except ValueError as e:
        print(f"\nОшибка: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nПроизошла ошибка: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    generate_admin_key()