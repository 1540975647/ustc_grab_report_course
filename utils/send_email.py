#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# utils/send_email.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from settings import email_settings

# 邮件配置属性
email_sender: str = email_settings.get("sender")
email_receiver: str = email_settings.get("receiver")
smtp_server: str = email_settings.get("smtp").get("server")
email_auth_code: str = email_settings.get("smtp").get("auth_code")
smtp_port: int = int(email_settings.get("smtp").get("port"))


def build_email_and_send(subject: str, html: str):
    msg = MIMEMultipart()
    msg['From'] = email_sender
    msg['To'] = email_receiver
    msg['Subject'] = subject
    msg.attach(MIMEText(html, 'html', 'utf-8'))

    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            print('Connecting to SMTP server...')
            # print(smtp_port, smtp_server)
            # print(email_sender)
            server.login(email_sender, email_auth_code)
            print('login success...')
            server.send_message(msg)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 邮件发送成功 → {email_receiver}")
    except smtplib.SMTPAuthenticationError as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 认证失败 [{e.smtp_code}]: {e.smtp_error.decode()}")
    except smtplib.SMTPConnectError:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 连接失败：无法连接到 {smtp_server}:{smtp_port}")
    except smtplib.SMTPServerDisconnected:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 服务器意外断开（可能端口/加密错误）")
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 其他错误: {type(e).__name__}: {e}")


def send_success_email(report_item: dict):
    # 发送选课成功邮件（HTML 格式）
    subject = "选课成功！报告已锁定"
    bgtmzw = report_item.get("BGTMZW", "未知")
    bgsj = report_item.get("BGSJ", "未知")
    dd = report_item.get("DD", "未知")
    bgbm = report_item.get("BGBM", "未知")
    yxdm_display = report_item.get("YXDM_DISPLAY", "未知")

    html = f"""
    <h2>恭喜！选课成功</h2>
    <p><strong>报告主题：</strong>{bgtmzw}</p>
    <p><strong>开课院系：</strong>{yxdm_display}</p>
    <p><strong>报告地点：</strong>{dd}</p>
    <p><strong>报告时间：</strong>{bgsj}</p>
    <p><strong>课程代码：</strong>{bgbm}</p>
    <p><em>时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>
    """
    build_email_and_send(subject, html)


def send_fail_email(post_result: str):
    # 发送查询课程失败邮件（HTML 格式）
    subject = "查询课程失败，cookie已过期"
    html = f"""
        <h2>查询课程失败</h2>
        <h2>cookie已过期</h2>
        <p><em>时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>
        """
    build_email_and_send(subject, html)


def send_withdraw_exclude_course_success(report_item: dict):
    # 发送退课成功邮件（HTML 格式）
    subject = "退课成功！查询到已选择排除的课程，已经退课"

    bgtmzw = report_item.get("BGTMZW", "未知")
    bgsj = report_item.get("BGSJ", "未知")
    dd = report_item.get("DD", "未知")
    bgbm = report_item.get("BGBM", "未知")
    yxdm_display = report_item.get("YXDM_DISPLAY", "未知")

    html = f"""
        <h2>恭喜！退课成功</h2>
        <p><strong>报告主题：</strong>{bgtmzw}</p>
        <p><strong>开课院系：</strong>{yxdm_display}</p>
        <p><strong>报告地点：</strong>{dd}</p>
        <p><strong>报告时间：</strong>{bgsj}</p>
        <p><strong>课程代码：</strong>{bgbm}</p>
        <p><em>时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>
        """
    build_email_and_send(subject, html)

if __name__ == '__main__':
    print("sending email...")
