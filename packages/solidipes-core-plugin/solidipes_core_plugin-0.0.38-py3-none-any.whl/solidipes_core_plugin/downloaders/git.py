#!/usr/bin/env python

from solidipes.downloaders.downloader import Downloader
from solidipes.utils.utils import optional_parameter


class GitDownloader(Downloader):
    "Download study from a git repo"

    parser_key = "git"

    def check_url(self):
        from urllib.parse import urlparse

        ALLOWED_SCHEMES = {"http", "https", "ssh", "git", "ftp"}
        ret = False
        result = urlparse(self.url)
        if result.scheme.lower() not in ALLOWED_SCHEMES:
            ret = False
        if result.scheme.lower() in {"http", "https", "ftp"}:
            ret = bool(result.netloc)
        if result.scheme.lower() in {"ssh", "git"}:
            ret = bool(result.netloc or result.path)
        if not ret:
            raise RuntimeError(f"invalid url: {self.url}")

    def download(self):
        self.check_url()

        uri = self.url
        if hasattr(self, "_branch") and self.branch != "":
            uri = f"-b {self.branch} " + uri
        cmd = f"git clone {uri} {self.destination}"
        return self.run_and_check_return(cmd.split(), fail_message="Failed to clone git")

    @optional_parameter
    def branch() -> str:
        "Only download metadata (overrides destination directory's metadata!)"
        pass
