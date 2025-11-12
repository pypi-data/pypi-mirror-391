"""
Email Notification Module

Sends email notifications for contract updates.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional, Dict, Any
from rich.console import Console


console = Console()


class EmailNotifier:
    """Email notification sender"""

    def __init__(self, smtp_config: Dict[str, Any]):
        """
        Initialize email notifier.

        Args:
            smtp_config: SMTP configuration
                {
                    'host': 'smtp.example.com',
                    'port': 587,
                    'user': 'user@example.com',
                    'password': '${SMTP_PASSWORD}',  # or actual password
                    'from': 'noreply@example.com'
                }
        """
        self.host = smtp_config.get('host')
        self.port = smtp_config.get('port', 587)
        self.user = smtp_config.get('user')
        self.from_email = smtp_config.get('from') or smtp_config.get('user')

        # Get password from config or environment variable
        password = smtp_config.get('password', '')
        if password.startswith('${') and password.endswith('}'):
            # Extract environment variable name
            env_var = password[2:-1]
            self.password = os.environ.get(env_var, '')
        else:
            self.password = password

    def send_contract_update_notification(
        self,
        feature_name: str,
        contract_url: str,
        recipients: List[str],
        commit_hash: Optional[str] = None,
        dev_team: Optional[List[str]] = None,
        custom_message: Optional[str] = None
    ) -> bool:
        """
        Send contract update notification.

        Args:
            feature_name: Feature name
            contract_url: Contract repository URL or path
            recipients: Email recipients
            commit_hash: Git commit hash (optional)
            dev_team: Development team members (optional)
            custom_message: Custom message (optional)

        Returns:
            True if sent successfully, False otherwise
        """
        if not recipients:
            console.print("[yellow]⚠️  无收件人，跳过邮件通知[/yellow]")
            return False

        console.print(f"\n[cyan]📧 发送邮件通知...[/cyan]")
        console.print(f"[dim]收件人: {', '.join(recipients)}[/dim]\n")

        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'[AceFlow] 契约更新通知 - {feature_name}'
        msg['From'] = self.from_email
        msg['To'] = ', '.join(recipients)

        # Create email body
        text_body = self._create_text_body(
            feature_name, contract_url, commit_hash, dev_team, custom_message
        )
        html_body = self._create_html_body(
            feature_name, contract_url, commit_hash, dev_team, custom_message
        )

        # Attach both plain text and HTML versions
        part1 = MIMEText(text_body, 'plain', 'utf-8')
        part2 = MIMEText(html_body, 'html', 'utf-8')
        msg.attach(part1)
        msg.attach(part2)

        # Send email
        try:
            with smtplib.SMTP(self.host, self.port, timeout=30) as server:
                server.starttls()
                server.login(self.user, self.password)
                server.send_message(msg)

            console.print(f"[green]✅ 邮件发送成功！[/green]\n")
            return True

        except smtplib.SMTPAuthenticationError:
            console.print("[red]❌ SMTP 认证失败，请检查用户名和密码[/red]\n")
            return False

        except smtplib.SMTPException as e:
            console.print(f"[red]❌ SMTP 错误: {e}[/red]\n")
            return False

        except Exception as e:
            console.print(f"[red]❌ 发送失败: {e}[/red]\n")
            return False

    def _create_text_body(
        self,
        feature_name: str,
        contract_url: str,
        commit_hash: Optional[str],
        dev_team: Optional[List[str]],
        custom_message: Optional[str]
    ) -> str:
        """Create plain text email body"""
        body = f"""
契约更新通知
================

需求: {feature_name}
"""
        if dev_team:
            body += f"开发团队: {', '.join(dev_team)}\n"

        body += f"""
契约仓库: {contract_url}
"""

        if commit_hash:
            body += f"提交版本: {commit_hash}\n"

        body += """
下一步操作:
1. 前端开发者: 拉取最新契约文件
2. 前端开发者: 使用 Mock Server 进行开发
3. 后端开发者: 按照契约实现接口

"""

        if custom_message:
            body += f"""
备注:
{custom_message}

"""

        body += """
---
此邮件由 AceFlow 自动发送
"""
        return body

    def _create_html_body(
        self,
        feature_name: str,
        contract_url: str,
        commit_hash: Optional[str],
        dev_team: Optional[List[str]],
        custom_message: Optional[str]
    ) -> str:
        """Create HTML email body"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background-color: #4CAF50;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 5px 5px 0 0;
        }}
        .content {{
            background-color: #f9f9f9;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 0 0 5px 5px;
        }}
        .info-box {{
            background-color: white;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #4CAF50;
        }}
        .label {{
            font-weight: bold;
            color: #555;
        }}
        .value {{
            color: #333;
        }}
        .next-steps {{
            background-color: #e3f2fd;
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
        }}
        .next-steps ol {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        .footer {{
            text-align: center;
            color: #888;
            font-size: 12px;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h2>📝 契约更新通知</h2>
    </div>
    <div class="content">
        <div class="info-box">
            <p><span class="label">需求:</span> <span class="value">{feature_name}</span></p>
"""
        if dev_team:
            html += f"""
            <p><span class="label">开发团队:</span> <span class="value">{', '.join(dev_team)}</span></p>
"""

        html += f"""
            <p><span class="label">契约仓库:</span> <span class="value">{contract_url}</span></p>
"""

        if commit_hash:
            html += f"""
            <p><span class="label">提交版本:</span> <span class="value">{commit_hash}</span></p>
"""

        html += """
        </div>

        <div class="next-steps">
            <h3>📋 下一步操作</h3>
            <ol>
                <li><strong>前端开发者:</strong> 拉取最新契约文件</li>
                <li><strong>前端开发者:</strong> 使用 Mock Server 进行开发</li>
                <li><strong>后端开发者:</strong> 按照契约实现接口</li>
            </ol>
        </div>
"""

        if custom_message:
            html += f"""
        <div class="info-box">
            <p><span class="label">备注:</span></p>
            <p class="value">{custom_message}</p>
        </div>
"""

        html += """
    </div>
    <div class="footer">
        <p>此邮件由 AceFlow 自动发送</p>
    </div>
</body>
</html>
"""
        return html

    def test_connection(self) -> bool:
        """
        Test SMTP connection.

        Returns:
            True if connection successful, False otherwise
        """
        console.print(f"\n[cyan]🔌 测试 SMTP 连接...[/cyan]")
        console.print(f"[dim]服务器: {self.host}:{self.port}[/dim]")
        console.print(f"[dim]用户: {self.user}[/dim]\n")

        try:
            with smtplib.SMTP(self.host, self.port, timeout=10) as server:
                server.starttls()
                server.login(self.user, self.password)

            console.print(f"[green]✅ 连接成功！[/green]\n")
            return True

        except smtplib.SMTPAuthenticationError:
            console.print("[red]❌ 认证失败，请检查用户名和密码[/red]\n")
            return False

        except Exception as e:
            console.print(f"[red]❌ 连接失败: {e}[/red]\n")
            return False
