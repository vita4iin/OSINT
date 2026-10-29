import dns.resolver
import dns.exception

KIRJETE_TUUBID = ["A", "AAAA", "NS", "MX", "TXT", "CNAME"]


def kysi(domeen, tyyp):
    try:
        vastus = dns.resolver.resolve(domeen, tyyp, lifetime=5)
    except dns.resolver.NoAnswer:
        return []
    return [kirje.to_text().rstrip(".") for kirje in vastus]

def kogu(domeen):
    tulemus = {}
    try:
        for tyyp in KIRJETE_TUUBID:
            tulemus[tyyp] = kysi(domeen, tyyp)
    except dns.resolver.NXDOMAIN:
        return {"viga": "Domeeni ei eksisteeri"}
    except dns.resolver.NoNameservers:
        return {"viga": "Nimeserverid ei vasta"}
    except dns.exception.Timeout:
        return {"viga": "DNS päring aegus"}
    return tulemus