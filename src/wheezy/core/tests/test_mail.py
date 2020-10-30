""" Unit tests for ``wheezy.core.mail``.
"""

import unittest

from mock import ANY, patch


def b(s):
    return s.encode("ascii")


try:
    import sys

    # [email.utils.formatdate] TypeError: unsupported operand type(s)
    # for +: 'NoneType' and 'int'
    # https://foss.heptapod.net/pypy/pypy/-/issues/3279
    sys.pypy_version_info
    PYPY = True  # pragma: nocover
except AttributeError:  # pragma: nocover
    PYPY = False


class MiscTestCase(unittest.TestCase):
    def setUp(self):
        self.patcher = patch("wheezy.core.mail.open", create=True)
        self.mock_open = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_recipients(self):
        """Ensure list is unique."""
        from wheezy.core.mail import MailMessage

        m = MailMessage(
            from_addr="f",
            to_addrs=["a", "b"],
            cc_addrs=["b", "c"],
            bcc_addrs=["c", "d"],
            reply_to_addrs=["e", "f"],
        )
        assert ["a", "b", "c", "d"] == sorted(m.recipients())

    def test_attachment_from_file(self):
        """Ensure attachment can be created from file."""
        from wheezy.core.mail import Attachment

        self.mock_open.return_value.read.return_value = "hello"
        a = Attachment.from_file("data/welcome.txt")
        self.mock_open.assert_called_once_with("data/welcome.txt", "rb")
        self.mock_open.return_value.read.assert_called_once_with()
        self.mock_open.return_value.close.assert_called_once_with()
        assert "welcome.txt" == a.name
        assert "hello" == a.content

    def test_alternative(self):
        """Alternative default content type."""
        from wheezy.core.mail import Alternative

        a = Alternative("content")
        assert "text/html" == a.content_type

    @patch("wheezy.core.mail.guess_type")
    def test_related_from_file(self, mock_guess_type):
        """Ensure related can be created from file."""
        from wheezy.core.mail import Related

        mock_guess_type.return_value = ("text/css", None)
        self.mock_open.return_value.read.return_value = "a {}"
        r = Related.from_file("css/style.css")
        self.mock_open.assert_called_once_with("css/style.css", "rb")
        self.mock_open.return_value.read.assert_called_once_with()
        self.mock_open.return_value.close.assert_called_once_with()
        assert "style.css" == r.content_id
        assert "text/css" == r.content_type
        assert "a {}" == r.content

    @patch("wheezy.core.mail.guess_type")
    def test_related_from_file_unknown_type(self, mock_guess_type):
        """Ensure default content type if its unknown."""
        from wheezy.core.mail import Related

        mock_guess_type.return_value = (None, None)
        r = Related.from_file("css/style.css")
        self.mock_open.assert_called_once_with("css/style.css", "rb")
        assert "application/octet-stream" == r.content_type


class MailAddressTestCase(unittest.TestCase):
    def test_mail_and_name(self):
        """Name or mail are ascii valid."""
        from wheezy.core.mail import mail_address

        assert "someone@dev.local" == mail_address("someone@dev.local")
        assert "Someone <someone@dev.local>" == mail_address(
            "someone@dev.local", "Someone"
        )
        assert (
            "=?utf-8?b?0L/RgNC40LLQtdGC?= <x@dev.local>"
            == mail_address(
                "x@dev.local",
                b("\\u043f\\u0440\\u0438\\u0432\\u0435\\u0442").decode(
                    "unicode_escape"
                ),
            ).replace("utf8", "utf-8")
        )

    def test_idna(self):
        """IDNA mail"""
        from wheezy.core.mail import mail_address

        mail = b(
            "\\u043f\\u0440\\u0438\\u0432\\u0435\\u0442@dev.local"
        ).decode("unicode_escape")
        assert "xn--b1agh1afp@dev.local" == mail_address(mail)
        assert (
            "=?utf-8?b?0L/RgNC40LLQtdGC?= " + "<xn--b1agh1afp@dev.local>"
        ) == mail_address(
            mail,
            b("\\u043f\\u0440\\u0438\\u0432\\u0435\\u0442").decode(
                "unicode_escape"
            ),
        ).replace(
            "utf8", "utf-8"
        )
        mail = b(
            "x@\\u043f\\u043e\\u0447\\u0442\\u0430.\\u0440\\u0443"
        ).decode("unicode_escape")
        assert "x@xn--80a1acny.xn--p1ag" == mail_address(mail)
        mail = b(
            "\\u043f\\u0440\\u0438\\u0432\\u0435\\u0442@"
            "\\u043f\\u043e\\u0447\\u0442\\u0430."
            "\\u0440\\u0443"
        ).decode("unicode_escape")
        assert "xn--b1agh1afp@xn--80a1acny.xn--p1ag" == mail_address(mail)


