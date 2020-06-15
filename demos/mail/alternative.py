"""
"""

import os.path

from wheezy.core.mail import Alternative, MailMessage, Related, SMTPClient

mail = MailMessage(
    subject="Welcome to Python",
    content="Hello World!",
    from_addr="someone@dev.local",
    to_addrs=["master@dev.local"],
)

alt = Alternative(
    """\
<html><body>
    <h1>Hello World!</h1>
    <p><img src="cid:python-logo.gif" /></p>
</body></html>""",
    content_type="text/html",
)

curdir = os.path.dirname(__file__)
path = os.path.join(curdir, "python-logo.gif")
alt.related.append(Related.from_file(path))

mail.alternatives.append(alt)

client = SMTPClient()
client.send(mail)
