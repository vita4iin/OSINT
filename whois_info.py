import whois

def vota_esimene(value):
    if type(value) == list:
        if len(value) == 0:
            return None
        return value[0]
    return value

def kuupaev(value):
    value = vota_esimene(value)
    if value is None:
        return None
    return str(value)[:10]

def nimeserverid(value):
    if value == None:
        return []
    if type(value) != list:
        value = [value]
    puhtad = set()
    for ns in value:
        puhtad.add(ns.lower().rstrip("."))
    return sorted(puhtad)

def kogu(domeen):
    try:
        w = whois.whois(domeen)
    except Exception as e:
        return {"viga": "WHOIS päring ebaõnnestus: " + str(e)}

    def loend(value):
        if value is None:
            return []
        if type(value) != list:
            return [value]
        return value

    return {
        "registraator": vota_esimene(w.get("registrar")),
        "loodud": kuupaev(w.get("creation_date")),
        "muudetud": kuupaev(w.get("updated_date")),
        "aegub": kuupaev(w.get("expiration_date")),
        "organisatsioon": vota_esimene(w.get("org")),
        "registreerija": vota_esimene(w.get("registrant_name")),
        "staatus": loend(w.get("status")),
        "nimeserverid": nimeserverid(w.get("name_servers")),
    }