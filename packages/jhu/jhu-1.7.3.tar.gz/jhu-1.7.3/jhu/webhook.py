"""
日期:2023-12-01
内容:
- 集成钉钉和企业微信的webhook能力
参考文档:
- https://open.dingtalk.com/document/robots/custom-robot-access
- https://developer.work.weixin.qq.com/document/path/91770
"""
from typing import Any
from base64 import b64encode
from enum import IntEnum
from hashlib import sha256
from hmac import new as hmac_new
from requests import session
from time import time
from urllib.parse import quote_plus


class WebHookType(IntEnum):
    DINGTALK = 0
    WECOM = 1


class WebHook:
    def __init__(self, webhook: WebHookType, url: str, sk: str | None = None) -> None:
        """Webhook对象

        Args:
            webhook:WebHookType,webhook的类型
            url:str,webhook的url
            sk:str,webhook的密钥,由webhook提供
        """
        self.__webhook = webhook
        self.__url = url
        self.__sk = sk

    @property
    def webhook(self):
        return self.__webhook

    @property
    def url(self):
        return self.__url

    @property
    def sk(self):
        return self.__sk

    def text(self, content: str, phone: list[str] | None = None, id: list[str] | None = None, all: bool = False) -> dict:
        """text类型,支持钉钉和企微

        Args:
            content:str,发送内容
            phone:list[str],需要@的用户手机号,比如['151****1234', '151****5678']
            id:list[str],需要@的用户ID,比如['id001', 'id002']
            all:bool,是否@ALL, 仅钉钉有效,企微请在id或phone里用'@all'来表示
        """
        result: dict[str, Any] = {"msgtype": "text"}
        text: dict[str, Any] = {"content": content}

        match(self.webhook):
            case WebHookType.DINGTALK:
                at = {"atMobiles": phone, "isAtAll": all, "atUserIds": id}
                result["at"] = at
            case WebHookType.WECOM:
                text["mentioned_list"] = id
                text["mentioned_mobile_list"] = phone
        result["text"] = text
        return result

    def link(self, title: str, text: str, url: str, pic: str = "") -> dict:
        """link类型,仅支持钉钉

        Args:
            title:str,消息标题
            text:str,消息内容.如果太长只会展示部分
            url:str,点击消息跳转URL
            pic:str,图片URL
        """
        result: dict[str, str | dict] = {"msgtype": "link"}
        link = {"title": title, "text": text, "messageUrl": url, "picUrl": pic}
        result["link"] = link
        return result

    def markdown(self, text: str, title: str = "") -> dict:
        """markdown类型,支持钉钉和企微

        Args:
            text:str,markdown内容
            title:str,markdown标题,仅钉钉需要填写
        """
        result: dict[str, str | dict] = {"msgtype": "markdown"}

        match(self.webhook):
            case WebHookType.DINGTALK:
                markdown = {"text": text, "title": title}
            case WebHookType.WECOM:
                markdown = {"content": text}

        result["markdown"] = markdown
        return result

    def send(self, data: dict) -> None:
        """发送webhook消息

        Args:
            data:dict,Webhook消息,可用类的text,markdown等方法构造
        """
        url = self.url
        sk = self.sk

        match(self.webhook):
            case WebHookType.DINGTALK:
                # 钉钉的处理
                if sk:
                    sk_enc = sk.encode()
                    timestamp = str(round(time()*1000))
                    sign_str = f"{timestamp}\n{sk}"
                    sign_str_enc = sign_str.encode()
                    hmac_code = hmac_new(sk_enc, sign_str_enc,
                                         digestmod=sha256).digest()
                    sign = quote_plus(b64encode(hmac_code))
                    url = f"{url}&timestamp={timestamp}&sign={sign}"

        # 消息发送
        with session() as s:
            result = s.post(url, json=data)

        rsp = result.json()
        if rsp["errcode"] != 0:
            raise Exception(rsp["errmsg"])


if __name__ == "__main__":
    dt = WebHook(WebHookType.DINGTALK, "url", "sk")

    data = dt.text("钉钉测试内容", phone=["151****9832"])
    data = dt.link(title="百度", text="点我可以打开baidu的地址",
                   url="https://www.baidu.com")
    data = dt.markdown("# 这是markdown的内容", title="markdown文本")
    dt.send(data)

    wb = WebHook(WebHookType.WECOM, "url")
    data = wb.text("微信测试内容", phone=["@all"])
    data = wb.markdown("# 这是markdown的内容")
    wb.send(data)
