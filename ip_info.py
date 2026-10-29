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

def kogu(domeen):
    ipd = leia_ipd(domeen)
    if len(ipd) == 0:
        return {"viga": "Domeenil pole A-kirjeid"}

    tulemused = []
    for ip in ipd:
        tulemused.append(ip_andmed(ip))
    return {"aadressid": tulemused}