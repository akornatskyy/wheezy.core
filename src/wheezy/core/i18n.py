""" ``i18n`` module.
"""

import os
import os.path
import gettext

from wheezy.core.comp import defaultdict
from wheezy.core.collections import attrdict


class TranslationsManager(object):
    """ Manages several languages and translation domains.        
    """

    def __init__(self, default_lang='en'):
        self.default_lang = default_lang
        self.fallbacks = {}
        self.translations = defaultdict(attrdict)

    def add_fallback(self, languages):
        """ Adds fallback languages.

            >>> tm = TranslationsManager()
            >>> tm.add_fallback(('uk', 'ru'))
            >>> tm.fallbacks
            {'uk': ('uk', 'ru', 'en')}
        """
        if self.default_lang not in languages:
            languages = list(languages)
            languages.append(self.default_lang)
        self.fallbacks[languages[0]] = tuple(languages)

    def load(self, localedir):
        """ Load all available languages and domains from the
            given directory.

            {localedir}/{lang}/LC_MESSAGES/{domain}.mo

            In order to generate .mo file from .po file:
            $ msgfmt domain.po

            >>> curdir = os.path.dirname(__file__)
            >>> localedir = os.path.join(curdir, 'tests', 'i18n')
            >>> tm = TranslationsManager()
            >>> tm.load(localedir)
            >>> tm.translations.keys()
            ['de', 'en']
            >>> lang = tm['en']
            >>> lang.messages.gettext('hello')
            'Hello'
            >>> lang = tm['de']
            >>> lang.messages.gettext('hello')
            'Hallo'

            Fallback to English:

            >>> lang.messages.gettext('world')
            'World'

            If translation is unknown ``key`` returned

            >>> lang.messages.gettext('test')
            'test'
        """
        for lang in os.listdir(localedir):
            if lang.startswith('.'):  # pragma: nocover
                continue
            domaindir = os.path.join(localedir, lang, 'LC_MESSAGES')
            if os.path.isdir(domaindir):
                for domain in os.listdir(domaindir):
                    if not domain.endswith('.mo'):
                        continue
                    domain = domain[:-3]
                    if lang not in self.fallbacks:
                        self.add_fallback((lang,))
                    self.translations[lang][domain] = gettext.translation(
                            domain,
                            localedir,
                            languages=self.fallbacks[lang]
                    )

    def __getitem__(self, lang):
        """ Returns ``attrdict`` with available translation domains.
        """
        return self.translations[lang]