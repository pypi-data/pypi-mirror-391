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
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from pyresample import geometry, kd_tree

DEFAULT_BUCKET = "noaa-goes16"
DEFAULT_PRODUCT = "ABI-L1b-RadF"          # Full Disk L1b radiances
DEFAULT_ASH_CHANNELS = ("11", "13", "14", "15")
DEFAULT_MAX_TIME_DIFF = timedelta(minutes=30)
DEFAULT_OUT_ROOT = "images/goes16_l1b"
DEFAULT_ASH_RGB_ROOT = "images/goes16_ash_rgb"
DEFAULT_ASH_LAT_BOUNDS = (15.0, 40.0)
DEFAULT_ASH_LON_BOUNDS = (-90.0, -30.0)
DEFAULT_ASH_RES_DEG = 0.02  # ~2 km

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
def _load_bt(path: str):
    """
    Load brightness temperature and projection info from a GOES-16 ABI L1b file.

    Returns
    -------
    bt : np.ndarray (float32)
        Brightness temperature [K].
    proj : xarray.DataArray
        GOES imager projection variable.
    x, y : xarray.DataArray
        Fixed grid coordinates.
    """
    with xr.open_dataset(path) as ds:
        rad = ds["Rad"]
        # Some products have time dimension; use first timestep.
        if "t" in rad.dims:
            rad = rad.isel(t=0)
        rad = rad.values

        fk1 = float(ds["planck_fk1"])
        fk2 = float(ds["planck_fk2"])
        bc1 = float(ds["planck_bc1"])
        bc2 = float(ds["planck_bc2"])

        bt = fk2 / np.log(fk1 / (rad + bc1) + 1.0) + bc2

        proj = ds["goes_imager_projection"]
        x = ds["x"]
        y = ds["y"]

    return bt.astype(np.float32), proj, x, y


def _goes_latlon(proj, x, y):
    """
    Convert GOES fixed grid coordinates to lat/lon in degrees.
    """
    Re = float(proj.semi_major_axis)
    Rp = float(proj.semi_minor_axis)
    H = float(proj.perspective_point_height) + Re
    lon0 = np.deg2rad(float(proj.longitude_of_projection_origin))

    xx, yy = np.meshgrid(x.values, y.values)

    sin_x = np.sin(xx)
    cos_x = np.cos(xx)
    sin_y = np.sin(yy)
    cos_y = np.cos(yy)

    a = (
        sin_x**2
        + cos_x**2 * (cos_y**2 + (Re**2 / Rp**2) * sin_y**2)
    )
    b = -2.0 * H * cos_x * cos_y
    c = H**2 - Re**2

    disc = b**2 - 4 * a * c
    mask = disc <= 0
    disc = np.where(mask, np.nan, disc)

    rs = (-b - np.sqrt(disc)) / (2 * a)

    Sx = rs * cos_x * cos_y
    Sy = rs * sin_x * cos_y
    Sz = rs * sin_y

    lat = np.arctan((Re**2 / Rp**2) * (Sz / np.sqrt((H - Sx) ** 2 + Sy**2)))
    lon = lon0 - np.arctan2(Sy, H - Sx)

    lat_deg = np.rad2deg(lat)
    lon_deg = np.rad2deg(lon)

    lat_deg[mask] = np.nan
    lon_deg[mask] = np.nan

    return lon_deg, lat_deg


def _clip_scale(data: np.ndarray, vmin: float, vmax: float) -> np.ndarray:
    """
    Linearly scale data to 0-1 and clip.
    """
    out = (data - vmin) / (vmax - vmin)
    return np.clip(out, 0.0, 1.0)


def _build_area_def(
    lat_min: float,
    lat_max: float,
    lon_min: float,
    lon_max: float,
    res_deg: float,
) -> geometry.AreaDefinition:
    """
    Build a regular lat/lon AreaDefinition for pyresample.
    """
    lats_tgt = np.arange(lat_min, lat_max + res_deg, res_deg)
    lons_tgt = np.arange(lon_min, lon_max + res_deg, res_deg)
    width, height = len(lons_tgt), len(lats_tgt)

    return geometry.AreaDefinition(
        "ash_latlon",
        "GOES-16 Ash RGB lat/lon grid",
        "latlon",
        {"proj": "longlat", "datum": "WGS84", "no_defs": True},
        width,
        height,
        (lon_min, lat_min, lon_max, lat_max),
    )


def _resample_channel(
    channel: np.ndarray,
    swath_def: geometry.SwathDefinition,
    area_def: geometry.AreaDefinition,
) -> np.ndarray:
    return kd_tree.resample_nearest(
        swath_def,
        channel,
        area_def,
        radius_of_influence=8000.0,  # ~1 pixel
        fill_value=np.nan,
    )
