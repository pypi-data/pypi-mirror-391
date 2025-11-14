"""
Utility functions for downloading and managing pretrained model weights.

This module ensures that required model weight files are accessible to the
user without being bundled inside the installed package. If a weight file
is not found in the user's current working directory, it is automatically
downloaded from a public repository (Zenodo, HuggingFace, etc.).

Weights are stored under:

    <user_current_working_directory>/weights/pretrained/

This design allows:
- lightweight pip installations
- decoupled distribution of large model files
- reproducible results regardless of user environment
"""

from __future__ import annotations
import requests
from pathlib import Path
from tqdm import tqdm


# Name of the pretrained weight file
WEIGHT_NAME = "coat_small_7479cf9b_checkpoint.pth"

# URL where the weights are publicly hosted (replace with your Zenodo link)
ZENODO_URL = (
    "https://zenodo.org/records/17599045/files/coat_small_7479cf9b_checkpoint.pth"
)


def ensure_local_weight() -> Path:
    """
    Ensure that the pretrained weight file exists locally.

    The function checks whether the weight file is present in the user's current
    working directory under the folder:

        ./weights/pretrained/

    If the file does not exist, it is downloaded from a remote source (Zenodo).

    :return: The local filesystem path to the weight file.
    :rtype: Path
    :raises requests.HTTPError: If the remote download fails.
    """
    # Determine the working directory where the user is running the program
    root = Path.cwd()

    # Final location of the weight file
    target = root / "weights" / "pretrained" / WEIGHT_NAME

    # If the weight already exists, simply return it
    if target.exists():
        return target

    # Create directories if needed
    target.parent.mkdir(parents=True, exist_ok=True)

    # Stream the file from the internet
    response = requests.get(ZENODO_URL, stream=True)
    response.raise_for_status()

    # Total size for progress bar (may be missing on some servers)
    total = int(response.headers.get("content-length", 0))

    # Download with progress visualization
    with open(target, "wb") as f, tqdm(
        total=total,
        unit="B",
        unit_scale=True,
        desc=f"Downloading {WEIGHT_NAME}",
    ) as pbar:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                pbar.update(len(chunk))

    return target
