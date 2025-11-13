import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def derive_key(password: str, salt: bytes) -> bytes:
    """Создает ключ из пароля"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key

def encrypt_text(text: str, password: str) -> str:
    """Шифрует текст с помощью пароля"""
    # Генерируем случайную соль
    salt = os.urandom(16)
    
    # Создаем ключ из пароля
    key = derive_key(password, salt)
    
    # Шифруем текст
    fernet = Fernet(key)
    encrypted_text = fernet.encrypt(text.encode())
    
    # Комбинируем соль и зашифрованный текст
    combined = salt + encrypted_text
    
    # Кодируем в base64 для удобного хранения
    return base64.urlsafe_b64encode(combined).decode()

def main():
    # Запрашиваем пароль
    password = input("Введите пароль для шифрования: ")
    
    try:
        # Импортируем текст из clear_text.py
        from clear_text import text_to_encrypt
        
        # Шифруем текст
        encrypted_text = encrypt_text(text_to_encrypt, password)
        
        # Создаем файл encrypted.py с зашифрованным текстом
        with open('miracle.py', 'w', encoding='utf-8') as f:
            f.write(f'encrypted_text = """{encrypted_text}"""\n')
        
        print("Текст успешно зашифрован и сохранен в miracle.py")
        
    except ImportError:
        print("Ошибка: Файл clear_text.py не найден или не содержит переменную text_to_encrypt")
    except Exception as e:
        print(f"Ошибка при шифровании: {e}")

if __name__ == "__main__":
    main()
