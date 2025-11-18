"""
安全模块工具
"""
from datetime import datetime, timedelta, timezone
from base64 import b64decode, b64encode
from uuid import uuid4
from bcrypt import checkpw, gensalt, hashpw
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad
from jose import jwt


class AESAPI:
    def __init__(self, key: str) -> None:
        # ECB模式,加密结果固定
        self._cipher = AES.new(key.encode(), AES.MODE_ECB)

    @property
    def cipher(self):
        return self._cipher

    def encrypt(self, plain_text: str) -> str:
        """加密:pad->encrypt->b64encode
        """

        # 对明文进行补全至块大小的填充
        padded_text = pad(plain_text.encode(), AES.block_size)

        # 加密
        ciphertext = self.cipher.encrypt(padded_text)

        # 返回Base64编码的密文
        return b64encode(ciphertext).decode()

    def decrypt(self, encrypted_value: str) -> str:
        """解密:b64decode->decrypt->unpad
        """

        # 将Base64编码的密文解码为字节
        ciphertext = b64decode(encrypted_value)

        # 解密
        decrypted_text = unpad(self.cipher.decrypt(ciphertext), AES.block_size)

        # 将解密后的字节串转换回字符串
        return decrypted_text.decode()

    def phone_encrypt(self, plain_text: str) -> str:
        """加密手机号;手机号按照每3位组成一段密文,然后拼接而成;
        如:18012345678,分为 180,801,012,123,......678;
        使用AES ECB模式加密,保障同样的明文输出同样的密文,用于手机号的模糊匹配

        Args:
            plain_text:手机号明文,例如:18012345678

        Returns:
            str:加密后的手机号
        """
        if (length := len(plain_text)) == 0:
            return ""

        end_pos = max(length-3, 0)
        return ",".join([self.encrypt(plain_text[i:i+3]) for i in range(end_pos+1)])

    def phone_decrypt(self, encrypted_text: str, mask: bool = True) -> str:
        """解密手机号

        Args:
            encrypted_text:加密的手机号
            mask: 是否脱敏显示,比如180****5678        

        Returns:
            str:手机号明文
        """
        if not encrypted_text:
            return ""

        phone_array = [self.decrypt(v) for v in encrypted_text.split(",")]
        phone = "".join([phone_array[i][0]
                        for i in range(8)]) + phone_array[-1]

        if mask:
            phone = f"{phone[:3]}****{phone[7:]}"

        return phone


class HashAPI:
    @staticmethod
    def hash(plain_text: str) -> str:
        """明文哈希加密
        """
        return hashpw(plain_text.encode(), gensalt()).decode()

    @staticmethod
    def verify(plain_text: str, hash_text: str) -> bool:
        """验证明文和密文的内容是否一致
        """
        return checkpw(plain_text.encode(), hash_text.encode())


class JWTAPI:
    def __init__(self, key: str, algorithm: str = "HS256") -> None:
        """JWT对象

        Args:
            key:str,密钥
            algorithm:str,加密算法

        """
        self._key = key
        self._algorithm = algorithm

    @property
    def key(self):
        return self._key

    @property
    def algorithm(self):
        return self._algorithm

    def encode(self, expire_min: float, **kw) -> str:
        """编码JWT的token, 其中jti,iat,exp会自动生成,无需设置

        Args:
            expire_min:float,token的有效期(分钟)

        """
        jti = uuid4().hex
        iat = datetime.now(timezone.utc)
        exp = iat + timedelta(minutes=expire_min)
        payload = dict(**kw, exp=exp, iat=iat, jti=jti)
        return jwt.encode(payload, key=self.key, algorithm=self.algorithm)

    def decode(self, token: str) -> dict:
        """解码JWT的token
        """
        return jwt.decode(token=token, key=self.key, algorithms=[self.algorithm])


if __name__ == "__main__":
    ...
