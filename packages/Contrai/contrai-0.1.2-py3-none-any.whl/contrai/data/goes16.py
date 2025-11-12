# contrai/data/goes16.py
"""
Utilities to locate and download GOES-16 ABI L1b radiance data
from the public NOAA S3 bucket.

All functions are side-effect free except for explicit downloads.
"""

import os
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple, Iterable

import s3fs

DEFAULT_BUCKET = "noaa-goes16"
DEFAULT_PRODUCT = "ABI-L1b-RadF"          # Full Disk L1b radiances
DEFAULT_ASH_CHANNELS = ("11", "13", "14", "15")
DEFAULT_MAX_TIME_DIFF = timedelta(minutes=30)
DEFAULT_OUT_ROOT = "goes16_ash_l1b"

SCAN_RE = re.compile(r"_s(\d{4})(\d{3})(\d{2})(\d{2})(\d{2})")


def target_datetime(year: int, month: int, day: int, hhmm: str) -> datetime:
    """
    Build a UTC :class:`datetime` from components.

    Parameters
    ----------
    year : int
        Four-digit year.
    month : int
        Month number (1-12).
    day : int
        Day of month (1-31).
    hhmm : str
        Time string in ``"HHMM"`` 24-hour format.

    Returns
    -------
    datetime
        Combined datetime in UTC.
    """
    hour = int(hhmm[:2])
    minute = int(hhmm[2:4])
    return datetime(year, month, day, hour, minute)


def day_of_year(dt: datetime) -> int:
    """
    Compute the day-of-year index for a given date.

    Parameters
    ----------
    dt : datetime
        Datetime instance.

    Returns
    -------
    int
        Day of year starting at 1 for January 1.
    """
    return (dt - datetime(dt.year, 1, 1)).days + 1


def extract_scan_time_from_name(name: str) -> Optional[datetime]:
    """
    Extract GOES-ABI scan start time embedded in a filename.

    The pattern searched is ``_sYYYYJJJHHMMSS_`` where
    ``YYYY`` = year, ``JJJ`` = Julian day, ``HHMMSS`` = UTC time.

    Parameters
    ----------
    name : str
        Object key or filename.

    Returns
    -------
    datetime or None
        Parsed scan start time, or ``None`` if pattern not found.
    """
    m = SCAN_RE.search(name)
    if not m:
        return None
    year, jjj, hh, mm, ss = map(int, m.groups())
    dt0 = datetime(year, 1, 1) + timedelta(days=jjj - 1)
    return datetime(dt0.year, dt0.month, dt0.day, hh, mm, ss)


