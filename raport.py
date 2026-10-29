"""
# raport.py guide

**Goal:** turn the combined dict from `kogu_koik()` into readable text. `raport.py` doesn't query anything; it only reads the dict and builds a string.

**Rule:** return the text, don't print it. `main.py` prints it in the terminal, and later `gui.py` puts the same text in the window. If `raport.py` printed, the GUI couldn't use it.

## What you get as input

One dict with the keys `domeen`, `dns`, `whois`, `ip`, `email`. Each section is either that module's normal dict or `{"viga": "..."}`. Run `python3 main.py ut.ee` and keep the output open while you work; it's the exact structure you're reading.

## Target output

```
===== ut.ee =====

--- DNS ---
A:      141.101.90.16, 141.101.90.17
AAAA:   2a06:98c1:3200::6, 2a06:98c1:3200::7
NS:     ns.ut.ee, ns2.eenet.ee, ns2.ut.ee
MX:     5 ut-ee.mail.protection.outlook.com
TXT:    12 kirjet

--- WHOIS ---
Registraator:   Haridus- ja Teadusministeerium (EENet)
Loodud:         2010-07-04
Aegub:          2032-12-10
Organisatsioon: -
Nimeserverid:   ns.ut.ee, ns2.eenet.ee, ns2.ut.ee
OK: WHOIS ja DNS nimeserverid ühtivad

--- IP ---
141.101.90.16   AS13335  Cloudflare, Inc.  US

--- E-post ---
VIGA: Pole veel tehtud
```

## Step 1: structure

Write one function per section, each taking that section's dict and returning text: `dns_osa`, `whois_osa`, `ip_osa`, `email_osa`. Then one main function, `koosta(tulemus)`, which calls all four and joins the results under a header with the domain name.

`main.py` should only call `koosta()`; it never needs to know about the section functions.

## Step 2: building text from lines

Easiest pattern: start each function with an empty list, append one string per output line, and at the end join them into one string with a newline between lines. Look up `str.join` — `"\n".join(...)` for lines, `", ".join(...)` for putting a list of IPs or name servers on one line.

## Step 3: errors first

Every section function starts the same way: if the dict has the key `"viga"`, return one line `VIGA: <message>` and stop. Everything after that check can assume the data is there.

## Step 4: empty values

`None` and empty lists must not print as `None` or `[]`. Write one small helper that takes a value and returns `"-"` if it's `None` or an empty list, a comma-joined string if it's a list, and the value as is otherwise. Use it for every field, and the sections stay short.

## Step 5: each section

- **DNS:** one line per record type. TXT is long and messy, so show only the count (`len()`), not the records.
- **WHOIS:** one line per key. Skip `muudetud` and `registreerija` if they clutter the output; your choice.
- **IP:** `aadressid` is a list of dicts, so loop over it and print one line per IP. An entry can have its own `"viga"`, so check that inside the loop too.
- **E-post:** only the `viga` check for now. The real content waits until `meil_info.py` is done and its output shape is fixed.

## Step 6: name server comparison

This is the one piece of actual analysis in `raport.py`, so it goes in `koosta()`, where both sections are visible. If neither DNS nor WHOIS has `"viga"`, sort both name server lists and compare them with `==`. Equal: an OK line. Different: a warning line showing both lists. Sort first because the two sources return servers in different orders.

`dns_info.py` must already strip trailing dots, otherwise `ns.ut.ee.` and `ns.ut.ee` never match.

## Step 7: connect to main.py

In `main.py`, import `raport` and replace the `json.dumps` print with printing `raport.koosta(tulemus)`. Keep the JSON line somewhere you can switch back to, because the raw output is easier for debugging.

## Test

- `ut.ee`: all sections filled, name servers OK.
- `google.com`: different shape of WHOIS data, check nothing prints as `None`.
- `olematu-xyz123.ee`: every section shows a `VIGA` line, no crash.
"""