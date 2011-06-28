import gzip
import urlparse
from os import path
from datetime import datetime

from django.core.files.storage import FileSystemStorage, get_storage_class
from django.utils.encoding import filepath_to_uri
from django.utils.functional import LazyObject

from compressor.conf import settings


class CompressorFileStorage(FileSystemStorage):
    """
    Standard file system storage for files handled by django-compressor.

    The defaults for ``location`` and ``base_url`` are ``COMPRESS_ROOT`` and
    ``COMPRESS_URL``.

    """
    def __init__(self, location=None, base_url=None, base_url_ssl=None, *args, **kwargs):
        if location is None:
            location = settings.COMPRESS_ROOT
        if base_url is None:
            base_url = settings.COMPRESS_URL
        if base_url_ssl is None:
            base_url_ssl = settings.COMPRESS_URL_SSL
        self.base_url_ssl = base_url_ssl
        super(CompressorFileStorage, self).__init__(location, base_url,
                                                    *args, **kwargs)

    def accessed_time(self, name):
        return datetime.fromtimestamp(path.getatime(self.path(name)))

    def created_time(self, name):
        return datetime.fromtimestamp(path.getctime(self.path(name)))

    def modified_time(self, name):
        return datetime.fromtimestamp(path.getmtime(self.path(name)))

    def get_available_name(self, name):
        """
        Deletes the given file if it exists.
        """
        if self.exists(name):
            self.delete(name)
        return name
    
    def url_ssl(self, name):
        if self.base_url_ssl is None:
            raise ValueError("This file is not accessible via a URL.")
        return urlparse.urljoin(self.base_url_ssl, filepath_to_uri(name))


class GzipCompressorFileStorage(CompressorFileStorage):
    """
    The standard compressor file system storage that gzips storage files
    additionally to the usual files.
    """
    def save(self, filename, content):
        filename = super(GzipCompressorFileStorage, self).save(filename, content)
        out = gzip.open(u'%s.gz' % self.path(filename), 'wb')
        out.writelines(open(self.path(filename), 'rb'))
        out.close()


class DefaultStorage(LazyObject):
    def _setup(self):
        self._wrapped = get_storage_class(settings.COMPRESS_STORAGE)()

default_storage = DefaultStorage()
