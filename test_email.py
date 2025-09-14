import asyncio
from app.utils.email import email_service  # путь к твоему EmailService

async def test_email():
    result = await email_service.send_email(
        to_email="seferov.murad.98@gmail.com",  # сюда пришлёт письмо
        subject="Тестовая отправка",
        body="Привет! Это тестовое письмо.",
        is_html=False
    )
    print("Email sent:", result)

if __name__ == "__main__":
    asyncio.run(test_email())