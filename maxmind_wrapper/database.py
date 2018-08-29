import urllib.request
import ssl
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context
import os
import time
import re
import datetime as dt
import tarfile
import io
from tempfile import gettempdir
from ipaddress import ip_address

import geoip2.database


__all__ = ['Reader', ]


class Reader():
    """Wrapper around Maxmind geoip2 library (with auto-fetch and auto-update capabilities)
    """

    _maxmind_url = "https://download.maxmind.com/app/geoip_download?edition_id=GeoIP2-City&date={}&suffix=tar.gz&license_key={}"
    _maxmind_db_prefix = "GeoIP2-City.mmdb"

    def __init__(self,
                 refresh_days=14,
                 cache_dir=None,
                 maxmind_license_key=None,
                 s3_bucket=None,
                 s3_key=self._maxmind_db_prefix,
                 aws_access_key_id=None,
                 aws_secret_access_key=None):

        # initialize some variables
        self._refresh_seconds = refresh_days*86400
        self._cache_dir = cache_dir
        if not self._cache_dir:
            self._cache_dir = os.path.join(gettempdir(), 'maxmind_wrapper')

        if s3_bucket is not None:  # check if we're updating from s3 instead!
            self._use_s3 = True
            self._s3_bucket = s3_bucket
            self._aws_access_key_id = aws_access_key_id    
            if self._aws_access_key_id is None:
                self._aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')  # raises if not exists
            self._aws_secret_access_key = aws_secret_access_key
            if self._aws_secret_access_key is None:
                self._aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')  # raises if not exists

        else:
            self._use_s3 = False
            self._maxmind_license_key = maxmind_license_key
            if self._maxmind_license_key is None:
                self._maxmind_license_key = os.environ.get('MAXMIND_LICENSE_KEY')  # raises if not exists

        # if cache directory already exists, find the latest files
        if os.path.isdir(self._cache_dir):
            maxmind_db_filename = self._find_latest_filename_in_dir(self._cache_dir, self._maxmind_db_prefix)
            if maxmind_db_filename:
                # compute the timestamp
                self._last_refresh = self._extract_timestamp_from_filename(maxmind_db_filename)
            else:
                self._last_refresh = 0
        else:
            os.mkdir(self._cache_dir)
            self._last_refresh = 0

        self.is_busy = False  # flag that external services can check

        # if files are too old (or missing), then refresh
        if time.time() > self._last_refresh + self._refresh_seconds:
            self._refresh()

        # else load from the files
        else:
            self._reader_raw = geoip2.database.Reader(os.path.join(self._cache_dir, maxmind_db_filename))

    def _find_latest_filename_in_dir(self, dirname, file_prefix):
        if not os.path.isdir(dirname):
            raise RuntimeError("directory %s does not exist" % dirname)

        # find all files matching pattern
        candidates = [fn for fn in os.listdir(dirname) if fn.startswith(file_prefix)]

        # grab the latest one
        if len(sorted(candidates)) > 0:
            return candidates[-1]
        else:
            return None

    def _extract_timestamp_from_filename(self, fn):
        if fn is not None:
            m = re.search(r'\d+$', fn)
            return int(m.group(0))
        else:
            return 0

    def _refresh(self):

        if self._use_s3:
            import boto3
            session = boto3.Session(
                aws_access_key_id=self._aws_access_key_id,
                aws_secret_access_key=self._aws_secret_access_key
            )
            s3 = session.resource('s3')
            s3.Object(self._s3_bucket, self._s3_key).get['Body'].read()

        else:  # fetch directly from Maxmind
            # City db updates every Tues (at least the non-free one does)
            today = dt.date.today()
            lasttues = today - dt.timedelta(days=today.weekday() + 6)
            lasttues = "%4d%02d%02d" % (lasttues.year, lasttues.month, lasttues.day)

            url = self._maxmind_url.format(lasttues, self._maxmind_license_key)

            print("Fetching from %s" % url)
            self.is_busy = True
            with urllib.request.urlopen(url) as response:
                tarball_bytes = response.read()

            file_like_wrapper = io.BytesIO(tarball_bytes)
            tar = tarfile.open(fileobj=file_like_wrapper)
            tar.getnames() 
            for name in tar.getnames():
                if name.endswith(self._maxmind_db_prefix):
                    maxmind_db_bytes = tar.extractfile(name).read()

        self._last_refresh = int(time.time())
        self._save_file(maxmind_db_bytes)

        self.is_busy = False

    def _save_file(self, maxmind_db_bytes):
        if self._cache_dir is None:
            return

        timestamp = str(self._last_refresh).zfill(11)
        maxmind_db_filename = os.path.join(self._cache_dir, self._maxmind_db_prefix + "_" + timestamp)

        with open(maxmind_db_filename, 'wb') as f:
            f.write(maxmind_db_bytes)

        # reload db
        self._reader_raw = geoip2.database.Reader(maxmind_db_filename)

    def city(self, ipaddr):
        # do we need to refresh the database?
        if time.time() > self._last_refresh + self._refresh_seconds:
            self._refresh()

        # cast to string (if was int)
        ipaddr = str(ip_address(ipaddr))

        return self._reader_raw.city(ipaddr)

    def __getattr__(self, attr):
        # do we need to refresh the database?
        if time.time() > self._last_refresh + self._refresh_seconds:
            self._refresh()
        
        return getattr(self._reader_raw, attr)
