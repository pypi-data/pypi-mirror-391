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

def decrypt_text(encrypted_data: str, password: str) -> str:
    """Дешифрует текст с помощью пароля"""
    try:
        # Декодируем из base64
        combined = base64.urlsafe_b64decode(encrypted_data.encode())
        
        # Извлекаем соль (первые 16 байт) и зашифрованный текст
        salt = combined[:16]
        encrypted_text = combined[16:]
        
        # Создаем ключ из пароля
        key = derive_key(password, salt)
        
        # Дешифруем текст
        fernet = Fernet(key)
        decrypted_text = fernet.decrypt(encrypted_text)
        
        return decrypted_text.decode()
    
    except Exception as e:
        raise ValueError("Неверный пароль или поврежденные данные")

def main():
    # Запрашиваем пароль
    password = input("Введите пароль для дешифрования: ")
    
    try:
        # Импортируем зашифрованный текст из encrypted.py
        from miracle import encrypted_text
        
        # Дешифруем текст
        decrypted_text = decrypt_text(encrypted_text, password)
        
        print("\nРасшифрованный текст:")
        print("=" * 50)
        print(decrypted_text)
        print("=" * 50)
        
    except ImportError:
        print("Ошибка: Файл miracle.py не найден или не содержит переменную encrypted_text")
    except ValueError as e:
        print(f"Ошибка: {e}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    main()
