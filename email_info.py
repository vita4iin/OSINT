import dns.resolver
import dns.exception
import requests

DKIM_SELEKTORID = ["selector1", "selector2", "google", "default",
                   "k1", "s1", "s2", "dkim", "mail"]

def kysi_txt(value):
    try:
        vastus = dns.resolver.resolve(value, "TXT", lifetime=5)
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
        return []
    tulemus = []
    for kirje in vastus:
        tulemus.append(b"".join(kirje.strings).decode())
    return tulemus

def leia_mx(value):
    try:
        vastus = dns.resolver.resolve(value, "MX", lifetime=5)
    except(dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
        return []
    tulemus = []
    for kirje in vastus:
        tulemus.append({
            "prioriteet": kirje.preference,
            "server": kirje.exchange.to_text().rstrip("."),
        })
    return tulemus

def kontrolli_spf(value):
    SPF_PUNKTID = {"-all": 2, "~all": 1}
    spf_kirjed = []
    for kirje in kysi_txt(value):
        if kirje.lower().startswith("v=spf1"):
            spf_kirjed.append(kirje)
    if len(spf_kirjed) == 0:
        return {"kirje": None,
                "lopp": None,
                "punktid": 0,
                "hoiatus": "SPF puudub"}

    if len(spf_kirjed) > 1:
        return {"kirje": spf_kirjed[0],
                "lopp": None,
                "punktid": 0,
                "hoiatus": "Mitu SPF kirjet, SPF ei kehti"}

    kirje = spf_kirjed[0]
    viimane = kirje.split(" ")[-1].lower()

    lopp = None
    if viimane.endswith("all"):
        lopp = viimane

    return {
        "kirje": kirje,
        "lopp": lopp,
        "punktid": SPF_PUNKTID.get(lopp, 0),
        "hoiatus": None,
    }

def loe_sildid(kirje):
    sildid = {}
    for osa in kirje.split(";"):
        osa = osa.strip()
        if "=" in osa:
            osad = osa.split("=", 1)
            voti = osad[0].strip().lower()
            vaartus = osad[1].strip()
            sildid[voti] = vaartus
    return sildid

def kontrolli_dmarc(value):
    DMARC_PUNKTID = {"reject": 2, "quarantine": 1}

    dmarc_kirjed = []
    for kirje in kysi_txt("_dmarc." + value):
        if kirje.lower().startswith("v=dmarc1"):
            dmarc_kirjed.append(kirje)
    if len(dmarc_kirjed) == 0:
        return {"kirje": None,
                "poliitika": None,
                "alampoliitika": None,
                "protsent": None,
                "aruanded": None,
                "punktid": 0,
                "hoiatus": "DMARC puudub"}

    if len(dmarc_kirjed) > 1:
        return {"kirje": dmarc_kirjed[0],
                "poliitika": None,
                "alampoliitika": None,
                "protsent": None,
                "aruanded": None,
                "punktid": 0,
                "hoiatus": "Mitu DMARC kirjet, DMARC ei kehti"}

    hoiatus = None

    kirje = dmarc_kirjed[0]
    sildid = loe_sildid(kirje)

    poliitika = sildid.get("p")
    if poliitika is not None:
        poliitika = poliitika.lower()
    if poliitika is None:
        hoiatus = "p= puudub, kirje ei kehti"
    elif sildid.get("pct", "100") != "100":
        hoiatus = "Poliitika kehtib ainult " + sildid["pct"] + "% kirjadele"

    return {
        "kirje": kirje,
        "poliitika": poliitika,
        "alampoliitika": sildid.get("sp", poliitika),
        "protsent": sildid.get("pct", "100"),
        "aruanded": sildid.get("rua"),
        "punktid": DMARC_PUNKTID.get(poliitika, 0), #otsib punktid ja tagastab 0 kui ei matchi
        "hoiatus": hoiatus,
    }

def voti_tugevus(voti, tyyp):
    if tyyp == "ed25519":
        return "ed25519"
    pikkus = len(voti)
    if pikkus < 300:
        return "1024 bitti või vähem"
    if pikkus < 600:
        return "2048 bitti"
    return "4096 bitti"


def kontrolli_dkim(value):
    leitud = []
    nimed = []
    hoiatused = []

    for selektor in DKIM_SELEKTORID:
        for kirje in kysi_txt(selektor + "._domainkey." + value): #kysib DKIM recordeid
            sildid = loe_sildid(kirje)
            voti = sildid.get("p")
            if voti is not None and voti != "" and selektor not in nimed: #tyhi p= tahendaks, et votit pole olemas
                voti = voti.replace(" ", "")
                tyyp = sildid.get("k", "rsa")
                testimine = "y" in sildid.get("t", "").lower()
                tugevus = voti_tugevus(voti, tyyp)

                leitud.append({
                    "selektor": selektor,
                    "tyyp": tyyp,
                    "tugevus": tugevus,
                    "testimine": testimine,
                })
                nimed.append(selektor)

                if testimine:
                    hoiatused.append(selektor + ": testrežiimis (t=y)")
                if tugevus == "1024 bitti või vähem":
                    hoiatused.append(selektor + ": nõrk võti")

    if len(leitud) == 0:
        return {"votmed": [],
                "punktid": 0,
                "hoiatus": "Levinud selektoritega võtit ei leitud, DKIM võib siiski olemas olla"}

    hoiatus = None
    if len(hoiatused) > 0:
        hoiatus = "; ".join(hoiatused)

    return {"votmed": leitud,
            "punktid": 1,
            "hoiatus": hoiatus}

def kontrolli_mta_sts(value):
    sts_kirjed = []
    for kirje in kysi_txt("_mta-sts."+ value):
        if kirje.lower().startswith("v=stsv1"):
            sts_kirjed.append(kirje)

    if len(sts_kirjed) == 0:
        return {
            "olemas": False,
            "reziim": None,
            "punktid": 0,
            "hoiatus": "MTA-STS puudub"
        }
    reziim = None
    hoiatus = None
    url = "https://mta-sts." + value + "/.well-known/mta-sts.txt"
    try:
        vastus = requests.get(url, timeout=20)
        if vastus.status_code == 200:
            for rida in vastus.text.splitlines():
                if rida.strip().lower().startswith("mode:"):
                    reziim = rida.split(":", 1)[1].strip().lower()
        else:
            hoiatus = "Poliitikafail vastas koodiga " + str(vastus.status_code)
    except Exception:
        hoiatus = "Poliitikafaili ei saanud kätte"

    punktid = 0
    if reziim == "enforce":
        punktid = 1

    return {"olemas": True,
            "reziim": reziim,
            "punktid": punktid,
            "hoiatus": hoiatus
            }

def kogu(domeen):
    try:
        mx = leia_mx(domeen)
        spf = kontrolli_spf(domeen)
        dmarc = kontrolli_dmarc(domeen)
        dkim = kontrolli_dkim(domeen)
        mta_sts = kontrolli_mta_sts(domeen)
    except dns.exception.Timeout:
        return {"viga": "DNS päring aegus"}
    except dns.resolver.NoNameservers:
        return {"viga": "Nimeserverid ei vasta"}
    kokku = spf["punktid"] + dmarc["punktid"] + dkim["punktid"] + mta_sts["punktid"]
    return {
        "mx": mx,
        "spf": spf,
        "dmarc": dmarc,
        "dkim": dkim,
        "mta_sts": mta_sts,
        "kokku": kokku,
        "max": 6,
    }