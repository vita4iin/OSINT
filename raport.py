def vaartus(v):
    if v is None or v == []:
        return "-"
    if isinstance(v, list):
        return ", ".join(str(x) for x in v)
    return str(v)


def dns_osa(d):
    if "viga" in d:
        return "VIGA: " + d["viga"]
    read = []
    read.append("A:      " + vaartus(d.get("A")))
    read.append("AAAA:   " + vaartus(sorted(d.get("AAAA") or [])))
    read.append("NS:     " + vaartus(d.get("NS")))
    read.append("MX:     " + vaartus(d.get("MX")))
    read.append("TXT:    " + str(len(d.get("TXT") or [])) + " kirjet")
    return "\n".join(read)


def whois_osa(d):
    if "viga" in d:
        return "VIGA: " + d["viga"]
    read = []
    read.append("Registraator:   " + vaartus(d.get("registraator")))
    read.append("Loodud:         " + vaartus(d.get("loodud")))
    read.append("Aegub:          " + vaartus(d.get("aegub")))
    read.append("Organisatsioon: " + vaartus(d.get("organisatsioon")))
    read.append("Nimeserverid:   " + vaartus(d.get("nimeserverid")))
    return "\n".join(read)


def ip_osa(d):
    if "viga" in d:
        return "VIGA: " + d["viga"]
    read = []
    for kirje in d.get("aadressid", []):
        if "viga" in kirje:
            read.append(vaartus(kirje.get("ip")) + "  VIGA: " + kirje["viga"])
            continue
        read.append(
            vaartus(kirje.get("ip")).ljust(18)
            + vaartus(kirje.get("asn")).ljust(9)
            + vaartus(kirje.get("organisatsioon")) + "  "
            + vaartus(kirje.get("riik"))
        )
    if not read:
        read.append("-")
    return "\n".join(read)


def email_osa(d):
    if "viga" in d:
        return "VIGA: " + d["viga"]
    return "(sisu tuleb hiljem)"


def ns_vordlus(dns, whois):
    if "viga" in dns or "viga" in whois:
        return None
    dns_ns = sorted(x.lower() for x in (dns.get("NS") or []))
    whois_ns = sorted(x.lower() for x in (whois.get("nimeserverid") or []))
    if dns_ns == whois_ns:
        return "OK: WHOIS ja DNS nimeserverid ühtivad"
    return ("HOIATUS: nimeserverid erinevad\n"
            "  DNS:   " + vaartus(dns_ns) + "\n"
            "  WHOIS: " + vaartus(whois_ns))


def koosta(tulemus):
    dns = tulemus.get("dns", {"viga": "puudub"})
    whois = tulemus.get("whois", {"viga": "puudub"})

    read = ["===== " + str(tulemus.get("domeen", "?")) + " =====", ""]
    read += ["--- DNS ---", dns_osa(dns), ""]
    read += ["--- WHOIS ---", whois_osa(whois)]
    vordlus = ns_vordlus(dns, whois)
    if vordlus:
        read.append(vordlus)
    read.append("")
    read += ["--- IP ---", ip_osa(tulemus.get("ip", {"viga": "puudub"})), ""]
    read += ["--- E-post ---", email_osa(tulemus.get("email", {"viga": "puudub"}))]
    return "\n".join(read)