def find_ash_keys_for_datetime(
    year: int,
    month: int,
    day: int,
    hhmm: str,
    *,
    channels: Iterable[str] = DEFAULT_ASH_CHANNELS,
    bucket: str = DEFAULT_BUCKET,
    product: str = DEFAULT_PRODUCT,
    max_time_diff: Optional[timedelta] = DEFAULT_MAX_TIME_DIFF,
) -> Tuple[Dict[str, str], datetime]:
    """
    Locate ABI-L1b-RadF S3 object keys closest in time to the target.

    Parameters
    ----------
    year, month, day : int
        Target date (UTC).
    hhmm : str
        Target time in ``"HHMM"`` 24-hour format.
    channels : Iterable[str], optional
        Channel numbers to retrieve (default ``("11","13","14","15")``).
    bucket : str, optional
        S3 bucket name (default ``"noaa-goes16"``).
    product : str, optional
        Product folder, e.g. ``"ABI-L1b-RadF"``.
    max_time_diff : timedelta or None, optional
        Maximum allowed difference between requested time and scan start.
        If ``None``, time filtering is disabled.

    Returns
    -------
    (dict, datetime)
        Mapping ``{channel: s3_key}`` and the resolved target datetime.

    Raises
    ------
    FileNotFoundError
        If no matching files or channels are found or time difference exceeds
        ``max_time_diff``.
    """
    fs = s3fs.S3FileSystem(anon=True)
    target = target_datetime(year, month, day, hhmm)
    doy = day_of_year(target)
    day_prefix = f"{bucket}/{product}/{year:04d}/{doy:03d}/"

    try:
        hour_dirs = fs.ls(day_prefix)
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"No data for {year}-{month:02d}-{day:02d} (doy {doy:03d}) "
            f"under s3://{bucket}/{product}/"
        ) from e

    all_files = []
    for hour_dir in hour_dirs:
        try:
            files = fs.ls(hour_dir)
        except FileNotFoundError:
            continue
        all_files.extend(files)

    if not all_files:
        raise FileNotFoundError(
            f"No files found for {year}-{month:02d}-{day:02d} "
            f"(doy {doy:03d}) under s3://{bucket}/{product}/"
        )

    keys: Dict[str, str] = {}

    for ch in channels:
        ch_files = [
            f for f in all_files
            if (f"{product}-M6C{ch}_" in f) and f.endswith(".nc")
        ]
        if not ch_files:
            raise FileNotFoundError(
                f"No files for band {ch} on {year}-{month:02d}-{day:02d}"
            )

        best_file = None
        best_time = None
        best_diff = None

        for fpath in ch_files:
            t = extract_scan_time_from_name(os.path.basename(fpath))
            if t is None or t.date() != target.date():
                continue
            diff = abs(t - target)
            if best_diff is None or diff < best_diff:
                best_file, best_time, best_diff = fpath, t, diff

        if best_file is None or best_time is None or best_diff is None:
            raise FileNotFoundError(
                f"No valid scan times for band {ch} on {year}-{month:02d}-{day:02d}"
            )

        if max_time_diff is not None and best_diff > max_time_diff:
            raise FileNotFoundError(
                "Closest file for band {ch} is at {bt} UTC, outside "
                "max_time_diff={mt} from target {tt} UTC. "
                "File: s3://{f}".format(
                    ch=ch,
                    bt=best_time.strftime("%Y-%m-%d %H:%M:%S"),
                    mt=str(max_time_diff),
                    tt=target.strftime("%Y-%m-%d %H:%M:%S"),
                    f=best_file,
                )
            )

        keys[ch] = best_file

    return keys, target


def download_ash_bands_for_datetime(
    year: int,
    month: int,
    day: int,
    hhmm: str,
    *,
    out_root: str = DEFAULT_OUT_ROOT,
    channels: Iterable[str] = DEFAULT_ASH_CHANNELS,
    bucket: str = DEFAULT_BUCKET,
    product: str = DEFAULT_PRODUCT,
    max_time_diff: Optional[timedelta] = DEFAULT_MAX_TIME_DIFF,
) -> Tuple[Dict[str, str], datetime]:
    """
    Download GOES-16 ABI-L1b-RadF Ash-RGB channel files for a given datetime.

    Parameters
    ----------
    year, month, day : int
        Target date (UTC).
    hhmm : str
        Target time in ``"HHMM"`` 24-hour format.
    out_root : str, optional
        Root output directory (default ``"goes16_ash_l1b"``).
    channels : Iterable[str], optional
        Channel numbers to retrieve (default ``("11","13","14","15")``).
    bucket : str, optional
        S3 bucket name (default ``"noaa-goes16"``).
    product : str, optional
        Product folder (default ``"ABI-L1b-RadF"``).
    max_time_diff : timedelta or None, optional
        Maximum tolerated difference between requested and scan start times.

    Returns
    -------
    (dict, datetime)
        Mapping ``{channel: local_path}`` of downloaded files
        and the resolved target datetime.

    Raises
    ------
    FileNotFoundError
        If files for required channels cannot be located or downloaded.
    """
    fs = s3fs.S3FileSystem(anon=True)

    keys, target = find_ash_keys_for_datetime(
        year=year,
        month=month,
        day=day,
        hhmm=hhmm,
        channels=channels,
        bucket=bucket,
        product=product,
        max_time_diff=max_time_diff,
    )

    subdir = os.path.join(
        out_root,
        f"{year:04d}",
        f"{month:02d}",
        f"{day:02d}",
        hhmm,
    )
    os.makedirs(subdir, exist_ok=True)

    local_paths: Dict[str, str] = {}
    for ch, key in keys.items():
        fname = os.path.basename(key)
        local_path = os.path.join(subdir, fname)
        if os.path.exists(local_path):
            os.remove(local_path)
        fs.get(key, local_path)
        local_paths[ch] = local_path

    return local_paths, target


__all__ = [
    "target_datetime",
    "day_of_year",
    "extract_scan_time_from_name",
    "find_ash_keys_for_datetime",
    "download_ash_bands_for_datetime",
]
