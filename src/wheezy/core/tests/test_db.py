
""" Unit tests for ``wheezy.core.db.session``.
"""

import unittest

from mock import Mock


class SessionTestCase(unittest.TestCase):

    def setUp(self):
        from wheezy.core.db import Session
        self.mock_pool = Mock()
        self.session = Session(self.mock_pool)

    def test_enter(self):
        """ Enter returns session instance.
        """
        assert self.session == self.session.__enter__()

    def test_connection_raise_error(self):
        """ If not entered raise error.
        """
        self.assertRaises(AssertionError, lambda: self.session.connection)

    def test_connection(self):
        """ Ensure same connection is returned each time.
        """
        mock_connection = Mock()
        self.mock_pool.acquire.return_value = mock_connection
        self.session.__enter__()
        assert mock_connection == self.session.connection
        assert mock_connection == self.session.connection
        self.mock_pool.acquire.assert_called_once_with()

    def test_on_active(self):
        """ Ensure on_active is called once.
        """
        from wheezy.core.db import Session

        class MockSession(Session):
            pass
        mock_session = MockSession(self.mock_pool)
        mock_session.on_active = Mock()
        mock_connection = Mock()
        self.mock_pool.acquire.return_value = mock_connection
        mock_session.__enter__()
        assert mock_connection == mock_session.connection
        assert mock_connection == mock_session.connection
        mock_session.on_active.assert_called_once_with(mock_connection)

    def test_cursor(self):
        """ Ensure cursor is called with all args.
        """
        mock_connection = Mock()
        self.mock_pool.acquire.return_value = mock_connection
        self.session.__enter__()
        self.session.cursor(1, x=2)
        mock_connection.cursor.assert_called_once_with(1, x=2)
        mock_connection.cursor.reset_mock()
        self.session.cursor()
        mock_connection.cursor.assert_called_once_with()

    def test_commit_raise_error(self):
        """ If not entered raise error.
        """
        self.assertRaises(AssertionError, lambda: self.session.commit())

    def test_commit_on_unused(self):
        """ no connection commit is called.
        """
        self.session.__enter__()
        self.session.commit()
        assert not self.mock_pool.acquire.called
        assert not self.mock_pool.get_back.called

    def test_commit_connection_error(self):
        """ An error is raised on connection commit.
        """
        mock_connection = Mock()
        self.mock_pool.acquire.return_value = mock_connection
        self.session.__enter__()
        self.session.cursor()
        mock_connection.commit.side_effect = KeyError()
        self.assertRaises(KeyError, lambda: self.session.commit())

    def test_commit_cursor(self):
        """ Cursor is aquires new connection after commit.
        """
        mock_connection = Mock()
        self.mock_pool.acquire.return_value = mock_connection
        self.session.__enter__()
        self.session.cursor()
        self.session.commit()
        self.session.cursor()
        assert self.mock_pool.acquire.call_count == 2

    def test_exit_on_unused(self):
        """ Exit when connection was not used.
        """
        self.session.__enter__()
        assert not self.mock_pool.acquire.called
        self.session.__exit__(None, None, None)
        assert not self.mock_pool.get_back.called

    def test_exit_rollback(self):
        """ Exit when no commit called.
        """
        mock_connection = Mock()
        self.mock_pool.acquire.return_value = mock_connection
        self.session.__enter__()
        self.session.cursor()
        assert self.mock_pool.acquire.called
        self.session.__exit__(None, None, None)
        mock_connection.rollback.assert_called_once_with()
        self.mock_pool.get_back.assert_called_once_with(mock_connection)

    def test_exit_connection_error(self):
        """ Exit when an error raised during rollback
        """
        mock_connection = Mock()
        self.mock_pool.acquire.return_value = mock_connection
        self.session.__enter__()
        self.session.cursor()
        assert self.mock_pool.acquire.called
        mock_connection.rollback.side_effect = KeyError()
        self.assertRaises(KeyError,
                          lambda: self.session.__exit__(None, None, None))
        self.mock_pool.get_back.assert_called_once_with(mock_connection)


