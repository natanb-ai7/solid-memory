from loguru import logger


def send_email(to_email: str, subject: str, body: str) -> None:
    # Placeholder: integrate SMTP or a provider like SES/SendGrid in production.
    logger.info("Email alert to %s: %s", to_email, subject)
    logger.debug(body)