def build_ash_rgb_from_paths(
    paths: Dict[str, str],
    *,
    lat_bounds: Tuple[float, float] = DEFAULT_ASH_LAT_BOUNDS,
    lon_bounds: Tuple[float, float] = DEFAULT_ASH_LON_BOUNDS,
    res_deg: float = DEFAULT_ASH_RES_DEG,
) -> np.ndarray:
    """
    Construct GOES-16 Ash RGB composite from local L1b channel files.

    Parameters
    ----------
    paths : dict
        Mapping ``{"11": path_C11, "13": path_C13, "14": path_C14, "15": path_C15}``.
    lat_bounds, lon_bounds : (float, float), optional
        Spatial subset [deg].
    res_deg : float, optional
        Target lat/lon resolution in degrees.

    Returns
    -------
    rgb : np.ndarray
        Float array of shape (ny, nx, 3), scaled 0-1.
    """
    for ch in ("11", "13", "14", "15"):
        if ch not in paths:
            raise KeyError(f"Missing required channel {ch!r} in paths")

    bt11, proj, x, y = _load_bt(paths["11"])
    bt13, _,   _, _  = _load_bt(paths["13"])
    bt14, _,   _, _  = _load_bt(paths["14"])
    bt15, _,   _, _  = _load_bt(paths["15"])

    lon_deg, lat_deg = _goes_latlon(proj, x, y)

    # Ash RGB recipe:
    #   R = C15 - C13
    #   G = C14 - C11
    #   B = C13
    red = bt15 - bt13
    green = bt14 - bt11
    blue = bt13

    red = _clip_scale(red, -4.0, 2.0)
    green = _clip_scale(green, -4.0, 5.0)
    blue = _clip_scale(blue, 243.0, 303.0)

    # Mask space
    space_mask = np.isnan(lat_deg) | np.isnan(lon_deg)
    red[space_mask] = np.nan
    green[space_mask] = np.nan
    blue[space_mask] = np.nan

    lat_min, lat_max = lat_bounds
    lon_min, lon_max = lon_bounds

    area_def = _build_area_def(lat_min, lat_max, lon_min, lon_max, res_deg)
    swath_def = geometry.SwathDefinition(lons=lon_deg, lats=lat_deg)

    Rr = _resample_channel(red, swath_def, area_def)
    Gr = _resample_channel(green, swath_def, area_def)
    Br = _resample_channel(blue, swath_def, area_def)

    rgb = np.dstack(
        [
            np.nan_to_num(Rr, nan=0.0),
            np.nan_to_num(Gr, nan=0.0),
            np.nan_to_num(Br, nan=0.0),
        ]
    )
    return np.clip(rgb, 0.0, 1.0)
def generate_ash_rgb_for_datetime(
    year: int,
    month: int,
    day: int,
    hhmm: str,
    *,
    l1b_root: str = DEFAULT_OUT_ROOT,
    rgb_root: str = DEFAULT_ASH_RGB_ROOT,
    lat_bounds: Tuple[float, float] = DEFAULT_ASH_LAT_BOUNDS,
    lon_bounds: Tuple[float, float] = DEFAULT_ASH_LON_BOUNDS,
    res_deg: float = DEFAULT_ASH_RES_DEG,
    save_png: bool = True,
) -> Tuple[str, np.ndarray, datetime]:
    """
    Download GOES-16 L1b Ash-RGB channels for a datetime, generate Ash RGB,
    and save PNG under a default path.

    The PNG path layout is:
        ``{rgb_root}/{YYYY}/{MM}/{DD}/{HHMM}/ash_rgb_{res}deg.png``

    Parameters
    ----------
    year, month, day : int
        Target date (UTC).
    hhmm : str
        Target time in ``"HHMM"`` 24-hour format.
    l1b_root : str, optional
        Root directory for L1b downloads (matches download_ash_bands_for_datetime).
    rgb_root : str, optional
        Root directory for Ash RGB PNGs.
    lat_bounds, lon_bounds : (float, float), optional
        Geographic subset for the RGB.
    res_deg : float, optional
        Target grid resolution in degrees.
    save_png : bool, optional
        If True, write the PNG to disk.

    Returns
    -------
    (png_path, rgb, target_dt)
        png_path : str
            Where the PNG was (or would be) saved.
        rgb : np.ndarray
            The Ash RGB image array (ny, nx, 3), values 0-1.
        target_dt : datetime
            The resolved scan datetime used.
    """
    # 1. Ensure L1b data are present (download if needed)
    local_paths, target_dt = download_ash_bands_for_datetime(
        year,
        month,
        day,
        hhmm,
        out_root=l1b_root,
        channels=DEFAULT_ASH_CHANNELS,
    )

    # 2. Build RGB
    rgb = build_ash_rgb_from_paths(
        local_paths,
        lat_bounds=lat_bounds,
        lon_bounds=lon_bounds,
        res_deg=res_deg,
    )

    # 3. Build default output path
    res_str = str(res_deg).replace(".", "p")
    out_dir = os.path.join(
        rgb_root,
        f"{year:04d}",
        f"{month:02d}",
        f"{day:02d}",
        hhmm,
    )
    os.makedirs(out_dir, exist_ok=True)
    png_path = os.path.join(out_dir, f"ash_rgb_{res_str}deg.png")

    # 4. Save PNG (if requested)
    if save_png:
        plt.imsave(png_path, rgb)

    return png_path, rgb, target_dt


__all__ = [
    "target_datetime",
    "day_of_year",
    "extract_scan_time_from_name",
    "find_ash_keys_for_datetime",
    "download_ash_bands_for_datetime",
]
