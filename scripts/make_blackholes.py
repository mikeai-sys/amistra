#!/usr/bin/env python3
"""Build the black-hole catalog for Astara.

Coordinates are ICRS/J2000 degrees resolved from SIMBAD/NED via Sesame
(see resolve_blackholes.py).  Masses (solar masses) and distances (light
years) are literature values; entries flagged `approx` have uncertain or
provisional parameters.

Emits:
  apps/web-frontend/public/skydata/blackholes.json   (consumed by the engine)
  apps/web-frontend/public/skydata/blackholes.csv    (reference / spreadsheet)
"""
import csv
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_JSON = os.path.join(ROOT, "apps/web-frontend/public/skydata/blackholes.json")
OUT_CSV = os.path.join(ROOT, "apps/web-frontend/public/skydata/blackholes.csv")

SMBH = "SMBH"
STELLAR = "stellar"
IMBH = "IMBH"

# name, ra(deg J2000), de(deg), kind, mass(Msun), dist(ly), host, aliases, year, approx
CATALOG = [
    # --- Supermassive (SMBH) ---
    ("Sagittarius A*", 266.4168, -29.0078, SMBH, 4.297e6, 26996, "Milky Way nucleus", ["Sgr A*", "NAME Sgr A*"], 1974, False),
    ("M87*", 187.7059, 12.3911, SMBH, 6.5e9, 5.35e7, "Messier 87 (Virgo A)", ["M87", "M 87", "NGC 4486", "Virgo A"], 2019, False),
    ("Ton 618", 187.1040, 31.4771, SMBH, 6.6e10, 1.82e10, "quasar (ultramassive)", ["TON 618", "QSO B1226+3142"], 1957, False),
    ("M31*", 10.6847, 41.2687, SMBH, 1.4e8, 2.54e6, "Andromeda Galaxy", ["M31", "NGC 224", "Andromeda"], 1995, False),
    ("NGC 1277", 49.9645, 41.5736, SMBH, 1.7e10, 2.20e8, "NGC 1277", [], 2012, False),
    ("NGC 4889", 195.0337, 27.9770, SMBH, 2.1e10, 3.08e8, "NGC 4889 (Coma B)", [], 2011, False),
    ("NGC 3115", 151.3080, -7.7186, SMBH, 2.0e9, 3.2e7, "NGC 3115 (Spindle)", [], 1992, False),
    ("IC 1101", 227.7338, 5.7448, SMBH, 4.0e10, 1.045e9, "IC 1101", [], 2017, True),
    ("Holm 15A", 10.4602, -9.3032, SMBH, 4.0e10, 7.0e8, "Holm 15A (Abell 85)", [], 2019, True),
    ("NGC 1600", 67.9161, -5.0861, SMBH, 1.7e10, 2.09e8, "NGC 1600", [], 2016, False),
    ("NGC 3842", 176.0090, 19.9498, SMBH, 9.7e9, 3.31e8, "NGC 3842", [], 2011, False),
    ("NGC 6240", 253.2454, 2.4009, SMBH, 6.8e8, 4.0e8, "NGC 6240 (dual SMBH)", [], 2002, True),
    ("3C 273", 187.2779, 2.0524, SMBH, 8.86e8, 2.44e9, "quasar", [], 1963, False),
    ("Cygnus A", 299.8682, 40.7339, SMBH, 2.5e9, 7.4e8, "Cygnus A (radio galaxy)", [], 1951, True),
    ("S5 0014+81", 4.2853, 81.5856, SMBH, 4.0e10, 1.4e10, "quasar", ["6C 001403+811827"], 1996, True),
    ("Phoenix A", 356.1830, -42.7201, SMBH, 1.0e11, 5.7e9, "Phoenix Cluster", [], 2012, True),
    ("SDSS J0100+2802", 15.0543, 28.0405, SMBH, 1.24e10, 1.28e10, "quasar", [], 2015, False),
    ("ULAS J1120+0641", 170.0061, 6.6899, SMBH, 2.0e9, 2.9e10, "quasar", [], 2011, False),
    ("J0313-1806", 48.3588, -18.1078, SMBH, 1.6e9, 3.0e10, "quasar (earliest known)", [], 2021, False),
    ("QSO B1422+2309", 216.1587, 22.9335, SMBH, 3.0e8, 2.6e10, "lensed quasar (Einstein Cross)", ["B1422+231"], 1992, True),
    ("3C 279", 194.0465, -5.7893, SMBH, 1.0e9, 5.0e9, "blazar quasar", [], 1971, True),
    ("3C 454.3", 343.4906, 16.1482, SMBH, 2.0e9, 7.6e9, "blazar", [], 1977, True),
    ("4C 11.69", 338.1517, 11.7308, SMBH, 1.0e9, 1.0e10, "blazar", ["PKS 2230+114"], 1980, True),
    ("PKS 1510-089", 228.2106, -9.1000, SMBH, 3.0e8, 8.0e9, "blazar", ["QSO J1512-0906"], 1985, True),
    ("3C 120", 68.2962, 5.3543, SMBH, 5.5e7, 4.5e8, "Seyfert galaxy", ["MCG+01-12-009"], 1962, False),
    ("OJ 287", 133.7036, 20.1085, SMBH, 1.8e10, 3.5e9, "blazar (binary SMBH)", ["PG 0851+202"], 1970, True),
    ("BL Lac", 330.6804, 42.2778, SMBH, 1.7e8, 8.9e8, "blazar prototype", ["BL Lacertae"], 1929, True),
    ("Markarian 421", 166.1138, 38.2088, SMBH, 3.0e8, 4.3e8, "blazar", ["Mkn 421", "Z 184-50"], 1970, True),
    ("Markarian 501", 253.4676, 39.7602, SMBH, 1.0e9, 4.6e8, "blazar", ["Mkn 501", "Z 225-7"], 1970, True),
    ("PKS 2155-304", 329.7169, -30.2256, SMBH, 1.0e9, 1.5e9, "blazar", ["PKS J2158-3013"], 1976, True),
    # --- Stellar-mass ---
    ("Cygnus X-1", 299.5903, 35.2016, STELLAR, 21.2, 7240, "HMXB (HDE 226868)", ["Cyg X-1", "HD 226868"], 1964, False),
    ("V404 Cygni", 306.0159, 33.8672, STELLAR, 9.0, 7800, "LMXB (GS 2023+338)", ["V* V404 Cyg", "GS 2023+338"], 1989, False),
    ("GRS 1915+105", 288.7981, 10.9458, STELLAR, 12.4, 28000, "microquasar", ["Granat 1915+105"], 1992, False),
    ("GRO J1655-40", 253.5006, -39.8458, STELLAR, 6.3, 11000, "microquasar (V1033 Sco)", ["V* V1033 Sco"], 1994, False),
    ("A0620-00", 95.6854, -0.3458, STELLAR, 6.6, 3470, "LMXB (V616 Mon)", ["V616 Mon"], 1975, False),
    ("XTE J1118+480", 169.5450, 48.0368, STELLAR, 8.0, 6200, "LMXB (KV UMa)", ["KV UMa"], 2000, False),
    ("LMC X-1", 84.9118, -69.7432, STELLAR, 10.9, 163000, "HMXB (Large Magellanic Cloud)", ["X LMC X-1"], 1969, False),
    ("LMC X-3", 84.7360, -64.0843, STELLAR, 7.0, 163000, "HMXB (Large Magellanic Cloud)", ["X LMC X-3"], 1971, False),
    ("SS 433", 287.9565, 4.9827, STELLAR, 12.0, 18000, "microquasar", [], 1977, False),
    ("GX 339-4", 255.7058, -48.7897, STELLAR, 9.0, 26000, "LMXB (V821 Ara)", ["V821 Ara"], 1973, True),
    ("Cygnus X-3", 308.1074, 40.9577, STELLAR, 2.2, 24000, "HMXB (V1521 Cyg)", ["V1521 Cyg"], 1967, True),
    ("XTE J1550-564", 237.7444, -56.4765, STELLAR, 9.1, 17000, "LMXB (V381 Nor)", ["V381 Nor"], 1998, False),
    ("4U 1543-47", 236.7845, -47.6695, STELLAR, 9.4, 24000, "LMXB (IL Lupi)", ["IL Lup"], 1971, False),
    ("V4641 Sagittarii", 274.8401, -25.4072, STELLAR, 9.6, 24000, "microquasar (XTE J1819-254)", ["XTE J1819-254"], 1999, False),
    ("MAXI J1820+070", 275.0914, 7.1854, STELLAR, 8.5, 10000, "LMXB", [], 2018, True),
    ("H 1705-250", 257.0605, -25.0917, STELLAR, 6.0, 28000, "LMXB (V2107 Oph)", ["V2107 Oph"], 1977, True),
    ("XTE J1650-500", 252.5041, -49.9621, STELLAR, 9.7, 15000, "LMXB", [], 2001, True),
    ("GRS 1124-683", 171.6108, -68.6758, STELLAR, 6.9, 15000, "LMXB (GU Muscae)", ["GU Mus", "Nova Muscae 1991"], 1991, False),
    ("QZ Vulpeculae", 300.7063, 25.2363, STELLAR, 7.1, 8800, "LMXB (GS 2000+25)", ["GS 2000+25"], 1988, False),
    ("V518 Persei", 65.4280, 32.9075, STELLAR, 3.7, 8800, "LMXB (GRO J0422+32)", ["GRO J0422+32"], 1992, True),
    ("XTE J1859+226", 284.6729, 22.6583, STELLAR, 7.0, 18000, "LMXB (V406 Vul)", ["V406 Vul"], 1999, True),
    ("Swift J1357.2-0933", 209.3201, -9.5441, STELLAR, 6.0, 10000, "LMXB", [], 2011, True),
    ("MAXI J1305-704", 196.7304, -70.4514, STELLAR, 6.0, 27000, "LMXB", [], 2012, True),
    ("MAXI J1659-152", 254.7570, -15.2580, STELLAR, 5.0, 26000, "LMXB", [], 2010, True),
    ("IGR J17091-3624", 257.2817, -36.4071, STELLAR, 8.0, 28000, "LMXB", [], 2003, True),
    ("H 1743-322", 266.5650, -32.2336, STELLAR, 8.0, 26000, "LMXB (XTE J17464-3213)", ["XTE J17464-3213"], 1977, True),
    ("GRS 1739-278", 265.6668, -27.7480, STELLAR, 8.0, 26000, "LMXB (V2606 Oph)", ["V2606 Oph"], 1996, True),
    ("XTE J1752-223", 268.0629, -22.3423, STELLAR, 8.0, 34000, "LMXB", [], 2009, True),
    ("MAXI J1535-571", 233.8322, -57.2300, STELLAR, 8.0, 20000, "LMXB", [], 2017, True),
    ("1E 1740.7-2942", 265.9780, -29.7456, STELLAR, 8.0, 26000, "microquasar (Great Annihilator)", ["2E 3938"], 1984, True),
    ("GRS 1758-258", 270.3020, -25.7432, STELLAR, 8.0, 25000, "microquasar", [], 1990, True),
    ("BW Circini", 209.5405, -64.7348, STELLAR, 7.0, 32000, "LMXB", ["V* BW Cir"], 1987, True),
    ("SWIFT J1753.5-0127", 268.3679, -1.4517, STELLAR, 8.0, 26000, "LMXB", [], 2005, True),
    ("XTE J1908+094", 287.2212, 9.3847, STELLAR, 8.0, 26000, "LMXB", [], 2002, True),
    ("GRS 1009-45", 153.4014, -45.0753, STELLAR, 5.0, 15000, "LMXB (MM Velorum)", ["MM Vel"], 1993, True),
    ("XTE J2012+381", 303.1573, 38.1835, STELLAR, 8.0, 33000, "LMXB", [], 1998, True),
    ("MAXI J1543-564", 235.8223, -56.4136, STELLAR, 8.0, 25000, "LMXB", [], 2011, True),
    ("XTE J1720-318", 259.9958, -31.7503, STELLAR, 8.0, 26000, "LMXB (V1228 Sco)", ["V1228 Sco"], 2003, True),
    ("XTE J1748-288", 267.0211, -28.4738, STELLAR, 8.0, 26000, "LMXB", [], 1998, True),
]


def main():
    entries = []
    for (name, ra, de, kind, mass, dist, host, aliases, year, approx) in CATALOG:
        entries.append({
            "name": name,
            "ra": round(ra, 6),
            "de": round(de, 6),
            "kind": kind,
            "mass": mass,
            "dist": dist,
            "host": host,
            "aliases": aliases,
            "year": year,
            "approx": approx,
        })
    entries.sort(key=lambda e: e["name"].lower())
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=1, ensure_ascii=False)
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["name", "ra_deg", "dec_deg", "kind", "mass_msun", "dist_ly",
                    "host", "aliases", "year", "approx"])
        for e in entries:
            w.writerow([e["name"], e["ra"], e["de"], e["kind"], e["mass"], e["dist"],
                        e["host"], ";".join(e["aliases"]), e["year"], e["approx"]])
    print("wrote %d black holes -> %s" % (len(entries), OUT_JSON))


if __name__ == "__main__":
    main()
