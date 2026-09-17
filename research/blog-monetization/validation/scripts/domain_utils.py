"""
Lightweight registrable-domain (eTLD+1) canonicalization.

Why this exists
----------------
Protocol V2 (research/blog-monetization/protocol/research_protocol_v2.md,
Section 6) requires duplicate detection to operate on the *registrable*
domain (eTLD+1), not on a naive lower()/strip() string compare, so that
"https://www.example.com/path", "www.example.com" and "blog.example.com"
are all recognized as the same site, while "example.co.uk" is correctly
kept distinct from "example.com" (the ".co.uk" second-level label is
itself part of the public suffix, not the registrable name).

Network/dependency constraints
-------------------------------
This repo's tooling must run with no network access and no third-party
dependencies (the sandboxed environments this has been developed in do
not have outbound access to PyPI or publicsuffix.org). A proper
implementation would use the `tldextract` package (which bundles/updates
a full snapshot of the IANA Public Suffix List, ~1500+ entries). Since
that dependency could not be installed or verified in this environment,
this module instead embeds a small, curated table of the common
multi-label public suffixes most likely to appear in this project's site
samples (co.uk, com.au, co.jp, etc.) plus a generic "last two labels"
fallback for everything else.

Known limitation: an uncommon multi-label suffix NOT listed in
COMMON_MULTI_LABEL_SUFFIXES below will be canonicalized using the
generic last-two-labels rule, which can be wrong for domains under that
suffix (e.g. a fictional foo.example.unusual.suffix would be reduced to
"unusual.suffix" instead of "example.unusual.suffix"). If this project
gains network/dependency access in the future, swap this module's
`registrable_domain()` for `tldextract.extract(...).registered_domain`
one-for-one -- the call sites in migrate_schema.py and run_gate_v2.py
only depend on this function's signature, not its internals.
"""
from urllib.parse import urlparse

COMMON_MULTI_LABEL_SUFFIXES = {
    "co.uk", "org.uk", "ac.uk", "gov.uk", "net.uk", "sch.uk", "me.uk",
    "co.jp", "ne.jp", "or.jp", "ac.jp", "go.jp",
    "co.kr", "or.kr", "ne.kr", "go.kr", "ac.kr",
    "com.au", "net.au", "org.au", "edu.au", "gov.au",
    "co.nz", "org.nz", "govt.nz",
    "co.za", "org.za", "gov.za",
    "com.br", "net.br", "org.br",
    "com.mx", "org.mx",
    "co.in", "org.in", "net.in", "gov.in", "ac.in",
    "com.cn", "net.cn", "org.cn", "gov.cn",
    "com.tw", "org.tw", "net.tw",
    "co.il", "org.il", "net.il",
    "com.sg", "org.sg", "net.sg",
    "com.hk", "org.hk", "net.hk",
    "co.id", "or.id",
    "com.tr", "org.tr", "net.tr",
    "co.at", "or.at",
    "co.th", "or.th", "ac.th", "go.th",
}


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
    Return the eTLD+1 / registrable domain for a raw domain/URL/hostname string.

    Examples:
        "https://www.example.com/path" -> "example.com"
        "blog.example.com"             -> "example.com"
        "example.co.uk"                -> "example.co.uk"
        "www.example.co.uk"            -> "example.co.uk"
        "example.net"                  -> "example.net"
    """
    host = normalize_host(raw)
    if not host:
        return ""
    labels = host.split(".")
    if len(labels) < 2:
        return host
    last_two = ".".join(labels[-2:])
    if last_two in COMMON_MULTI_LABEL_SUFFIXES and len(labels) >= 3:
        return ".".join(labels[-3:])
    return last_two


def is_clean_root_form(raw: str) -> bool:
    """True if `raw` is already a bare root-domain string: no scheme, no www., no path/slash."""
    raw = (raw or "").strip()
    if not raw:
        return False
    if raw.startswith("http://") or raw.startswith("https://"):
        return False
    if raw.startswith("www."):
        return False
    if "/" in raw:
        return False
    return raw == raw.lower()
