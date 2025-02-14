from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
import json
import hashlib

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
    
    def calculate_message_hash(self, message_dict, prev_hash=None):
        """计算消息的哈希值"""
        # 创建要哈希的消息内容
        hash_content = {
            'content': message_dict['content'],
            'author': message_dict['author'],
            'timestamp': message_dict['timestamp'],
            'prev_hash': prev_hash
        }
        
        # 将字典转换为规范化的JSON字符串（确保相同内容总是产生相同的字符串）
        message_str = json.dumps(hash_content, sort_keys=True)
        
        # 计算SHA256哈希
        return hashlib.sha256(message_str.encode()).hexdigest()
    
    def encrypt_message(self, message_dict, prev_hash=None):
        """加密消息字典，并添加哈希链"""
        # 计算当前消息的哈希值
        current_hash = self.calculate_message_hash(message_dict, prev_hash)
        
        # 将哈希值添加到消息中
        message_dict['hash'] = current_hash
        message_dict['prev_hash'] = prev_hash
        
        message_bytes = json.dumps(message_dict, ensure_ascii=False).encode('utf-8')
        return self.fernet.encrypt(message_bytes).decode('utf-8')
    
    def decrypt_message(self, encrypted_message):
        """解密消息并验证哈希值"""
        try:
            decrypted_bytes = self.fernet.decrypt(encrypted_message.encode('utf-8'))
            message_dict = json.loads(decrypted_bytes.decode('utf-8'))
            
            # 验证消息哈希
            calculated_hash = self.calculate_message_hash(message_dict, message_dict.get('prev_hash'))
            if calculated_hash != message_dict.get('hash'):
                raise ValueError("消息哈希验证失败，消息可能被篡改")
            
            return message_dict
        except Exception as e:
            raise ValueError(f"解密或验证失败：{str(e)}") 