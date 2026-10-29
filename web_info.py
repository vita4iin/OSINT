"""## Examples

### Real headers, 29.10.2026

**ut.ee** (redirects to `https://ut.ee/et`):

```
Strict-Transport-Security: max-age=31536000
Content-Security-Policy:   child-src 'self' *.facebook.com ... (long, contains unsafe-inline and frame-ancestors)
X-Frame-Options:           SAMEORIGIN
X-Content-Type-Options:    nosniff
Referrer-Policy:           strict-origin-when-cross-origin
Server:                    cloudflare
X-Powered-By:              (missing)
```

**github.com:**

```
Strict-Transport-Security: max-age=31536000; includeSubdomains; preload
Content-Security-Policy:   default-src 'none'; base-uri 'self'; ...
X-Frame-Options:           deny
X-Content-Type-Options:    nosniff
Referrer-Policy:           origin-when-cross-origin, strict-origin-when-cross-origin
Server:                    github.com
X-Powered-By:              (missing)
```

Three things these show that your code must handle:

- GitHub writes `deny` in lowercase, ut.ee writes `SAMEORIGIN` in uppercase. Convert the value with `.upper()` before comparing, or `deny` won't match `DENY`.
- GitHub's `Referrer-Policy` has two values separated by a comma. For scoring, "present" is enough, so don't parse it.
- HSTS `includeSubdomains` and `preload` have no `=`, so `loe_sildid()` skips them and only `max-age` comes out. That's exactly what you need.

### Small pieces

Reading `max-age` from HSTS:

```python
sildid = loe_sildid("max-age=31536000; includeSubdomains; preload")
# {'max-age': '31536000'}
int(sildid.get("max-age", "0"))   # 31536000
```

`.get("max-age", "0")` gives `"0"` if the tag is missing, so `int()` never gets `None`.

Checking for a version number in `Server`:

```python
"Apache/2.4.41"  → has a digit → warning
"cloudflare"     → no digit    → fine
"github.com"     → no digit    → fine
```

Loop over the characters and check each with `.isdigit()`, or use `any(c.isdigit() for c in vaartus)` if you've seen that form.

Checking `nosniff` and X-Frame-Options:

```python
"nosniff" → 1 point          "NoSniff" → lowercase first, then 1 point
"DENY" / "SAMEORIGIN" → 1    "ALLOW-FROM ..." → old, ignored by browsers, 0
```

Comparing dates as strings:

```python
"2026-11-28T09:56:54z"[:10]   # '2026-11-28'
"2026-11-28" < "2026-10-29"   # False → not expired
```

### Real security.txt

**github.com**, `/.well-known/security.txt`, status 200:

```
Contact: https://hackerone.com/github
Acknowledgments: https://hackerone.com/github/hacktivity
Preferred-Languages: en
Canonical: https://github.com/.well-known/security.txt
Policy: https://bounty.github.com
Hiring: https://github.careers
Expires: 2026-11-28T09:56:54z
```

`Contact` doesn't have to be an email; here it's a bug bounty URL. Store it as text as is. `Expires` ends in lowercase `z`, which doesn't matter because you only use the first 10 characters. It expires in a month, so in December this same file will trigger your "expired" warning.

**ut.ee**, `/.well-known/security.txt`: status **403** and an HTML page titled "Ligipääs keelatud". That's not a security.txt, so count it as not found. Whether ut.ee blocks the path or Cloudflare blocks scripts, the code can't tell, and the result is the same.

### Expected output

**ut.ee:**

| Check | Result | Points |
|---|---|---|
| HSTS | `max-age=31536000`, one year | 2 |
| CSP | present, warning: `unsafe-inline` | 1 |
| X-Frame-Options | `SAMEORIGIN` | 1 |
| X-Content-Type-Options | `nosniff` | 1 |
| Referrer-Policy | present | 1 |
| Server | `cloudflare`, no version | no warning |
| security.txt | 403, not found | 0 |
| **Total** | | **6 / 7** |

**github.com:** all five headers present, HSTS one year, CSP without `unsafe-inline`, security.txt found and valid until 28.11.2026. **7 / 7.**

Shape of `kogu()`'s return for ut.ee:

```python
{
    "url": "https://ut.ee/et",
    "paised": {
        "hsts": "max-age=31536000",
        "csp": "child-src 'self' ...",
        "x_frame_options": "SAMEORIGIN",
        "x_content_type_options": "nosniff",
        "referrer_policy": "strict-origin-when-cross-origin",
        "server": "cloudflare",
        "x_powered_by": None,
        "punktid": 6,
        "hoiatus": "CSP lubab unsafe-inline",
    },
    "security_txt": {
        "leitud": False,
        "kontaktid": [],
        "aegub": None,
        "punktid": 0,
        "hoiatus": "security.txt puudub",
    },
    "kokku": 6,
    "max": 7,
}
```"""