class TPCSessionTestCase(unittest.TestCase):

    def setUp(self):
        from wheezy.core.db import TPCSession
        self.mock_pool = Mock()
        self.session = TPCSession(self.mock_pool)

    def test_enter(self):
        """ Enter returns session instance.
        """
        assert self.session == self.session.__enter__()

    def test_enlist_raise_error(self):
        """ If not entered raise error.
        """
        self.assertRaises(AssertionError, lambda: self.session.enlist(None))

    def test_enlist(self):
        """ Starts TPC transaction on connection.
        """
        self.session.__enter__()
        session = Mock()
        session.__enter__ = Mock()
        session.connection.xid.return_value = 'xid'
        self.session.enlist(session)
        session.__enter__.assert_called_once_with()
        assert session.connection.xid.called
        session.connection.tpc_begin.assert_called_once_with('xid')

    def test_enlist_twice(self):
        """ Starts TPC transaction on connection.
        """
        self.session.__enter__()
        session = Mock()
        session.__enter__ = Mock()
        self.session.enlist(session)
        session = Mock()
        session.__enter__ = Mock()
        session.connection.xid.return_value = 'xid'
        self.session.enlist(session)
        session.__enter__.assert_called_once_with()
        assert session.connection.xid.called
        session.connection.tpc_begin.assert_called_once_with('xid')

    def test_commit_raise_error(self):
        """ If not entered raise error.
        """
        self.assertRaises(AssertionError, lambda: self.session.commit())

    def test_commit_no_enlisted(self):
        """ If nothing enlisted commit does nothing.
        """
        self.session.__enter__()
        self.session.commit()

    def test_commit_prepare_error(self):
        """ An error is raised while working with connection.
        """
        from wheezy.core.db import SESSION_STATUS_ACTIVE
        self.session.__enter__()
        session = Mock()
        session.__enter__ = Mock()
        session.status = SESSION_STATUS_ACTIVE
        self.session.enlist(session)
        assert session.connection.tpc_begin.called
        session.connection.tpc_prepare.side_effect = KeyError()
        session.__exit__ = Mock()
        self.assertRaises(KeyError, lambda: self.session.commit())
        assert not session.connection.tpc_commit.called
        assert not session.__exit__.called

    def test_commit_error(self):
        """ An error is raised while working with connection.
        """
        from wheezy.core.db import SESSION_STATUS_ACTIVE
        self.session.__enter__()
        session = Mock()
        session.__enter__ = Mock()
        session.status = SESSION_STATUS_ACTIVE
        self.session.enlist(session)
        assert session.connection.tpc_begin.called
        session.connection.tpc_commit.side_effect = KeyError()
        session.__exit__ = Mock()
        self.assertRaises(KeyError, lambda: self.session.commit())
        assert session.connection.tpc_prepare.called
        assert not session.__exit__.called

    def test_commit(self):
        """ Enlisted sessions are exited.
        """
        from wheezy.core.db import SESSION_STATUS_ACTIVE
        self.session.__enter__()
        session = Mock()
        session.__enter__ = Mock()
        session.status = SESSION_STATUS_ACTIVE
        self.session.enlist(session)
        assert session.connection.tpc_begin.called
        session.__exit__ = Mock()
        self.session.commit()
        session.connection.tpc_prepare.assert_called_once_with()
        session.connection.tpc_commit.assert_called_once_with()
        session.__exit__.assert_called_once_with(None, None, None)

    def test_exit_on_unused(self):
        """ No sessions enlisted.
        """
        self.session.__enter__()
        self.session.__exit__(None, None, None)

    def test_exit_no_active(self):
        """ There are sessions enlisted but they are not active.
        """
        self.session.__enter__()
        session = Mock()
        session.__enter__ = Mock()
        self.session.enlist(session)
        session.__exit__ = Mock()
        self.session.__exit__(None, None, None)
        assert not session.connection.tpc_rollback.called
        session.__exit__.assert_called_once_with(None, None, None)

    def test_exit_active(self):
        """ There are active sessions enlisted.
        """
        from wheezy.core.db import SESSION_STATUS_ACTIVE
        self.session.__enter__()
        session = Mock()
        session.__enter__ = Mock()
        self.session.enlist(session)
        session.status = SESSION_STATUS_ACTIVE
        session.__exit__ = Mock()
        self.session.__exit__(None, None, None)
        assert session.connection.tpc_rollback.called
        session.__exit__.assert_called_once_with(None, None, None)

    def test_exit_active_on_error(self):
        """ There are active sessions enlisted and error is raised
            while working with connection.
        """
        import warnings
        from wheezy.core.db import SESSION_STATUS_ACTIVE
        self.session.__enter__()
        session = Mock()
        session.__enter__ = Mock()
        self.session.enlist(session)
        session.status = SESSION_STATUS_ACTIVE
        session.__exit__ = Mock()
        session.connection.tpc_rollback.side_effect = KeyError
        warnings.simplefilter('ignore')
        self.session.__exit__(None, None, None)
        assert session.connection.tpc_rollback.called
        session.__exit__.assert_called_once_with(None, None, None)
        warnings.simplefilter('default')


class NullSessionTestCase(unittest.TestCase):

    def test_enter(self):
        """ Enter returns session instance.
        """
        from wheezy.core.db import NullSession
        session = NullSession()
        assert session == session.__enter__()

    def test_commit(self):
        """ If session is not entered raise error.
        """
        from wheezy.core.db import NullSession
        session = NullSession()
        session.__enter__()
        session.commit()

        session = NullSession()
        self.assertRaises(AssertionError, lambda: session.commit())

    def test_exit(self):
        """ If session is not entered raise error.
        """
        from wheezy.core.db import NullSession
        session = NullSession()
        session.__enter__()
        session.__exit__(None, None, None)

        session = NullSession()
        self.assertRaises(AssertionError,
                          lambda: session.__exit__(None, None, None))
