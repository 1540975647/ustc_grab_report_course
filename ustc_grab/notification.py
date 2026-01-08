import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Any, Optional
from .config import Config

class Mailer:
    """
    Handles email notifications for success, failure, and other events.
    """
    def __init__(self, config: Config):
        self.config = config
        self.settings = config.email_settings
        self.sender = self.settings.get("sender")
        self.receiver = self.settings.get("receiver")
        smtp_conf = self.settings.get("smtp", {})
        self.smtp_server = smtp_conf.get("server")
        self.auth_code = smtp_conf.get("auth_code")
        self.smtp_port = int(smtp_conf.get("port", 465))

    def _send(self, subject: str, html_content: str):
        msg = MIMEMultipart()
        msg['From'] = self.sender
        msg['To'] = self.receiver
        msg['Subject'] = subject
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))

        try:
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                print('Connecting to SMTP server...')
                server.login(self.sender, self.auth_code)
                print('login success...')
                server.send_message(msg)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Email sent successfully -> {self.receiver}")
        except smtplib.SMTPAuthenticationError as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Auth failed [{e.smtp_code}]: {e.smtp_error.decode()}")
        except smtplib.SMTPConnectError:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Connection failed: {self.smtp_server}:{self.smtp_port}")
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Error sending email: {type(e).__name__}: {e}")

    def send_success(self, report_item: Dict[str, Any]):
        """Sends an email when a course is successfully grabbed."""
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
        self._send(subject, html)

    def send_fail(self, post_result: str):
        """Sends an email when the session/cookie is invalid."""
        subject = "查询课程失败，cookie已过期"
        html = f"""
        <h2>查询课程失败</h2>
        <h2>cookie已过期</h2>
        <p><em>时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>
        <p>详细信息: {post_result}</p>
        """
        self._send(subject, html)

    def send_withdraw_success(self, report_item: Dict[str, Any]):
        """Sends an email when an excluded course is successfully withdrawn."""
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
        self._send(subject, html)

    def send_grade_notification(self, grade_info: Dict[str, Any]):
        """Sends an email when a new grade is found."""
        kcmc = grade_info.get("KCMC", "未知课程")
        cj = grade_info.get("CJ", "未知")  # Score
        jdz = grade_info.get("JDZ")  # GPA
        xf = grade_info.get("XF")    # Credit
        kclbmc = grade_info.get("KCLBMC", "") # Category
        
        # Determine pass/fail or extra display
        sfjg = grade_info.get("SFJG_DISPLAY", "")
        
        subject = f"新成绩发布：{kcmc} - {cj}"
        
        html = f"""
        <h2>新成绩通知</h2>
        <p><strong>课程名称：</strong>{kcmc}</p>
        <p><strong>成绩：</strong><span style="color: red; font-size: 1.2em;">{cj}</span></p>
        <p><strong>绩点：</strong>{jdz}</p>
        <p><strong>学分：</strong>{xf}</p>
        <p><strong>课程类别：</strong>{kclbmc}</p>
        <p><strong>是否及格：</strong>{sfjg}</p>
        <p><em>更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>
        <hr/>
        <p>原始数据摘要：</p>
        <pre>{kcmc} (代码: {grade_info.get('KCDM')})</pre>
        """
        self._send(subject, html)
