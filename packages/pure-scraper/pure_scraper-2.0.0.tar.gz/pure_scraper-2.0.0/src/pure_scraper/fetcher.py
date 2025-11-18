# pure_scraper/fetcher.py
import socket
import ssl
import zlib
import time
from urllib.parse import urlparse
from .config import config
from .cache import load_from_cache, save_to_cache
from .utils import is_html_valid, clean_html

try:
    import brotli  # optional
    _HAS_BROTLI = True
except Exception:
    _HAS_BROTLI = False

def _log(msg: str):
    if config.show_logs:
        print(msg)

def _read_all(sock: socket.socket) -> bytes:
    buf = bytearray()
    while True:
        try:
            chunk = sock.recv(4096)
        except socket.timeout:
            raise TimeoutError("Socket read timed out")
        if not chunk:
            break
        buf.extend(chunk)
    return bytes(buf)

def _parse_headers(header_bytes: bytes):
    header_text = header_bytes.decode("latin-1")
    lines = header_text.split("\r\n")
    status = lines[0] if lines else ""
    headers = {}
    for line in lines[1:]:
        if ":" in line:
            k, v = line.split(":", 1)
            headers[k.strip().lower()] = v.strip()
    return status, headers

def _decode_body(body: bytes, headers: dict) -> str:
    enc = headers.get("content-encoding", "").lower()
    try:
        if "gzip" in enc or "deflate" in enc:
            try:
                return zlib.decompress(body, 16 + zlib.MAX_WBITS).decode("utf-8", errors="replace")
            except Exception:
                try:
                    return zlib.decompress(body).decode("utf-8", errors="replace")
                except Exception:
                    return body.decode("utf-8", errors="replace")
        elif "br" in enc and _HAS_BROTLI:
            return brotli.decompress(body).decode("utf-8", errors="replace")
        else:
            ctype = headers.get("content-type", "")
            if "charset=" in ctype:
                charset = ctype.split("charset=")[-1].split(";")[0].strip()
                try:
                    return body.decode(charset, errors="replace")
                except Exception:
                    return body.decode("utf-8", errors="replace")
            return body.decode("utf-8", errors="replace")
    except Exception:
        return body.decode("utf-8", errors="replace")

def _fetch_once(url: str, timeout: int):
    parsed = urlparse(url)
    scheme = parsed.scheme or "http"
    host = parsed.hostname
    port = parsed.port or (443 if scheme == "https" else 80)
    path = parsed.path or "/"
    if parsed.query:
        path += "?" + parsed.query

    sock = socket.create_connection((host, port), timeout=timeout)
    if scheme == "https":
        ctx = ssl.create_default_context()
        sock = ctx.wrap_socket(sock, server_hostname=host)

    headers = {
        "Host": parsed.netloc,
        "User-Agent": config.user_agent,
        "Accept-Encoding": "gzip, deflate" + (", br" if _HAS_BROTLI else ""),
        "Connection": "close",
    }

    req = f"GET {path} HTTP/1.1\r\n" + "\r\n".join(f"{k}: {v}" for k,v in headers.items()) + "\r\n\r\n"
    sock.sendall(req.encode("utf-8"))
    raw = _read_all(sock)
    sock.close()

    sep = raw.find(b"\r\n\r\n")
    if sep == -1:
        return b"", 500, {}
    header_bytes = raw[:sep]
    body = raw[sep+4:]
    status_line, hdrs = _parse_headers(header_bytes)

    # chunked
    if hdrs.get("transfer-encoding", "").lower() == "chunked":
        out = bytearray()
        rest = body
        while True:
            pos = rest.find(b"\r\n")
            if pos == -1:
                break
            size_str = rest[:pos].decode("latin-1").strip()
            try: size = int(size_str, 16)
            except ValueError: break
            if size == 0: break
            start = pos + 2
            out.extend(rest[start:start+size])
            rest = rest[start+size+2:]
        body = bytes(out)

    status_code = 500
    try:
        status_code = int(status_line.split(" ")[1])
    except Exception:
        pass
    return body, status_code, hdrs

def fetch_html(url: str, timeout: int = None, use_cache: bool = None, max_attempts: int = 3):
    timeout = timeout or config.timeout
    use_cache = config.use_cache if use_cache is None else use_cache

    for attempt in range(1, max_attempts + 1):
        html = None
        if use_cache:
            cached = load_from_cache(url, max_age_hours=config.cache_expiry_hours)
            if cached:
                _log(f"⚡ Loaded from cache: {url}")
                html = cached

        if not html:
            try:
                body, status, headers = _fetch_once(url, timeout)
                html = _decode_body(body, headers)
            except Exception as e:
                _log(f"⚠️ Fetch error (attempt {attempt}): {e}")
                html = ""

        html = clean_html(html)

        if is_html_valid(html):
            if use_cache: save_to_cache(url, html)
            if config.rate_limit_seconds: time.sleep(config.rate_limit_seconds)
            _log(f"✅ Fetched ({attempt}): {url}")
            return html
        else:
            _log(f"⚠️ Invalid HTML detected (attempt {attempt}), retrying...")
            time.sleep(config.rate_limit_seconds)

    _log(f"❌ Failed to fetch valid HTML after {max_attempts} attempts: {url}")
    return ""
