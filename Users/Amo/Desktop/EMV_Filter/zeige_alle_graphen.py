"""
zeige_alle_graphen.py
Master-Skript: Ruft alle Visualisierungen auf einmal auf
"""

import subprocess
import sys

print("\n" + "="*70)
print("  EMV-Filter: Alle Visualisierungen aufrufen")
print("="*70 + "\n")

scripts = [
    ("filter_plot.py", "Haupt-Filter-Analyse (4 Plots)"),
    ("schaltbild_und_erklarung.py", "Schaltbild & Komponenten-Erklärung"),
    ("komponenten_vergleich.py", "Detaillierte Komponenten-Analyse (5 Plots)"),
]

print("📊 Starte alle Visualisierungen...\n")

for i, (script, description) in enumerate(scripts, 1):
    print(f"[{i}/3] {description}")
    print(f"     → Starte {script}...")
    try:
        subprocess.run([sys.executable, script], check=True)
        print(f"     ✅ {script} fertig!\n")
    except subprocess.CalledProcessError as e:
        print(f"     ❌ Fehler bei {script}: {e}\n")

print("="*70)
print("✅ Alle Visualisierungen abgeschlossen!")
print("="*70)
print("\nGenerierte Dateien:")
print("  1. emv_filter_auslegung.png          - Haupt-4-Plots")
print("  2. emv_schaltung_erklaerung.png      - Schaltbild & Erklärung")
print("  3. emv_komponenten_detailanalyse.png - Komponenten-Details")
print("\n")
