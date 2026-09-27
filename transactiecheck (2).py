"""
TransactieCheck — eerste versie
Controleert of de verdeling van eerste cijfers in een lijst transactiebedragen
afwijkt van de wet van Benford. Grote afwijkingen zijn een signaal om de
transacties manueel te bekijken (mogelijke fraude, manipulatie, of fouten).

Gebruik:
    python3 transactiecheck.py transactions.csv
"""

import csv
import math
import sys

# Verwachte proportie per eerste cijfer volgens de wet van Benford
BENFORD_EXPECTED = {d: math.log10(1 + 1 / d) for d in range(1, 10)}


def leading_digit(bedrag):
    """Geeft het eerste cijfer (1-9) van een positief bedrag terug."""
    bedrag = abs(bedrag)
    while bedrag < 1:
        bedrag *= 10
    while bedrag >= 10:
        bedrag /= 10
    return int(bedrag)


def load_amounts(pad):
    bedragen = []
    with open(pad, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for rij in reader:
            try:
                bedragen.append(float(rij["bedrag"]))
            except (KeyError, ValueError):
                continue
    return bedragen


def analyseer(bedragen):
    n = len(bedragen)
    if n == 0:
        raise ValueError("Geen geldige bedragen gevonden in het bestand.")

    tellingen = {d: 0 for d in range(1, 10)}
    for bedrag in bedragen:
        d = leading_digit(bedrag)
        if d in tellingen:
            tellingen[d] += 1

    waargenomen = {d: tellingen[d] / n for d in range(1, 10)}
    afwijkingen = {d: waargenomen[d] - BENFORD_EXPECTED[d] for d in range(1, 10)}
    mad = sum(abs(v) for v in afwijkingen.values()) / 9  # mean absolute deviation

    return waargenomen, afwijkingen, mad


def print_rapport(waargenomen, afwijkingen, mad):
    print(f"{'Cijfer':<8}{'Verwacht':<12}{'Waargenomen':<14}{'Afwijking'}")
    for d in range(1, 10):
        print(
            f"{d:<8}{BENFORD_EXPECTED[d]*100:>7.1f}%    "
            f"{waargenomen[d]*100:>7.1f}%     "
            f"{afwijkingen[d]*100:+.1f}%"
        )

    print(f"\nMean Absolute Deviation: {mad*100:.2f}%")

    # Drempel is bewust eenvoudig gehouden voor deze eerste versie.
    if mad > 0.02:
        print("Vlag: BEKIJK MANUEEL — afwijking groter dan verwacht.")
    else:
        print("Vlag: OK — verdeling volgt de wet van Benford.")


def genereer_html_rapport(waargenomen, afwijkingen, mad, pad="rapport.html"):
    """Schrijft een klein visueel rapport weg als HTML-bestand."""
    vlag = "BEKIJK MANUEEL" if mad > 0.02 else "OK"
    kleur = "#9c4a3c" if mad > 0.02 else "#3e6e68"

    balken = ""
    max_pct = max(max(waargenomen.values()), max(BENFORD_EXPECTED.values())) * 100
    for d in range(1, 10):
        verwacht_pct = BENFORD_EXPECTED[d] * 100
        waarg_pct = waargenomen[d] * 100
        balken += f"""
        <div class="rij">
          <span class="cijfer">{d}</span>
          <div class="balk-verwacht" style="width:{verwacht_pct/max_pct*100:.1f}%"></div>
          <div class="balk-waarg" style="width:{waarg_pct/max_pct*100:.1f}%"></div>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="nl"><head><meta charset="UTF-8">
<title>TransactieCheck rapport</title>
<style>
  body {{ font-family: sans-serif; max-width: 480px; margin: 2rem auto; }}
  .rij {{ display:flex; align-items:center; gap:6px; margin-bottom:6px; }}
  .cijfer {{ width:1rem; }}
  .balk-verwacht {{ height:8px; background:#ccc; }}
  .balk-waarg {{ height:8px; background:{kleur}; }}
  .vlag {{ font-weight:bold; color:{kleur}; }}
</style></head>
<body>
  <h2>TransactieCheck rapport</h2>
  <p>Grijs = verwacht (Benford), gekleurd = waargenomen.</p>
  {balken}
  <p>Mean Absolute Deviation: {mad*100:.2f}%</p>
  <p class="vlag">Vlag: {vlag}</p>
</body></html>"""

    with open(pad, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML-rapport geschreven naar {pad}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Gebruik: python3 transactiecheck.py <bestand.csv>")
        sys.exit(1)

    bedragen = load_amounts(sys.argv[1])
    waargenomen, afwijkingen, mad = analyseer(bedragen)
    print_rapport(waargenomen, afwijkingen, mad)
    genereer_html_rapport(waargenomen, afwijkingen, mad)
