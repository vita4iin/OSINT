def kogu(domeen):
    return {"viga": "Pole veel tehtud"}

"""# ip_info.py guide

**Goal:** find the domain's IP addresses and, for each one, who owns it (ASN, organisation) and where it is (country, city).

**How:** get the A records with dnspython, then ask ipinfo.io about each IP. ipinfo answers in JSON, and `requests` turns that into a dict.

## Step 1: try ipinfo by hand

Open `https://ipinfo.io/141.101.90.16/json` in a browser. You'll see:

```
{"ip": "141.101.90.16", "city": "San Francisco", "country": "US",
 "org": "AS13335 Cloudflare, Inc.", ...}
```

Note that `org` holds two things in one string: the ASN (`AS13335`) and the name (`Cloudflare, Inc.`). We split them.

## Step 2: get the IPs

```python
import dns.resolver
import requests


def leia_ipd(domeen):
    try:
        vastus = dns.resolver.resolve(domeen, "A", lifetime=5)
    except Exception:
        return []
    ipd = []
    for kirje in vastus:
        ipd.append(kirje.to_text())
    return ipd
```

Same DNS query as in `dns_info.py`, but only A records. On any error it returns an empty list, and `kogu()` handles that below.

## Step 3: ask ipinfo about one IP

```python
def ip_andmed(ip):
    try:
        vastus = requests.get("https://ipinfo.io/" + ip + "/json", timeout=10)
    except Exception as e:
        return {"ip": ip, "viga": "Päring ebaõnnestus: " + str(e)}

    if vastus.status_code != 200:
        return {"ip": ip, "viga": "ipinfo vastas koodiga " + str(vastus.status_code)}

    andmed = vastus.json()

    org = andmed.get("org")
    asn = None
    organisatsioon = None
    if org is not None:
        osad = org.split(" ", 1)
        asn = osad[0]
        if len(osad) > 1:
            organisatsioon = osad[1]

    return {
        "ip": ip,
        "asn": asn,
        "organisatsioon": organisatsioon,
        "riik": andmed.get("country"),
        "linn": andmed.get("city"),
        "hostinimi": andmed.get("hostname"),
    }
```

- `requests.get(...)` sends the request. `timeout=10` stops it from hanging forever if ipinfo doesn't answer.
- `status_code` 200 means OK. Without a token, ipinfo answers 429 if we send too many requests, so we check before reading the data.
- `vastus.json()` turns the answer into a normal dict.
- `org.split(" ", 1)` splits at the **first** space only: `"AS13335 Cloudflare, Inc."` becomes `["AS13335", "Cloudflare, Inc."]`. Without the `1`, the name would be cut into pieces too.
- `.get()` instead of `[]` because some IPs lack some fields (private IPs, for example), and `.get` returns `None` instead of crashing.

## Step 4: `kogu()`

```python
def kogu(domeen):
    ipd = leia_ipd(domeen)
    if len(ipd) == 0:
        return {"viga": "Domeenil pole A-kirjeid"}

    tulemused = []
    for ip in ipd:
        tulemused.append(ip_andmed(ip))
    return {"aadressid": tulemused}
```

Call `ip_andmed` for every IP and collect the results in a list. If one IP fails, only that entry gets a `"viga"`; the others still show.

## Order in the file

`import`s at the top, then `leia_ipd`, then `ip_andmed`, then `kogu`.

## Test

`python main.py ut.ee` should show two Cloudflare addresses (AS13335, US). A nonexistent domain should show `"ip": {"viga": "Domeenil pole A-kirjeid"}` without crashing.

## Expected output

```
"ip": {
  "aadressid": [
    {"ip": "141.101.90.17", "asn": "AS13335", "organisatsioon": "Cloudflare, Inc.",
     "riik": "US", "linn": "San Francisco", "hostinimi": null}
  ]
}
```

Note: `ut.ee` sits behind Cloudflare, so we see Cloudflare's IPs, not the university's own server. That's correct, and a good thing to point out in the demo."""