class SMTPClientTestCase(unittest.TestCase):
    def setUp(self):
        self.patcher = patch("wheezy.core.mail.SMTP")
        self.mock_smtp = self.patcher.start().return_value

    def tearDown(self):
        self.patcher.stop()

    @unittest.skipIf(PYPY, "issue #3279")
    def test_connect(self):
        """Ensure connected to right host and port"""
        from wheezy.core.mail import MailMessage, SMTPClient

        client = SMTPClient("mail.dev.local", 125)
        client.send(MailMessage())
        self.mock_smtp.connect.assert_called_once_with("mail.dev.local", 125)
        assert not self.mock_smtp.starttls.called
        assert not self.mock_smtp.login.called
        self.mock_smtp.quit.assert_called_once_with()

    @unittest.skipIf(PYPY, "issue #3279")
    def test_use_tls(self):
        """Ensure start tls command is issued."""
        from wheezy.core.mail import MailMessage, SMTPClient

        client = SMTPClient(use_tls=True)
        client.send(MailMessage())
        self.mock_smtp.starttls.assert_called_once_with()
        assert not self.mock_smtp.login.called

    @unittest.skipIf(PYPY, "issue #3279")
    def test_login(self):
        """Ensure credentials are used."""
        from wheezy.core.mail import MailMessage, SMTPClient

        client = SMTPClient(username="user", password="pass")
        client.send(MailMessage())
        self.mock_smtp.login.assert_called_once_with("user", "pass")

    @unittest.skipIf(PYPY, "issue #3279")
    def test_send(self):
        """Ensure from and to lists are valid in sending a single message."""
        from wheezy.core.mail import MailMessage, SMTPClient

        client = SMTPClient(username="user", password="pass")
        message = MailMessage(
            from_addr="one@dev.local", to_addrs=["two@dev.local"]
        )
        client.send(message)
        self.mock_smtp.sendmail.assert_called_once_with(
            message.from_addr, message.recipients(), ANY
        )

    @unittest.skipIf(PYPY, "issue #3279")
    def test_send_multi(self):
        """Ensure from and to lists are valid in sending multiple messages."""
        from mock import call

        from wheezy.core.mail import MailMessage, SMTPClient

        client = SMTPClient(username="user", password="pass")
        message1 = MailMessage(
            from_addr="one@dev.local", to_addrs=["two@dev.local"]
        )
        message2 = MailMessage(
            from_addr="three@dev.local", to_addrs=["four@dev.local"]
        )
        client.send_multi([message1, message2])
        assert 2 == self.mock_smtp.sendmail.call_count
        assert self.mock_smtp.sendmail.mock_calls == [
            call(message1.from_addr, message1.recipients(), ANY),
            call(message2.from_addr, message2.recipients(), ANY),
        ]


class MIMETestCase(unittest.TestCase):
    @patch("wheezy.core.mail.formatdate")
    def test_required_headers(self, mock_formatdate):
        """Ensure mail message information is included."""
        from wheezy.core.mail import MailMessage, mime

        mock_formatdate.return_value = "x"
        message = MailMessage(
            subject="s",
            content="c",
            charset="utf-8",
            from_addr="z",
            to_addrs=["a", "b"],
            cc_addrs=["c", "d"],
            bcc_addrs=["e", "f"],
            reply_to_addrs=["x", "y"],
        )
        message.date = 1354555373
        m = mime(message)
        assert m["Message-ID"]
        assert 'text/plain; charset="utf-8"' == m["Content-Type"]
        assert message.subject == m["Subject"]
        assert "c" == m.get_payload()
        mock_formatdate.assert_called_once_with(message.date, localtime=True)
        assert "x" == m["Date"]
        assert message.from_addr == m["From"]
        assert "a, b" == m["To"]
        assert "c, d" == m["Cc"]
        assert "e, f" == m["Bcc"]
        assert "x, y" == m["Reply-To"]

    @unittest.skipIf(PYPY, "issue #3279")
    def test_alternative(self):
        """Ensure alternative includes both plain and html."""
        from wheezy.core.mail import Alternative, MailMessage, mime

        message = MailMessage(content="c")
        a = Alternative("a")
        message.alternatives.append(a)
        m = mime(message)
        assert "multipart/alternative" == m["Content-Type"]
        subparts = m.get_payload()
        assert 2 == len(subparts)
        assert "c" == subparts[0].get_payload()
        assert "a" == subparts[1].get_payload()

    @unittest.skipIf(PYPY, "issue #3279")
    def test_alternative_no_plain(self):
        """Ensure if alternative available by plain is empty
        only one included.
        """
        from wheezy.core.mail import Alternative, MailMessage, mime

        message = MailMessage()
        a = Alternative("a")
        message.alternatives.append(a)
        m = mime(message)
        assert "text/html" == m["Content-Type"]
        assert "a" == m.get_payload()

    @unittest.skipIf(PYPY, "issue #3279")
    def test_attachment(self):
        """Ensure attachments added."""
        from wheezy.core.mail import Attachment, MailMessage, mime

        message = MailMessage(content="c")
        a = Attachment("1.txt", "a")
        message.attachments.append(a)
        m = mime(message)
        assert "multipart/mixed" == m["Content-Type"]
        subparts = m.get_payload()
        assert 2 == len(subparts)
        assert "c" == subparts[0].get_payload()
        assert "a" == subparts[1].get_payload()

    @unittest.skipIf(PYPY, "issue #3279")
    def test_everything(self):
        """Add plain, alternate and attachment."""
        from wheezy.core.mail import Alternative, Attachment, MailMessage, mime

        message = MailMessage(content="c")
        a = Alternative("al")
        message.alternatives.append(a)
        a = Attachment("1.txt", "at")
        message.attachments.append(a)
        m = mime(message)
        assert "multipart/mixed" == m["Content-Type"]
        subparts = m.get_payload()
        assert 2 == len(subparts)
        assert "at" == subparts[1].get_payload()
        subparts = subparts[0].get_payload()
        assert "c" == subparts[0].get_payload()
        assert "al" == subparts[1].get_payload()


