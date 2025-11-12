from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from tqdm import tqdm
from urllib3.util.retry import Retry


def download_file(
    url: str,
    file_path: Path,
    chunk_size: int = 8192,
    proxies: dict | None = None,
) -> bool:
    """
    Download a file from URL with progress bar.

    Args:
        url: URL to download from
        file_path: Local path to save the file
        chunk_size: Size of chunks to download
        proxies: Proxy configuration dict
        (e.g., {'http': 'http://proxy:port', 'https': 'https://proxy:port'})

    Returns:
        bool: True if download completed successfully, False if failed
    """
    try:
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Use a temporary partial file for atomic completion
        tmp_path = file_path.with_suffix(file_path.suffix + ".part")

        # Configure a session with retries for transient errors
        session = requests.Session()
        retry = Retry(
            total=5,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=("GET",),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Determine if we can resume from a partial download
        existing_size = tmp_path.stat().st_size if tmp_path.exists() else 0

        headers: dict[str, str] = {}
        if existing_size > 0:
            headers["Range"] = f"bytes={existing_size}-"

        # First request to get headers and possibly resume
        response = session.get(url, stream=True, proxies=proxies, headers=headers, timeout=30)
        # If server doesn't support Range and we tried to resume, start over
        if existing_size > 0 and response.status_code == 200:
            # Start from scratch: truncate partial
            existing_size = 0
            headers.pop("Range", None)
            response.close()
            response = session.get(url, stream=True, proxies=proxies, timeout=30)

        # Handle 416 (range not satisfiable) which typically means we already have the full file
        if response.status_code == 416 and tmp_path.exists():
            # Validate by doing a HEAD request to get total size
            head = session.head(url, proxies=proxies, timeout=15)
            total_size_hdr = head.headers.get("content-length")
            if total_size_hdr is not None and int(total_size_hdr) == tmp_path.stat().st_size:
                tmp_path.replace(file_path)
                return True
            # Otherwise, remove corrupt partial and restart
            tmp_path.unlink(missing_ok=True)
            response.close()
            response = session.get(url, stream=True, proxies=proxies, timeout=30)

        response.raise_for_status()

        # Determine total size for progress
        total_size = None
        # Content-Range example: bytes 100-999/1000 → total is after '/'
        content_range = response.headers.get("content-range")
        if content_range and "/" in content_range:
            try:
                total_size = int(content_range.split("/")[-1])
            except ValueError:
                total_size = None
        if total_size is None:
            cl = response.headers.get("content-length")
            if cl is not None:
                try:
                    # If resuming, content-length is remaining bytes
                    remaining = int(cl)
                    total_size = existing_size + remaining if existing_size > 0 else remaining
                except ValueError:
                    total_size = None

        # If the final file already exists and size matches server's total, skip
        if file_path.exists() and total_size is not None and file_path.stat().st_size == total_size:
            return True

        # Open file for append-binary if resuming, else write-binary
        mode = "ab" if existing_size > 0 else "wb"
        with open(tmp_path, mode) as f:
            with tqdm(
                total=total_size,
                initial=existing_size,
                unit="B",
                unit_scale=True,
                desc=file_path.name,
            ) as pbar:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if not chunk:
                        continue
                    f.write(chunk)
                    pbar.update(len(chunk))

        # If we know the expected size, validate
        if total_size is not None and tmp_path.stat().st_size != total_size:
            # Incomplete/corrupt; keep the .part file for future resume
            return False

        # Atomically move into place
        tmp_path.replace(file_path)
        return True

    except Exception:
        # Any exception during download means failure
        return False
