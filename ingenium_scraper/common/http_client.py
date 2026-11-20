"""Cliente HTTP "educado" compartido por todos los scripts de descubrimiento y scraping.

- Pausa aleatoria de 1-3 s entre peticiones al mismo host (rate limiting); si el
  robots.txt declara Crawl-delay, se respeta si es mayor.
- Reintentos con exponential backoff + jitter ante 429/5xx/errores de red; si el
  servidor manda Retry-After, se espera ese tiempo.
- Respeta robots.txt según RFC 9309: comodines `*` y `$`, la regla más larga gana,
  y se vuelve a comprobar en CADA redirección (una URL permitida puede redirigir
  a una ruta prohibida). Un robots.txt que responde 5xx se trata como "todo prohibido".
- Caché en disco por URL: re-ejecutar un script NO vuelve a golpear el servidor.

Uso:
    from common.http_client import PoliteClient, RobotsBlocked
    http = PoliteClient(cache_dir=Path(__file__).parent / "raw_cache")
    html = http.get_text("https://...")
    pdf_path = http.get_file("https://.../modulhandbuch.pdf")

`RobotsBlocked` (subclase de FetchError) significa que el servidor no admite el acceso
automatizado a esa ruta: es una parada, no un fallo que reintentar ni rodear.
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import re
import time
from pathlib import Path
from urllib.parse import unquote, urlsplit

import httpx

_CONTACT = os.environ.get("SCRAPER_CONTACT", "").strip()
USER_AGENT = "IngeniumSyllabusBot/0.1 (academic research; polite crawler" + (f"; {_CONTACT}" if _CONTACT else "") + ")"
UA_TOKEN = USER_AGENT.split("/")[0].lower()

RETRY_STATUS = {408, 425, 429, 500, 502, 503, 504}
REDIRECT_STATUS = {301, 302, 303, 307, 308}


class FetchError(RuntimeError):
    pass


class RobotsBlocked(FetchError):
    """robots.txt prohíbe la ruta (o su redirección). No se reintenta."""


class RobotsRules:
    """Reglas de un robots.txt para nuestro agente (RFC 9309)."""

    def __init__(self, text: str = "", deny_all: bool = False):
        self.deny_all = deny_all
        self.rules: list[tuple[bool, str, re.Pattern]] = []
        self.crawl_delay: float | None = None
        if text:
            self._parse(text)

    @staticmethod
    def _compile(pattern: str) -> re.Pattern:
        anchored = pattern.endswith("$")
        core = pattern[:-1] if anchored else pattern
        body = ".*".join(re.escape(part) for part in core.split("*"))
        return re.compile("^" + body + ("$" if anchored else ""))

    def _parse(self, text: str) -> None:
        groups: list[tuple[list[str], list[tuple[bool, str]], float | None]] = []
        agents: list[str] = []
        rules: list[tuple[bool, str]] = []
        delay: float | None = None
        in_rules = False
        for raw in text.splitlines():
            line = raw.split("#", 1)[0].strip()
            if ":" not in line:
                continue
            field, value = (s.strip() for s in line.split(":", 1))
            field = field.lower()
            if field == "user-agent":
                if in_rules:  # una línea User-agent tras reglas abre un grupo nuevo
                    groups.append((agents, rules, delay))
                    agents, rules, delay, in_rules = [], [], None, False
                agents.append(value.lower())
            elif field in ("allow", "disallow"):
                in_rules = True
                rules.append((field == "allow", value))
            elif field == "crawl-delay":
                in_rules = True
                try:
                    delay = float(value)
                except ValueError:
                    pass
        groups.append((agents, rules, delay))
        # el grupo con el nombre de agente más específico que coincida con el nuestro; si no, "*"
        specific = [a for ags, _, _ in groups for a in ags if a and a != "*" and UA_TOKEN.startswith(a)]
        selected = max(specific, key=len) if specific else "*"
        for ags, rls, dl in groups:
            if selected in ags:
                for allow, pattern in rls:
                    if pattern:  # "Disallow:" vacío = todo permitido
                        self.rules.append((allow, pattern, self._compile(pattern)))
                if dl is not None:
                    self.crawl_delay = dl

    def can_fetch(self, url: str) -> bool:
        if self.deny_all:
            return False
        parts = urlsplit(url)
        target = (parts.path or "/") + (("?" + parts.query) if parts.query else "")
        best_len, allowed = -1, True
        for allow, pattern, rx in self.rules:
            if rx.match(target) or rx.match(unquote(target)):
                if len(pattern) > best_len or (len(pattern) == best_len and allow):
                    best_len, allowed = len(pattern), allow
        return allowed


class PoliteClient:
    def __init__(self, cache_dir: Path, min_delay: float = 1.0, max_delay: float = 3.0,
                 max_retries: int = 5, timeout: float = 45.0, respect_robots: bool = True,
                 headers: dict | None = None, max_redirects: int = 8):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.min_delay, self.max_delay = min_delay, max_delay
        self.max_retries = max_retries
        self.max_redirects = max_redirects
        self.respect_robots = respect_robots
        self._last_hit: dict[str, float] = {}
        self._robots: dict[str, RobotsRules] = {}
        self._crawl_delay: dict[str, float] = {}
        # Las redirecciones se siguen a mano para pasar cada salto por robots.txt y por el limitador
        self._client = httpx.Client(
            timeout=timeout, follow_redirects=False,
            headers={"User-Agent": USER_AGENT, "Accept-Language": "en;q=0.9,*;q=0.5", **(headers or {})},
        )
        self.stats = {"network": 0, "cache": 0, "retries": 0}

    # ---------- caché ----------
    def _paths(self, url: str) -> tuple[Path, Path]:
        key = hashlib.sha1(url.encode("utf-8")).hexdigest()
        return self.cache_dir / f"{key}.bin", self.cache_dir / f"{key}.meta.json"

    # ---------- robots ----------
    def _rules_for(self, origin: str) -> RobotsRules:
        if origin not in self._robots:
            rules = RobotsRules()  # sin robots.txt (4xx) o inalcanzable => permitido
            for _ in range(2):
                try:
                    r = self._client.get(origin + "/robots.txt", follow_redirects=True)
                except httpx.HTTPError:
                    break
                if r.status_code == 200:
                    # utf-8-sig: un BOM inicial anulaba la primera regla
                    rules = RobotsRules(r.content.decode("utf-8-sig", errors="replace"))
                    break
                if r.status_code >= 500:
                    rules = RobotsRules(deny_all=True)  # RFC 9309: error de servidor => prohibido
                    time.sleep(2)
                    continue
                break
            self._robots[origin] = rules
            if rules.crawl_delay:
                self._crawl_delay[urlsplit(origin).netloc] = rules.crawl_delay
        return self._robots[origin]

    def _allowed(self, url: str) -> bool:
        if not self.respect_robots:
            return True
        parts = urlsplit(url)
        return self._rules_for(f"{parts.scheme}://{parts.netloc}").can_fetch(url)

    # ---------- red ----------
    def _throttle(self, host: str) -> None:
        delay = random.uniform(self.min_delay, self.max_delay)
        if self._crawl_delay.get(host):
            delay = max(delay, self._crawl_delay[host])
        wait = self._last_hit.get(host, 0) + delay - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        self._last_hit[host] = time.monotonic()

    def _send(self, method: str, url: str, **kwargs) -> httpx.Response:
        """Una petición con redirecciones manuales: cada salto pasa por robots.txt y por el limitador de su host."""
        for _ in range(self.max_redirects + 1):
            if not self._allowed(url):
                raise RobotsBlocked(f"robots.txt no permite: {url}")
            self._throttle(urlsplit(url).netloc)
            r = self._client.request(method, url, **kwargs)
            if r.status_code in REDIRECT_STATUS and r.headers.get("location"):
                url = str(httpx.URL(url).join(r.headers["location"]))
                if r.status_code in (301, 302, 303) and method != "HEAD":
                    method, kwargs = "GET", {k: v for k, v in kwargs.items() if k == "headers"}
                else:
                    kwargs = {k: v for k, v in kwargs.items() if k != "params"}
                continue
            return r
        raise FetchError(f"Demasiadas redirecciones: {url}")

    def get_bytes(self, url: str, force: bool = False, method: str = "GET", **kwargs) -> bytes:
        """Descarga (o lee de caché). kwargs se pasan a httpx (params, data, json...)."""
        cache_key = url if not kwargs else url + "|" + json.dumps(kwargs, sort_keys=True, default=str)
        body, meta = self._paths(cache_key)
        if body.exists() and not force:
            self.stats["cache"] += 1
            return body.read_bytes()
        last: Exception | None = None
        for attempt in range(self.max_retries + 1):
            retry_after: float | None = None
            try:
                r = self._send(method, url, **kwargs)
                if r.status_code in RETRY_STATUS:
                    ra = r.headers.get("retry-after", "").strip()
                    retry_after = float(ra) if re.fullmatch(r"\d+(\.\d+)?", ra) else None
                    raise FetchError(f"HTTP {r.status_code}")
                if r.status_code >= 400:
                    raise FetchError(f"HTTP {r.status_code} (no reintentable): {url}")
                body.write_bytes(r.content)
                meta.write_text(json.dumps({
                    "url": url, "final_url": str(r.url), "status": r.status_code,
                    "content_type": r.headers.get("content-type", ""), "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                }, ensure_ascii=False), encoding="utf-8")
                self.stats["network"] += 1
                return r.content
            except RobotsBlocked:
                raise
            except FetchError as e:
                if "no reintentable" in str(e):
                    raise
                last = e
            except httpx.HTTPError as e:
                last = e
            self.stats["retries"] += 1
            # Retry-After del servidor si lo manda; si no, exponential backoff + jitter
            time.sleep(retry_after if retry_after and retry_after <= 300 else min(60.0, 2.0 ** attempt + random.uniform(0, 1)))
        raise FetchError(f"Agotados los reintentos para {url}: {last}")

    def get_text(self, url: str, encoding: str | None = None, **kw) -> str:
        data = self.get_bytes(url, **kw)
        if encoding:
            return data.decode(encoding, errors="replace")
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            return data.decode("latin-1", errors="replace")

    def get_json(self, url: str, **kw):
        return json.loads(self.get_text(url, **kw))

    def get_file(self, url: str, force: bool = False) -> Path:
        """Descarga un binario (PDF...) y devuelve su ruta en la caché."""
        self.get_bytes(url, force=force)
        return self._paths(url)[0]
