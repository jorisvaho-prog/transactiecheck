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


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Gebruik: python3 transactiecheck.py <bestand.csv>")
        sys.exit(1)

    bedragen = load_amounts(sys.argv[1])
    waargenomen, afwijkingen, mad = analyseer(bedragen)
    print_rapport(waargenomen, afwijkingen, mad)
