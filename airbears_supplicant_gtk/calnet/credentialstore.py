import base64
import logging

from airbears_supplicant_gtk import log
from gi.repository import GObject
from gi.repository import GnomeKeyring

logger = logging.getLogger(__name__)

class CredentialStore:
    def save(self, username, password):
        """
        Save the username and password.
        
        Return True if successful, else return False.
        """
        raise NotImplementedError()
    
    def get_credentials(self):
        """
        Return a tuple (username, password) if credentials have been stored,
        else return None
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

    def get_credentials(self):
        return ("TestUsername", "TestPassword")

    def has_credentials(self):
        return self.has_creds

class GnomeCredentialStore(CredentialStore):
    ITEM_ATTR_ID = 'airbears_supplicant'
    KEYRING_NAME = 'login'

    def __init__(self):
        self.item_attrs = GnomeKeyring.Attribute.list_new()
        GnomeKeyring.Attribute.list_append_string(self.item_attrs, 'id', GnomeCredentialStore.ITEM_ATTR_ID)
        
    def _encode_credentials(self, username, password):
        logger.debug("Encoding credentials")
        return "%s@@@%s" % (base64.b64encode(username),
                            base64.b64encode(password))

    def _decode_credentials(self, encoded):
        logger.debug("Attempting to decode credentials")
        if "@@@" in encoded:
            split = encoded.split("@@@")
            try:
                username = base64.b64decode(split[0])
                password = base64.b64decode(split[1])
            except:
                logger.deubg("Error base64 decoding credentials")
                return None
            logger.debug("Successfully retrieved credentials for username: %s" % username)
            return (username, password)
        logger.debug("Credentials were stored in a strange format")
        return None
        
    def _find_keyring_item_id(self):
        cached_value = getattr(self, '_cached_item_id', None)
        if cached_value:
            # only 1 keyring item is needed, so it's safe to cache
            logger.deubg("Retrieved cached keyring item id from cache: %s" % cached_value)
            return self._cached_item_id
            
        logger.debug("No keyring item id cached, so need to create the item")
        result, value = GnomeKeyring.find_items_sync(
                            GnomeKeyring.ItemType.GENERIC_SECRET,
                            self.item_attrs)
        if result != GnomeKeyring.Result.OK:
            logger.debug("There was an error finding the keyring item: %s" % result)
            return None
        
        self._cached_item_id = value[0].item_id
        logger.debug("Successfully found keyring item id: %s" % self._cached_item_id)
        return self._cached_item_id
     
    def _get_keyring_item_info(self, item_id):
        result, value = GnomeKeyring.item_get_info_sync(
                            GnomeCredentialStore.KEYRING_NAME,
                            item_id)
        if result != GnomeKeyring.Result.OK:
            logger.debug("Failed to get keyring info for item_id %s: %s" % (item_id, result))
            return None
        logger.debug("Successfully got keyring item info for item_id %s" % item_id)
        return value
        
    def _create_keyring_item_info(self, secret):
        result, item_id = GnomeKeyring.item_create_sync(
                                GnomeCredentialStore.KEYRING_NAME,
                                GnomeKeyring.ItemType.GENERIC_SECRET,
                                repr(GnomeCredentialStore.ITEM_ATTR_ID),
                                self.item_attrs,
                                secret,
                                True)
        if result != GnomeKeyring.Result.OK:
            logger.debug("Failed to create keyring item: %s" % result)
            return None
        logger.debug("Successfully created keyring item info with item id: %s " % item_id)
        return item_id
    
    def save(self, username, password):
        encoded_credentials = self._encode_credentials(username, password)
    
        item_id = self._find_keyring_item_id()
        if not item_id:
            item_id = self._create_keyring_item_info(encoded_credentials)
        else:
            item_info = self._get_keyring_item_info(item_id)
            item_info.set_secret(encoded_credentials)
            GnomeKeyring.item_set_info_sync(
                GnomeCredentialStore.KEYRING_NAME,
                item_id,
                item_info)
        logger.debug("Successfully saved new credentials to item_id: %s" % item_id)
        return True
        
    def get_credentials(self):
        item_id = self._find_keyring_item_id()
        if not item_id:
            return None

        item_info = self._get_keyring_item_info(item_id)
        credentials = self._decode_credentials(item_info.get_secret())
        return credentials

    def has_credentials(self):
        return self._find_keyring_item_id() is not None
