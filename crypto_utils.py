from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
import base64
import json
import hashlib
from mnemonic import Mnemonic
import os

class MessageCrypto:
    def __init__(self, mnemonic_words):
        """
        初始化加密器
        mnemonic_words: 助记词字符串
        """
        # 使用助记词生成密钥
        mnemo = Mnemonic("chinese_simplified")
        if not mnemo.check(mnemonic_words):
            raise ValueError("无效的助记词")
        
        # 从助记词生成种子
        seed = mnemo.to_seed(mnemonic_words)
        # 使用种子的前32字节作为密钥
        key = base64.urlsafe_b64encode(seed[:32])
        self.fernet = Fernet(key)
    
    @staticmethod
    def generate_mnemonic():
        """生成新的助记词"""
        mnemo = Mnemonic("chinese_simplified")
        return mnemo.generate()
    
    @staticmethod
    def verify_mnemonic(mnemonic_words):
        """验证助记词是否有效"""
        mnemo = Mnemonic("chinese_simplified")
        return mnemo.check(mnemonic_words)
    
    def calculate_message_hash(self, message_dict, prev_hash=None):
        """计算消息的哈希值"""
        hash_content = {
            'content': message_dict['content'],
            'author': message_dict['author'],
            'timestamp': message_dict['timestamp'],
            'prev_hash': prev_hash
        }
        
        message_str = json.dumps(hash_content, sort_keys=True)
        return hashlib.sha256(message_str.encode()).hexdigest()
    
    def encrypt_message(self, message_dict, prev_hash=None):
        """加密消息字典，并添加哈希链"""
        current_hash = self.calculate_message_hash(message_dict, prev_hash)
        message_dict['hash'] = current_hash
        message_dict['prev_hash'] = prev_hash
        
        message_bytes = json.dumps(message_dict, ensure_ascii=False).encode('utf-8')
        return self.fernet.encrypt(message_bytes).decode('utf-8')
    
    def decrypt_message(self, encrypted_message):
        """解密消息并验证哈希值"""
        try:
            decrypted_bytes = self.fernet.decrypt(encrypted_message.encode('utf-8'))
            message_dict = json.loads(decrypted_bytes.decode('utf-8'))
            
            calculated_hash = self.calculate_message_hash(message_dict, message_dict.get('prev_hash'))
            if calculated_hash != message_dict.get('hash'):
                raise ValueError("消息哈希验证失败，消息可能被篡改")
            
            return message_dict
        except Exception as e:
            raise ValueError(f"解密或验证失败：{str(e)}")

    def encrypt_config(self, config_dict):
        """加密配置字典"""
        config_bytes = json.dumps(config_dict, ensure_ascii=False).encode('utf-8')
        return self.fernet.encrypt(config_bytes).decode('utf-8')

    def decrypt_config(self, encrypted_config):
        """解密配置字典"""
        try:
            decrypted_bytes = self.fernet.decrypt(encrypted_config.encode('utf-8'))
            return json.loads(decrypted_bytes.decode('utf-8'))
        except Exception as e:
            raise ValueError(f"配置解密失败：{str(e)}")

    @staticmethod
    def generate_config_key():
        """生成用于加密配置文件的密钥"""
        return base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8') 