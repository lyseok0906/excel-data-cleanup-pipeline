"""
Registrable-domain (eTLD+1) canonicalization using the FULL Public Suffix
List, via `tldextract` (pinned in
research/blog-monetization/validation/requirements.txt -- see that file
and scripts/README.md for the exact version and installation).

Why this exists
----------------
Protocol V2 (research/blog-monetization/protocol/research_protocol_v2.md,
Section 6) requires duplicate detection to operate on the *registrable*
domain, not on a naive lower()/strip() string compare, so that
"https://www.example.com/path", "www.example.com" and "blog.example.com"
are all recognized as the same site, while "example.co.uk" is correctly
kept distinct from "example.com" (the ".co.uk" second-level label is
itself part of the public suffix, not the registrable name).

History (Full PSL blocker -- now RESOLVED, 2026-09-17)
--------------------------------------------------------
Earlier rounds of this project ran with no network/dependency access, so
this module used to embed a small, curated table of common multi-label
public suffixes (co.uk, com.au, ...) plus a generic "last two labels"
fallback for everything else -- documented at the time as a known
limitation (an uncommon suffix not in the table would canonicalize
incorrectly, and PRIVATE PSL entries like blogspot.com/github.io were not
handled at all, so two different blogspot.com sites incorrectly collapsed
to the same registrable domain). That constraint no longer holds: the
user confirmed `pip install tldextract==5.3.2` works and imports cleanly
in their local Windows Python (>=3.10) environment, so this module now
uses tldextract's full IANA Public Suffix List directly instead of any
curated table.

Design choices
--------------
- `TLDExtract(suffix_list_urls=(), cache_dir=None, fallback_to_snapshot=True,
  include_psl_private_domains=True)` is built ONCE as a module-level
  singleton (`_extractor`), not per-call: `suffix_list_urls=()` and
  `cache_dir=None` mean this NEVER makes a network request at runtime
  (this project's tooling must run with no network access);
  `fallback_to_snapshot=True` makes it use tldextract's own bundled PSL
  snapshot file instead.
- `include_psl_private_domains=True` is a deliberate RESEARCH POLICY
  decision (Protocol V2 Section 6-3), not a default left as-is: PRIVATE
  PSL entries (blogspot.com, github.io, ...) are treated as their own
  registrable suffix, because in this research a distinct
  `foo.blogspot.com` is a distinct hosted-site identity worth its own
  Study A row, not one "blogspot.com" site. Two different sites hosted on
  the SAME private-suffix platform (foo.blogspot.com vs bar.blogspot.com)
  must be recognized as different registrable domains, and two DIFFERENT
  private platforms under the same public TLD (foo.github.io vs
  foo.blogspot.com) are, of course, already different.
- `registrable_domain()` calls `result.top_domain_under_public_suffix` on
  the extractor's result -- with `include_psl_private_domains=True`, this
  returns the domain label immediately above whatever suffix boundary was
  actually matched (public OR private), which is exactly "foo.blogspot.com"
  for a blogspot subdomain, "example.co.uk" for a co.uk domain, and
  "example.com" for a plain .com domain.

If `tldextract` is not installed, importing this module raises ImportError
immediately (see below) rather than silently falling back to a
less-correct implementation -- Full PSL is now a required dependency of
this project's validation tooling, not an optional enhancement.
"""
from urllib.parse import urlparse

try:
    from tldextract import TLDExtract
except ImportError as exc:  # pragma: no cover - exercised only when the dependency is missing
    raise ImportError(
        "domain_utils.py requires the 'tldextract' package (pinned in "
        "research/blog-monetization/validation/requirements.txt). Install it with "
        "`pip install -r research/blog-monetization/validation/requirements.txt` "
        "(Python >= 3.10 required). Full PSL support was confirmed working on the "
        "user's local Windows environment with tldextract==5.3.2 as of 2026-09-17; "
        "this error means tldextract is not installed in the environment currently "
        "running this script."
    ) from exc

# Module-level singleton -- see the module docstring above for why each
# constructor argument is set the way it is. Built once at import time,
# not per-call, since constructing a TLDExtract instance re-parses the
# bundled PSL snapshot.
_extractor = TLDExtract(
    suffix_list_urls=(),
    cache_dir=None,
    fallback_to_snapshot=True,
    include_psl_private_domains=True,
)


def normalize_host(raw: str) -> str:
    """Strip scheme, path, query, fragment, port, and lowercase -- return a bare host."""
    raw = (raw or "").strip()
    if not raw:
        return ""
    candidate = raw if "://" in raw else "http://" + raw
    parsed = urlparse(candidate)
    host = parsed.netloc or parsed.path
    host = host.split("@")[-1]  # drop userinfo if present
    host = host.split(":")[0]  # drop port
    host = host.strip().strip("/").lower()
    return host


def registrable_domain(raw: str) -> str:
    """
    Return the registrable domain (eTLD+1, PRIVATE PSL entries included per
    this project's policy -- see module docstring) for a raw domain/URL/
    hostname string.

    Examples:
        "https://www.example.com/path" -> "example.com"
        "blog.example.com"             -> "example.com"
        "example.co.uk"                -> "example.co.uk"
        "www.example.co.uk"            -> "example.co.uk"
        "example.net"                  -> "example.net"
        "foo.blogspot.com"             -> "foo.blogspot.com"  (private PSL entry)
        "bar.blogspot.com"             -> "bar.blogspot.com"  (distinct from foo's)
        "foo.github.io"                -> "foo.github.io"     (private PSL entry)
    """
    host = normalize_host(raw)
    if not host:
        return ""
    result = _extractor(host)
    domain = result.top_domain_under_public_suffix
    return domain or host


def is_clean_root_form(raw: str) -> bool:
    """
    True if `raw` is already a bare, canonical root-domain string: no
    scheme, no www., no path/slash, all-lowercase, AND `raw` itself IS its
    own registrable domain (i.e. it is not a subdomain of something else).

    This last condition (added when Full PSL was implemented) is what
    catches a bare-looking but non-root string like "blog.example.com" --
    previously `is_clean_root_form` only checked surface formatting
    (scheme/www/path/case) and would incorrectly accept a subdomain that
    happened to have no "www." prefix. A PRIVATE PSL entry like
    "foo.blogspot.com" is, correctly, still True here: this project treats
    it as its own independent site identity (see module docstring), and
    `registrable_domain("foo.blogspot.com") == "foo.blogspot.com"`.

    Examples:
        "example.com"              -> True
        "example.co.uk"            -> True
        "foo.blogspot.com"         -> True   (its own registrable identity)
        "www.example.com"          -> False  (www. prefix)
        "blog.example.com"         -> False  (a subdomain of example.com)
        "https://example.com/x"    -> False  (scheme + path)
    """
    raw = (raw or "").strip()
    if not raw:
        return False
    if raw.startswith("http://") or raw.startswith("https://"):
        return False
    if raw.startswith("www."):
        return False
    if "/" in raw:
        return False
    if raw != raw.lower():
        return False
    return raw == registrable_domain(raw)
