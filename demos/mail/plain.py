
"""
"""

from wheezy.core.mail import MailMessage
from wheezy.core.mail import SMTPClient


mail = MailMessage(
    subject='Welcome to Python',
    content='Hello World!',
    from_addr='someone@dev.local',
    to_addrs=['master@dev.local'])

client = SMTPClient()
client.send(mail)
