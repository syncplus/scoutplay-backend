import logging

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType

from app.config import get_smtp_config, get_app_url

logger = logging.getLogger(__name__)


def _build_client() -> FastMail:
    smtp = get_smtp_config()
    conf = ConnectionConfig(
        MAIL_USERNAME=smtp["user"],
        MAIL_PASSWORD=smtp["password"],
        MAIL_FROM=smtp["from"],
        MAIL_PORT=smtp["port"],
        MAIL_SERVER=smtp["host"],
        MAIL_STARTTLS=smtp["starttls"],
        MAIL_SSL_TLS=not smtp["starttls"],
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True,
    )
    return FastMail(conf)


async def send_password_reset_email(to_email: str, name: str, token: str) -> None:
    app_url = (get_app_url() or "http://localhost:3000").rstrip("/")
    reset_url = f"{app_url}/reset-password?token={token}"

    if not get_smtp_config()["user"]:
        logger.warning("SMTP não configurado. Use este link para resetar: %s", reset_url)
        return

    body = f"""
    <div style="font-family:sans-serif;max-width:480px;margin:auto">
        <h2>Redefinição de senha</h2>
        <p>Olá, <strong>{name}</strong>!</p>
        <p>Recebemos uma solicitação para redefinir a senha da sua conta no ScoutPlay.</p>
        <p>
            <a href="{reset_url}"
               style="display:inline-block;padding:12px 24px;background:#1a73e8;
                      color:#fff;border-radius:6px;text-decoration:none;font-weight:bold">
                Redefinir minha senha
            </a>
        </p>
        <p>O link expira em <strong>1 hora</strong>.</p>
        <p style="color:#888;font-size:13px">
            Se você não solicitou isso, ignore este e-mail — sua senha permanece inalterada.
        </p>
    </div>
    """

    message = MessageSchema(
        subject="Redefinição de senha — ScoutPlay",
        recipients=[to_email],
        body=body,
        subtype=MessageType.html,
    )
    await _build_client().send_message(message)
