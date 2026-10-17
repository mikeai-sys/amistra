#!/usr/bin/env python3
"""Resolve a list of known black-hole host names to J2000 coordinates.

Queries the CDS Sesame name resolver (SIMBAD/NED/VizieR) and falls back to the
SIMBAD TAP service.  Emits raw resolution results; curation/metadata lives in
make_blackholes.py.

Usage: python3 resolve_blackholes.py BH_NAMES.txt out.json
"""
import json
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

SESAME = "https://cds.unistra.fr/cgi-bin/nph-sesame/-oxp/SNV?%s"
SIMBAD_TAP = "https://simbad.u-strasbg.fr/simbad/sim-tap/sync"


def http_get(url, timeout=45):
    req = urllib.request.Request(url, headers={"User-Agent": "astara-bh-catalog/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def sesame(name):
    url = SESAME % urllib.parse.quote(name)
    try:
        raw = http_get(url)
    except Exception as e:  # noqa: BLE001
        return {"error": str(e)}
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as e:
        return {"error": "parse: %s" % e}
    res = root.findall(".//Resolver")
    out = {"resolvers": []}
    for r in res:
        entry = {
            "name": r.get("name"),
            "oname": (r.findtext("oname") or "").strip(),
            "jradeg": (r.findtext("jradeg") or "").strip(),
            "jdedeg": (r.findtext("jdedeg") or "").strip(),
        }
        if entry["jradeg"]:
            out["resolvers"].append(entry)
    # prefer SIMBAD
    for pref in ("Simbad", "NED", "VizieR"):
        for r in out["resolvers"]:
            if r["name"] == pref and r["jradeg"]:
                out.update({"ra": float(r["jradeg"]), "dec": float(r["jdedeg"]),
                            "oname": r["oname"], "source": pref})
                return out
    if out["resolvers"]:
        r = out["resolvers"][0]
        out.update({"ra": float(r["jradeg"]), "dec": float(r["jdedeg"]),
                    "oname": r["oname"], "source": r["name"]})
    return out


def simbad_basic(name):
    q = "SELECT main_id,ra,dec,otype FROM basic WHERE main_id IN ('%s')" % name.replace("'", "''")
    data = urllib.parse.urlencode({
        "request": "doQuery", "lang": "adql", "format": "json", "query": q}).encode()
    try:
        raw = http_get(SIMBAD_TAP + "?" + data.decode())
    except Exception as e:  # noqa: BLE001
        return {"error": str(e)}
    try:
        d = json.loads(raw)
    except Exception as e:  # noqa: BLE001
        return {"error": "parse: %s" % e}
    rows = d.get("data", [])
    if not rows:
        return {}
    mid, ra, dec, ot = rows[0]
    return {"ra": float(ra), "dec": float(dec), "oname": mid, "otype": ot, "source": "SimbadTAP"}


def main():
    names_file, out_file = sys.argv[1], sys.argv[2]
    with open(names_file, encoding="utf-8") as f:
        names = [l.strip() for l in f if l.strip() and not l.startswith("#")]
    result = {}
    for n in names:
        r = sesame(n)
        if "ra" not in r:
            r2 = simbad_basic(n)
            if "ra" in r2:
                r = r2
        result[n] = r
        status = "ok" if "ra" in r else "FAIL"
        print("%-22s %-4s %s" % (n, status,
              ("ra=%.4f dec=%.4f %s" % (r["ra"], r["dec"], r.get("oname", ""))) if "ra" in r else r.get("error", "")))
        time.sleep(0.35)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=1, sort_keys=True)
    ok = sum(1 for v in result.values() if "ra" in v)
    print("resolved %d/%d -> %s" % (ok, len(names), out_file))


if __name__ == "__main__":
    main()
