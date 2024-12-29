from ..mailer import mail,create_message
from fastapi import APIRouter
from ..schemas import EmailModel

router=APIRouter(
    prefix="/email",
    tags=['email']
)

@router.post("/send-mail")
async def send_mail(emails:EmailModel):
    emails = emails.addresses

    html = "<h1>Welcome to the app</h1>"
    subject = "Welcome to our app"

    message = create_message(recipients=emails, subject=subject, body=html)
    await mail.send_message(message)

    return {"message": "Email sent successfully"}

