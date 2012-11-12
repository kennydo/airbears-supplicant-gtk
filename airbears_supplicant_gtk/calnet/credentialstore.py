import logging

from airbears_supplicant_gtk import log

logger = logging.getLogger(__name__)

class CredentialStore:
    def save(self, username, password):
        """
        Save the username and password.
        
        Return True if successful, else return False.
        """
        raise NotImplementedError()

    def has_credentials(self):
        """
        Return True if the store has credentials saved, else False
        """
        raise NotImplementedError()

class TestCredentialStore(CredentialStore):
    def __init__(self):
        self.has_creds = False

    def save(self, username, password):
        logger.debug("Called save with username: %s" % username)
        self.has_creds = True
        return True

    def has_credentials(self):
        return self.has_creds

class GnomeCredentialStore(CredentialStore):
    def __init__(self):
        self.has_creds = False
