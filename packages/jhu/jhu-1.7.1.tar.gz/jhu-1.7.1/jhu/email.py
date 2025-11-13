"""
作者:J.Hu
日期:2023-12-19
内容:
# 功能描述：
 - 支持邮件发送
# 重要版本变更说明：
 - 更新附件的代码编写,使其支持正常的文字显示;
 - To/Cc/Bcc的列表拼接采用逗号的形式拼接,原因是原来采用多个To/Cc/Bcc会导致
   在某些邮件客户端上只显示一个To/Cc/Bcc内容.
   比如,Header里面内容如:
   To:=?utf-8?b?6IOh5YGl?= <huj@citytsm.com>
   To:=?utf-8?b?6IOh5YGl?= <huj@citytsm.com>
   这样只会显示一个huj,
   现在修改变成：
   To:=?utf-8?b?6IOh5YGl?= <huj@citytsm.com>,=?utf-8?b?6IOh5YGl?= <huj@citytsm.com>
   这样就可以显示出2个huj,huj了
"""
from smtplib import SMTP, SMTP_SSL
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from email.header import Header


class EmailSender:
    def __init__(self, host: str, port: int = 465, ssl: bool = True, timeout: int = 10, encode: str = "utf-8", mail_type: str = "html", attach_type: str = "base64") -> None:
        """Email对象

        Args:
            host:str,STMP的服务器地址
            port:int,STMP的端口号,默认465
            ssl:bool,是否使用ssl,默认true
            timeout:int,服务器连接超时(秒)
            encode:str,邮件编码,默认为utf-8
            mail_type:str,邮件正文类型,默认为html
            attch_type:str,邮件附件类型,默认为base64
        """
        # 根据SSL确定SMTP的类型
        smtpfunc = SMTP_SSL if ssl else SMTP
        self.__smtp = smtpfunc(host, port, timeout=timeout)

        self.encode = encode
        self.mail_type = mail_type
        self.attach_type = attach_type

        # 初始化to,cc,bcc对象

    @property
    def smtp(self):
        return self.__smtp

    @property
    def sender(self):
        return self.__sender

    def login(self, acct: str, passwd: str, nickname: str | None = None) -> None:
        """登录SMTP服务器

        Args:
            acct:str,账号,比如:joestarhu@163.com
            passwd:str,密码
            nickname:str,昵称
        """
        self.smtp.login(acct, passwd)
        if not nickname:
            nickname = acct
        self.__sender = formataddr([nickname, acct], self.encode)
        self.acct = acct

    def send(self, title: str, content: str, attach_list: list[str] = [], to: list[str] | None = None, cc: list[str] | None = None, bcc: list[str] | None = None) -> None:
        """发送邮件

        Args:
            title:str,邮件正文标题
            content:str,邮件正文内容
            attach_list:list,邮件附件列表, ['/user/a.zip','/user/b.zip']
            to:list,收件人列表,['a@a.com','b@b.com']
            cc:list,cc列表,['a@a.com','b@b.com']
            bcc:list,bcc列表,['a@a.com','b@b.com']
        """
        mime = MIMEMultipart()

        # 设置邮件标题和发件人
        mime["Subject"] = Header(title, self.encode)
        mime["From"] = self.sender

        # 设置收件人信息 to,cc,bcc
        receive_lst = []
        rcpt_to = dict(label="To", value=to)
        rcpt_cc = dict(label="Cc", value=cc)
        rcpt_bcc = dict(label="Bcc", value=bcc)

        for val in [rcpt_to, rcpt_cc, rcpt_bcc]:
            # 没有设置相关的收件人信息
            rcpt_type = val["label"]
            rcpt_value = val["value"]

            if not rcpt_value:
                continue
            receive_lst.extend(rcpt_value)
            mime[rcpt_type] = ','.join(
                [formataddr([None, mail], self.encode) for mail in rcpt_value])

        # 正文内容设置
        mime.attach(MIMEText(content, self.mail_type, self.encode))

        # 附件内容设置
        for idx, val in enumerate(attach_list):
            att = MIMEText(open(val, "rb").read(), self.mail_type, self.encode)
            att.add_header("Content-ID", str(idx))
            att.add_header("Content-Type", "application/octet-stream")
            att_name = val.split('/')[-1]
            att.add_header("Content-Disposition", "attachment",
                           filename=(self.encode, '', att_name))
            mime.attach(att)

        # 发送邮件
        self.smtp.sendmail(self.acct, receive_lst, mime.as_string())

    def close(self):
        """关闭smtp链接
        """
        self.smtp.close()


if __name__ == "__main__":
    host = "host"
    e = EmailSender(host)
    acct = "a@a.com"
    passwd = "passwd"
    nickname = "joestarhu"
    e.login(acct, passwd, nickname)
    e.send(title="title", content="content", to=["a@a.com", "b@b.com"])
