"""
"""

from wheezy.core.mail import Attachment, MailMessage, SMTPClient

mail = MailMessage(
    subject="Welcome to Python",
    content="Hello World!",
    from_addr="someone@dev.local",
    to_addrs=["master@dev.local"],
)
mail.attachments.append(Attachment(name="welcome.txt", content="Hello World!"))

client = SMTPClient()
client.send(mail)
