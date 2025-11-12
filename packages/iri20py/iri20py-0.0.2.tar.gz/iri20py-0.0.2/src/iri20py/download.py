# %% Imports
from __future__ import annotations
from pathlib import Path
import ftplib
from typing import Optional
import warnings
import requests
from urllib.parse import urlparse
from datetime import datetime, timedelta
import socket
import requests.exceptions
import numpy as np
import importlib.resources
import logging

URL = 'https://chain-new.chain-project.net/echaim_downloads/'

APF7 = 'apf107.dat'
IGRG = 'ig_rz.dat'

TIMEOUT = 15  # seconds

logger = logging.getLogger(__name__)  # module logger


def check_files(url: str = URL):
    with importlib.resources.path(__package__, "__init__.py") as fdir:  # type: ignore
        path = fdir.parent / "data"
        if not path.is_dir():
            raise NotADirectoryError(path)

    # Check modification date of files
    for file in [APF7, IGRG]:
        will_download = False
        fpath = path / file
        if not fpath.is_file():
            will_download = True
        else:
            finf = fpath.stat()
            mod_date = datetime.fromtimestamp(finf.st_mtime)
            if datetime.now() - mod_date > timedelta(days=1):
                warnings.warn(
                    f"Warning: {file} is older than 1 day. Updating."
                )
                will_download = True
        if will_download:
            url = f'{URL}/{file}'
            try:
                download(url, fpath)
                logger.info(f"Downloaded {file} successfully.")
            except ConnectionError as e:
                logger.error(e)

    if not (path / APF7).is_file() or not (path / IGRG).is_file():
        raise FileNotFoundError(
            "Required data files are missing after download attempt.")


def download(url: str, fn: Path):

    if url.startswith("http"):
        http_download(url, fn)
    elif url.startswith("ftp"):
        ftp_download(url, fn)
    else:
        raise ValueError(f"not sure how to download {url}")


def http_download(url: str, fn: Path):
    if not fn.parent.is_dir():
        raise NotADirectoryError(fn.parent)

    try:
        R = requests.get(url, allow_redirects=True, timeout=TIMEOUT)
        if R.status_code == 200:
            fn.write_text(R.text)
        else:
            raise ConnectionError(f"Could not download {url} to {fn}")
    except requests.exceptions.ConnectionError:
        raise ConnectionError(f"Could not download {url} to {fn}")


def ftp_download(url: str, fn: Path):

    p = urlparse(url)

    host = p[1]
    path = "/".join(p[2].split("/")[:-1])

    if not fn.parent.is_dir():
        raise NotADirectoryError(fn.parent)

    try:
        with ftplib.FTP(host, "anonymous", "guest", timeout=TIMEOUT) as F, fn.open("wb") as f:
            F.cwd(path)
            F.retrbinary(f"RETR {fn.name}", f.write)
    except (socket.timeout, ftplib.error_perm, socket.gaierror):
        if fn.is_file():  # error while downloading
            fn.unlink()
        raise ConnectionError(f"Could not download {url} to {fn}")


def exist_ok(fn: Path, maxage: Optional[timedelta] = None) -> bool:
    if not fn.is_file():
        return False

    ok = True
    finf = fn.stat()
    ok &= finf.st_size > 1000
    if maxage is not None:
        ok &= datetime.now() - datetime.utcfromtimestamp(finf.st_mtime) <= maxage

    return ok
