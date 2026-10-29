import sys
import re
import json

import dns_info
import whois_info
import ip_info
import email_info

DOMEENI_MUSTER = r"^(?=.{1,253}$)([a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$"


def puhasta_domeen(sisend):
    """'https://www.Example.ee/leht' -> 'example.ee'. Vigase sisendi korral None."""
    d = sisend.strip().lower()
    d = re.sub(r"^[a-z]+://", "", d)
    d = d.split("/")[0]
    d = d.split(":")[0]
    if d.startswith("www."):
        d = d[4:]
    if re.match(DOMEENI_MUSTER, d) is None:
        return None
    return d


def kogu_koik(domeen):
    tulemus = {"domeen": domeen}

    try:
        tulemus["dns"] = dns_info.kogu(domeen)
    except Exception as e:
        tulemus["dns"] = {"viga": str(e)}

    try:
        tulemus["whois"] = whois_info.kogu(domeen)
    except Exception as e:
        tulemus["whois"] = {"viga": str(e)}

    try:
        tulemus["ip"] = ip_info.kogu(domeen)
    except Exception as e:
        tulemus["ip"] = {"viga": str(e)}

    try:
        tulemus["email"] = email_info.kogu(domeen)
    except Exception as e:
        tulemus["email"] = {"viga": str(e)}

    return tulemus


def main():
    if len(sys.argv) < 2:
        print("Kasutus: python main.py <domeen>")
        sys.exit(1)

    domeen = puhasta_domeen(sys.argv[1])
    if domeen is None:
        print("Vigane domeen:", sys.argv[1])
        sys.exit(1)

    tulemus = kogu_koik(domeen)
    print(json.dumps(tulemus, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()