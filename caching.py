import requests
import json
from datetime import datetime

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
DEBUG = True

class Cache:
    def __init__(self, filename):
        """Load cache from disk, if present"""
        self.filename = filename
        try:
            with open(self.filename, 'r') as cache_file:
                cache_json = cache_file.read()
                self.cache_diction = json.loads(cache_json)
        except:
            self.cache_diction = {}

    def _save_to_disk(self):
        """Save cache to disk"""
        with open(self.filename, 'w') as cache_file:
            json.dump(self.cache_diction, cache_file, indent = 4)

    def _has_entry_expired(self, timestamp_str, expire_in_days):
        """Check if cache timestamp is over expire_in_days old"""

        # gives current datetime
        now = datetime.now()

        # datetime.strptime converts a formatted string into datetime object
        cache_timestamp = datetime.strptime(timestamp_str, DATETIME_FORMAT)

        # subtracting two datetime objects gives you a timedelta object
        delta = now - cache_timestamp
        delta_in_days = delta.days


        # now that we have days as integers, we can just use comparison
        # and decide if cache has expired or not
        if delta_in_days > expire_in_days:
            return True # It's been longer than expiry time
        else:
            return False

    def get(self, identifier):
        """If unique identifier exists in the cache and has not expired, return the data associated with it from the request, else return None"""
        identifier = identifier.upper() # Assuming none will differ with case sensitivity here
        if identifier in self.cache_diction:
            data_assoc_dict = self.cache_diction[identifier]
            if self._has_entry_expired(data_assoc_dict['timestamp'],data_assoc_dict['expire_in_days']):
                if DEBUG:
                    print("Cache has expired for {}".format(identifier))
                # also remove old copy from cache
                del self.cache_diction[identifier]
                self._save_to_disk()
                data = None
            else:
                data = data_assoc_dict['values']
        else:
            data = None
        return data

    def set(self, identifier, data, expire_in_days):
        """Add identifier and its associated values (literal data) to the cache, and save the cache as json"""
        identifier = identifier.upper() # make unique
        self.cache_diction[identifier] = {
            'values': data,
            'timestamp': datetime.now().strftime(DATETIME_FORMAT),
            'expire_in_days': expire_in_days
        }

        self._save_to_disk()
