"""
menu.py
Interaktives Menü zum Aufrufen aller EMV-Filter Visualisierungen
"""

import subprocess
import sys

def clear_screen():
    import os
    os.system('cls' if sys.platform == 'win32' else 'clear')

def show_menu():
    clear_screen()
    print("\n" + "╔" + "═"*68 + "╗")
    print("║" + " "*15 + "EMV-Filter Visualisierungs-Menü" + " "*21 + "║")
    print("╚" + "═"*68 + "╝\n")
    
    menu_items = [
        ("1", "📊 Haupt-Filter-Analyse (4 Plots)", "test_plot.py"),
        ("2", "🔧 Schaltbild & Komponenten-Erklärung", "schaltbild_und_erklarung.py"),
        ("3", "📈 Detaillierte Komponenten-Analyse (5 Plots)", "komponenten_vergleich.py"),
        ("4", "🎯 ALLE Visualisierungen nacheinander", "zeige_alle_graphen.py"),
        ("5", "🔄 Komplette Berechnung mit Ausgabe", "main.py"),
        ("0", "❌ Beenden", None),
    ]
    
    for choice, description, _ in menu_items:
        print(f"  {choice}. {description}")
    
    print("\n" + "─"*70)
    choice = input("  Wähle eine Option (0-5): ").strip()
    
    if choice == "0":
        print("\n  👋 Auf Wiedersehen!\n")
        sys.exit(0)
    
    script_map = {
        "1": "test_plot.py",
        "2": "schaltbild_und_erklarung.py",
        "3": "komponenten_vergleich.py",
        "4": "zeige_alle_graphen.py",
        "5": "main.py",
    }
    
    if choice in script_map:
        script = script_map[choice]
        print(f"\n  ⏳ Starte {script}...\n")
        try:
            subprocess.run([sys.executable, script], check=True)
        except subprocess.CalledProcessError as e:
            print(f"\n  ❌ Fehler: {e}\n")
            input("  Drücke Enter zum Zurückkehren...")
        except KeyboardInterrupt:
            print("\n  ⚠️  Abgebrochen.\n")
    else:
        print(f"\n  ❌ Ungültige Wahl. Bitte versuche es erneut.\n")
        input("  Drücke Enter zum Zurückkehren...")
    
    show_menu()

if __name__ == "__main__":
    show_menu()
