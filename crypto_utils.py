from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
import json

class MessageCrypto:
    def __init__(self, password):
        """
        初始化加密器
        password: 用户提供的密码
        """
        # 使用密码生成加密密钥
        salt = b'gitchat_salt'  # 在实际应用中应该为每个用户生成唯一的salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        self.fernet = Fernet(key)
    
    def encrypt_message(self, message_dict):
        """加密消息字典"""
        message_bytes = json.dumps(message_dict, ensure_ascii=False).encode('utf-8')
        return self.fernet.encrypt(message_bytes).decode('utf-8')
    
    def decrypt_message(self, encrypted_message):
        """解密消息"""
        try:
            decrypted_bytes = self.fernet.decrypt(encrypted_message.encode('utf-8'))
            return json.loads(decrypted_bytes.decode('utf-8'))
        except Exception as e:
            raise ValueError(f"解密失败：密码可能不正确 - {str(e)}") 