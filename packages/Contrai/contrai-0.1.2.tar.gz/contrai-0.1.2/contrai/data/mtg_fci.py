# contrai/data/mtg_fci.py
"""
Helpers for searching and downloading Meteosat Third Generation (MTG)
Flexible Combined Imager (FCI) Level 1c products from the EUMETSAT
Data Store using the EUMDAC client.

This module is library-only: no side effects, no printing.
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Iterable, List, Optional, Sequence

import eumdac  # type: ignore[import]


# Default collection ID for FCI L1c High Resolution Image data (MTG, 0°).
# Check EUMETSAT product documentation for the latest IDs.
DEFAULT_FCI_L1C_COLLECTION_ID = "EO:EUM:DAT:0665"


def find_fci_l1c_products(
    datastore: eumdac.DataStore,
    start: datetime,
    end: datetime,
    *,
    collection_id: str = DEFAULT_FCI_L1C_COLLECTION_ID,
    bbox: Optional[Sequence[float]] = None,
    limit: Optional[int] = None,
) -> List[eumdac.dataset.Dataset]:
    """
    Search MTG FCI Level 1c products in the EUMETSAT Data Store.

    Parameters
    ----------
    datastore : eumdac.DataStore
        An authenticated DataStore instance. Authentication (API key/secret)
        must be handled by the caller, for example via
        :class:`eumdac.AccessToken`.
    start : datetime
        Start of search interval (UTC).
    end : datetime
        End of search interval (UTC).
    collection_id : str, optional
        EUMETSAT collection identifier for the desired FCI L1c product.
        Defaults to ``"EO:EUM:DAT:0665"`` (FCI L1c HRFI full disk at 0°).
    bbox : sequence of float, optional
        Geographic bounding box as ``[west, south, east, north]`` in degrees.
        If omitted, no spatial filter is applied.
    limit : int, optional
        Maximum number of products to return. If ``None``, all matches in
        the interval (subject to API defaults) are returned.

    Returns
    -------
    list of eumdac.dataset.Dataset
        List of matching product descriptors.

    Raises
    ------
    ValueError
        If ``start >= end`` or ``bbox`` is malformed.
    """
    if start >= end:
        raise ValueError("start must be earlier than end")

    if bbox is not None:
        if len(bbox) != 4:
            raise ValueError("bbox must be [west, south, east, north]")
        # EUMDAC accepts bbox as a comma-separated string or list; we pass list.

    collection = datastore.get_collection(collection_id)

    search_kwargs = {
        "dtstart": start,
        "dtend": end,
    }
    if bbox is not None:
        search_kwargs["bbox"] = bbox

    products_iter = collection.search(**search_kwargs)

    if limit is None:
        return list(products_iter)

    products: List[eumdac.dataset.Dataset] = []
    for i, p in enumerate(products_iter):
        if i >= limit:
            break
        products.append(p)
    return products


def download_fci_l1c_products(
    datastore: eumdac.DataStore,
    start: datetime,
    end: datetime,
    *,
    out_dir: str,
    collection_id: str = DEFAULT_FCI_L1C_COLLECTION_ID,
    bbox: Optional[Sequence[float]] = None,
    limit: Optional[int] = None,
    entries: Optional[Iterable[str]] = None,
) -> List[str]:
    """
    Download MTG FCI Level 1c products for a given time range (and optional region).

    Parameters
    ----------
    datastore : eumdac.DataStore
        An authenticated DataStore instance.
    start : datetime
        Start of search interval (UTC).
    end : datetime
        End of search interval (UTC).
    out_dir : str
        Directory where products will be saved. Created if it does not exist.
    collection_id : str, optional
        FCI L1c collection identifier. Defaults to
        ``"EO:EUM:DAT:0665"`` (HRFI full disk).
    bbox : sequence of float, optional
        Geographic bounding box as ``[west, south, east, north]`` in degrees.
    limit : int, optional
        Maximum number of products to download.
    entries : iterable of str, optional
        If provided, only download specific entries within each product
        (e.g. selected NetCDF files). If ``None``, the full product is
        downloaded, as implemented by :meth:`eumdac.dataset.Dataset.download`.

    Returns
    -------
    list of str
        Paths of downloaded files (best-effort based on the return values
        of :meth:`eumdac.dataset.Dataset.download`).

    Raises
    ------
    ValueError
        If search parameters are invalid.
    """
    os.makedirs(out_dir, exist_ok=True)

    products = find_fci_l1c_products(
        datastore=datastore,
        start=start,
        end=end,
        collection_id=collection_id,
        bbox=bbox,
        limit=limit,
    )

    downloaded: List[str] = []

    for product in products:
        if entries is None:
            result = product.download(out_dir)
            # EUMDAC may return a path or list; normalise to list of strings.
            if isinstance(result, str):
                downloaded.append(result)
            elif isinstance(result, Iterable):
                downloaded.extend(str(p) for p in result)
        else:
            for entry in entries:
                result = product.download(out_dir, entries=[entry])
                if isinstance(result, str):
                    downloaded.append(result)
                elif isinstance(result, Iterable):
                    downloaded.extend(str(p) for p in result)

    return downloaded


__all__ = [
    "DEFAULT_FCI_L1C_COLLECTION_ID",
    "find_fci_l1c_products",
    "download_fci_l1c_products",
]
