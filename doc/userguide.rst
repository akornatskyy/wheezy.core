
User Guide
==========

:ref:`wheezy.core` comes with extensions to the following features:

* collections
* config
* datetime
* descriptors
* i18n
* introspection
* url
* uuid

collections
-----------

The :py:mod:`~wheezy.core.collections` module contains types and functions 
that define various collections, iterators and algorithms.

Classes:

* :py:class:`~wheezy.core.collections.ItemAdapter` - adapts 
  ``defaultdict(list)``.__getitem__ accessor to return item at ``index`` 
  from the list. If ``key`` is not found return None.
* :py:class:`~wheezy.core.collections.attrdict` - a dictionary with 
  attribute-style access. Maps attribute access to dictionary.
* :py:class:`~wheezy.core.collections.defaultattrdict` - a dictionary with 
  attribute-style access. Maps attribute access to dictionary. Extends 
  ``defaultdict``.
  
Functions:

* :py:meth:`~wheezy.core.collections.first_item_adapter` - adapts 
  ``defaultdict(list)``.__getitem__  accessor to return the first item from 
  the list. 
* :py:meth:`~wheezy.core.collections.last_item_adapter` - adapts 
  ``defaultdict(list)``.__getitem__  accessor to return the last item from 
  the list.
* :py:meth:`~wheezy.core.collections.distinct` - returns generator for unique 
  items in ``seq`` with preserved order.
* :py:meth:`~wheezy.core.collections.gzip_iterator` - iterates over ``items`` 
  and returns generator of gzipped items. Argument ``compress_level`` sets
  compression level.

config
------

:py:class:`~wheezy.core.config.Config` -  promotes ``options`` dict to 
attributes. If an option can not be found in ``options``, tries to get it 
from ``master``. ``master`` must have a requested option otherwise raises 
error::

    m = {'DEBUG': False}
    c = Config(options={'DEBUG': True}, master=m)
    assert True == c.DEBUG

``master`` - object with dictionary or attribute style of access.

datetime
--------

Represents an instant in time, typically expressed as a date and time of day.

Classes:

* :py:class:`~wheezy.core.datetime.utc` - defines UTC timezone. There are
  two instances of the class: GMT and UTC.

Functions:

* :py:meth:`~wheezy.core.datetime.format_http_datetime` - formats datetime 
  to a string following rfc1123 pattern::
  
    >>> from wheezy.core.datetime import UTC
    >>> now = datetime(2011, 9, 19, 10, 45, 30, 0, UTC)
    >>> format_http_datetime(now)
    'Mon, 19 Sep 2011 10:45:30 GMT'

* :py:meth:`~wheezy.core.datetime.parse_http_datetime` - parses a string 
  in rfc1123 format to ``datetime``::
  
    >>> parse_http_datetime('Mon, 19 Sep 2011 10:45:30 GMT')
    datetime.datetime(2011, 9, 19, 10, 45, 30)

* :py:meth:`~wheezy.core.datetime.total_seconds` - returns a total number 
  of seconds for the given time delta (``datetime.timedelta`` or ``int``)::
  
    >>> total_seconds(timedelta(hours=2))
    7200

i18n
----

Internationalisation is a process of adapting application to different 
languages, regional differences and technical requirements.
Internationalization is the process of designing a software application so 
that it can be adapted to various languages and regions without engineering 
changes.

``gettext`` is an internationalization and localization (i18n) system commonly
used for writing multilingual programs on Unix-like operating systems.

:py:class:`~wheezy.core.i18n.TranslationsManager` - manages several languages 
and translation domains. You can use method 
:py:meth:`~wheezy.core.i18n.TranslationsManager.load` to load all available 
languages and domains from the given directory (typically it is ``i18n``
directory within our application root directory).

Translations directory structure must follow ``gettext`` requirements (this
this how it looks below ``i18n`` directory)::

    {localedir}/{lang}/LC_MESSAGES/{domain}.mo
    
