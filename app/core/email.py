import smtplib
from email.message import EmailMessage
from pathlib import Path

from app.core.config import settings


EMAIL_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates" / "emails"


def render_email_template(template_name: str, context: dict[str, str]) -> str:
      template_path = EMAIL_TEMPLATES_DIR / template_name
      html = template_path.read_text(encoding="utf-8")

      for key, value in context.items():
          html = html.replace(f"{{{{ {key} }}}}", value)

      return html


def send_email(
      *,
      to_email: str,
      subject: str,
      text_content: str,
      html_content: str | None = None,
  ) -> None:
      message = EmailMessage()
      message["Subject"] = subject
      message["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
      message["To"] = to_email

      message.set_content(text_content)

      if html_content is not None:
          message.add_alternative(html_content, subtype="html")

      with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
          smtp.starttls()
          smtp.login(settings.smtp_username, settings.smtp_password)
          smtp.send_message(message)


def send_password_reset_email(*, to_email: str, reset_token: str) -> None:
      reset_url = f"{settings.frontend_url}/reset-password?token={reset_token}"

      subject = "Reset your NexoScribe password"

      text_content = f"""
  You requested a password reset.

  Open this link to reset your password:
  {reset_url}

  If you did not request this, you can ignore this email.
  """.strip()

      html_content = render_email_template(
          "password_reset.html",
          {"reset_url": reset_url},
      )

      send_email(
          to_email=to_email,
          subject=subject,
          text_content=text_content,
          html_content=html_content,
      )
