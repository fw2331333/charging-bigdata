"""SMTP 发信（同步 smtplib 在线程池中执行）。"""

import asyncio
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr, parseaddr

from app.core.config import settings
from app.models.email_verification import PURPOSE_RESET_PASSWORD

logger = logging.getLogger(__name__)


def _envelope_from() -> str:
    _, addr = parseaddr(settings.SMTP_FROM)
    return addr or settings.SMTP_USER


def _send_smtp_sync(to_email: str, subject: str, html_body: str, text_body: str) -> None:
    envelope = _envelope_from()
    _, from_addr = parseaddr(settings.SMTP_FROM)
    display = settings.SMTP_FROM.split("<", 1)[0].strip().strip('"') if "<" in settings.SMTP_FROM else "Charging Big Data"
    if not from_addr:
        from_addr = settings.SMTP_USER

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = formataddr((display or "Charging Big Data", from_addr))
    msg["To"] = to_email
    msg.attach(MIMEText(text_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    if settings.SMTP_PORT == 465:
        server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=30)
    else:
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=30)
    with server:
        if settings.SMTP_PORT != 465 and settings.SMTP_USE_TLS:
            server.starttls()
        if settings.SMTP_USER:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(envelope, [to_email], msg.as_string())


def send_set_password_email_sync(to_email: str, action_url: str, purpose: str) -> bool:
    if purpose == PURPOSE_RESET_PASSWORD:
        subject = "重置充电大数据平台密码"
        title = "重置密码"
        intro = "你申请了重置密码。请打开下方链接设置新密码："
        button = "设置新密码"
    else:
        subject = "完成充电大数据平台注册"
        title = "完成注册"
        intro = "欢迎注册 <strong>新能源充电桩大数据分析系统</strong>。请打开下方链接设置登录密码并完成验证："
        button = "设置密码并验证"

    qq_tip = "QQ 邮箱若无法点击按钮，请复制下方整段链接到 Chrome / Edge 地址栏打开。"
    text_body = (
        f"{title}\n\n{intro.replace('<strong>', '').replace('</strong>', '')}\n"
        f"{action_url}\n\n{qq_tip}\n\n"
        f"链接 {settings.EMAIL_VERIFY_EXPIRE_HOURS} 小时内有效。如非本人操作请忽略。"
    )
    html_body = f"""
    <div style="font-family:sans-serif;line-height:1.6;color:#374151;max-width:480px">
      <h2 style="color:#1f2937">{title}</h2>
      <p>{intro}</p>
      <p><a href="{action_url}"
         style="display:inline-block;padding:12px 24px;background:#2d6a9f;color:#fff;
         text-decoration:none;border-radius:8px">{button}</a></p>
      <p style="font-size:13px;color:#6b7280">或复制链接：<br>
        <span style="word-break:break-all">{action_url}</span></p>
      <p style="font-size:12px;color:#b45309;background:#fffbeb;padding:8px;border-radius:6px">{qq_tip}</p>
      <p style="font-size:12px;color:#9ca3af">链接 {settings.EMAIL_VERIFY_EXPIRE_HOURS} 小时内有效。</p>
    </div>
    """

    if not settings.smtp_configured:
        logger.warning("[email] SMTP 未配置，邮件未发送 to=%s purpose=%s", to_email, purpose)
        return False

    try:
        _send_smtp_sync(to_email, subject, html_body, text_body)
        logger.info("[email] 已发送至 %s purpose=%s", to_email, purpose)
        return True
    except Exception:
        logger.exception("[email] 发送失败: %s", to_email)
        return False


async def send_set_password_email(to_email: str, action_url: str, purpose: str) -> bool:
    return await asyncio.to_thread(send_set_password_email_sync, to_email, action_url, purpose)


def send_profile_otp_email_sync(to_email: str, code: str) -> bool:
    subject = "充电大数据平台 · 安全验证码"
    text_body = (
        f"你的验证码是：{code}\n\n"
        f"用于修改登录密码，{settings.PROFILE_OTP_EXPIRE_MINUTES} 分钟内有效。\n"
        f"如非本人操作请忽略此邮件。"
    )
    html_body = f"""
    <div style="font-family:sans-serif;line-height:1.6;color:#374151;max-width:480px">
      <h2 style="color:#1f2937">安全验证码</h2>
      <p>你正在修改登录密码，验证码为：</p>
      <p style="font-size:28px;font-weight:700;letter-spacing:6px;color:#2d6a9f">{code}</p>
      <p style="font-size:13px;color:#6b7280">
        {settings.PROFILE_OTP_EXPIRE_MINUTES} 分钟内有效。如非本人操作请忽略。</p>
    </div>
    """
    if not settings.smtp_configured:
        logger.warning("[email] SMTP 未配置，验证码邮件未发送 to=%s", to_email)
        return False
    try:
        _send_smtp_sync(to_email, subject, html_body, text_body)
        return True
    except Exception:
        logger.exception("[email] 验证码发送失败: %s", to_email)
        return False
