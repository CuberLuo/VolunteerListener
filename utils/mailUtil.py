import smtplib
import ssl
import traceback
from email.mime.text import MIMEText
from email.utils import formataddr


def mail(content, sender, auth_code, receiver):
    ret = True
    try:
        # 使用ssl模块的context加载系统允许的证书，在登录时进行验证
        context = ssl.create_default_context()
        msg = MIMEText(content, 'plain', 'utf-8')
        msg['From'] = formataddr(("anonymous", sender))  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        msg['To'] = formataddr(("anonymous", receiver))  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['Subject'] = "志愿者报告"  # 邮件的主题，也可以说是标题

        # 网易邮箱smtp.163.com
        # QQ邮箱 smtp.qq.com
        server = smtplib.SMTP_SSL("smtp.163.com", 465, context=context)  # 启用SSL发邮件, 端口一般是465
        server.login(sender, auth_code)  # 括号中对应的是发件人邮箱账号、邮箱授权码
        server.sendmail(sender, receiver, msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()  # 关闭连接
    except Exception:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
        traceback.print_exc()
        ret = False
    return ret