class MimeHeaderTestCase(unittest.TestCase):
    def test_ascii(self):
        """Value is ascii valid."""
        from wheezy.core.mail import mime_header

        assert "x" == mime_header("x", "ascii")

    def test_encode(self):
        """Value is not ascii valid."""
        from wheezy.core.mail import mime_header

        value = b("\\u043f\\u0440\\u0438\\u0432\\u0435\\u0442").decode(
            "unicode_escape"
        )
        assert "=?utf-8?b?0L/RgNC40LLQtdGC?=" == mime_header(value, "utf-8")


class MIMEPartsTestCase(unittest.TestCase):
    def test_part(self):
        """Ensure base64 encoding for non text content."""
        from wheezy.core.mail import mime_part

        m = mime_part("content", "text/plain")
        assert "text/plain" == m["Content-Type"]
        assert "content" == m.get_payload()
        m = mime_part(b("content"), "image/gif")
        assert "Y29udGVudA==" == m.get_payload().rstrip("\n")

    def test_multipart(self):
        """Ensure subparts."""
        from wheezy.core.mail import mime_multipart

        subparts = ["a"]
        m = mime_multipart("multipart/mixed", subparts)
        assert "multipart/mixed" == m["Content-Type"]
        assert subparts == m.get_payload()

    @patch("wheezy.core.mail.mime_part")
    def test_alternative(self, mock_mime_part):
        """Ensure alternative is built."""
        from wheezy.core.mail import Alternative, mime_alternative

        mock_mime_part.return_value = "x"
        a = Alternative("content", "ct", "cs")
        assert "x" == mime_alternative(a)
        mock_mime_part.assert_called_once_with("content", "ct", "cs")

    def test_related(self):
        """Ensure related is built."""
        from wheezy.core.mail import Alternative, Related, mime_alternative

        a = Alternative("content", "text/html", "utf-8")
        a.related.append(Related("cid", b("rc"), "image/gif"))
        m = mime_alternative(a)
        assert "multipart/related" == m["Content-Type"]
        subparts = m.get_payload()
        assert 2 == len(subparts)
        m = subparts[0]
        assert 'text/html; charset="utf-8"' == m["Content-Type"]
        assert "content" == m.get_payload()
        m = subparts[1]
        assert "cid" == m["Content-ID"]
        assert "image/gif" == m["Content-Type"]
        assert "cmM=" == m.get_payload().rstrip("\n")

    def test_attachment(self):
        """Ensure attachment is built."""
        from wheezy.core.mail import Attachment, mime_attachment

        a = Attachment("1.txt", "c", "text/plain")
        m = mime_attachment(a)
        assert "text/plain" == m["Content-Type"]
        assert 'attachment; filename="1.txt"' == m["Content-Disposition"]
        a = Attachment("1.txt", "c", "text/plain", disposition="inline")
        m = mime_attachment(a)
        assert 'inline; filename="1.txt"' == m["Content-Disposition"]
        a = Attachment("1.txt", "c", "text/plain", content_charset="utf-8")
        m = mime_attachment(a)
        assert 'text/plain; charset="utf-8"' == m["Content-Type"]
        a = Attachment("1.txt", "c", "text/plain", name_charset="utf-8")
        m = mime_attachment(a)
        assert "attachment; filename*=utf-8''1.txt" == m["Content-Disposition"]
        a = Attachment("1", b("c"))
        m = mime_attachment(a)
        assert "application/octet-stream" == m["Content-Type"]