In order to generate .mo file from .po file::

    $ msgfmt domain.po

:py:class:`~wheezy.core.i18n.TranslationsManager` supports the following
arguments in initialization:

* ``directories`` - a list of directories that holds translations.
* ``default_lang`` - a default language in translations. Defaults to ``en``.

:py:class:`~wheezy.core.i18n.TranslationsManager` supports fallback mechanism.
You can use :py:meth:`~wheezy.core.i18n.TranslationsManager.add_fallback`
to adds fallback languages.

    >>> from wheezy.core.i18n import TranslationsManager
    >>> tm = TranslationsManager(['i18n'], default_lang='en')
    >>> tm.add_fallback(('uk', 'ru'))
    >>> tm.fallbacks
    {'uk': ('uk', 'ru', 'en')}

Default language is always appended to the fallback list.

:py:class:`~wheezy.core.i18n.TranslationsManager` supports dictionary access
that accepts a language code as a key. So the following represents all
translations related to ``en`` language code::

    lang = tm['en']

``lang`` is an instance of 
:py:class:`~wheezy.core.collections.defaultattrdict` where attributes 
correspond to translation file (translation domain), if it is not available 
fallback to an instance of ``gettext.NullTranslations``::
    
    assert 'Hello' == lang.messages.gettext('hello')

Seamless integration with ``gettext`` module simplifies your application
internationalization and localization.

introspection
-------------

Type introspection is a capability to determine the type of an object at 
runtime.

:py:meth:`~wheezy.core.introspection.import_name` - dynamically imports 
object by its full name. The following two imports are equivalent::

    from datetime import timedelta
    import_name('datetime.timedelta')

:py:meth:`~wheezy.core.introspection.import_name` let you introduce lazy
imports into your application.

url
---
Every URL consists of the following: the scheme name (or protocol), 
followed by a colon and two slashes, then, a domain name (alternatively, 
IP address), a port number (optionally), the path of the resource to be 
fetched, a query string, and an optional fragment identifier. Here is the 
syntax::
    
    scheme://domain:port/path?query_string#fragment_id

The :py:mod:`~wheezy.core.url` module provides integration with `urlparse`_
module. 

:py:class:`~wheezy.core.url.UrlParts` - concrete class for 
:func:`urlparse.urlsplit` results, where argument ``parts`` is a tupple of 
length 6. There are the following methods:

* ``geturl()`` - returns the re-combined version of the original URL as a 
  string.
* ``join(other)`` - joins with another ``UrlParts`` instance by taking 
  none-empty values from ``other``. Returns new ``UrlParts`` instance.

There is factory function :py:meth:`~wheezy.core.url.urlparts` for 
:py:class:`~wheezy.core.url.UrlParts` that let you create an instance of 
:py:class:`~wheezy.core.url.UrlParts` with partial content.

uuid
----

A universally unique identifier (UUID) is an identifier that enable 
distributed systems to uniquely identify information without significant 
central coordination. A UUID is a 16-byte (128-bit) number.

There are the following functions available:

* :py:meth:`~wheezy.core.uuid.shrink_uuid` - returns base64 representation 
  of ``uuid``::
  
    >>> shrink_uuid(UUID('a4af2f54-e988-4f5c-bfd6-351c79299b74'))
    'pK8vVOmIT1y_1jUceSmbdA'
    
* :py:meth:`~wheezy.core.uuid.parse_uuid` - decodes base64 string to ``uuid``::

    >>> parse_uuid('pK8vVOmIT1y_1jUceSmbdA')
    UUID('a4af2f54-e988-4f5c-bfd6-351c79299b74')

There is also defined module attribute ``UUID_EMPTY`` that is just an 
instance of UUID ``'00000000-0000-0000-0000-000000000000'``.



.. _`urlparse`: http://docs.python.org/library/urlparse.html

