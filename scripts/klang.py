"""Musik für die Reels, komplett hier im Skript erzeugt.

Keine Samples, keine fremden Aufnahmen: jeder Ton wird aus Sinuswellen und Rauschen berechnet.
Die Musik gehört damit Pascal, es gibt keine Urheberrechte Dritter und keine Content-ID-Treffer.

Aufbau (synchron zu den Szenen des Reels, 120 bpm):
  Einstieg      dunkel, Herzschlag-Kick, leises Ticken, Riser in den Drop
  ab 1. Schnitt voller Beat: Kick, Clap, Hi-Hats, pumpender Bass, Arpeggio
  jeder Schnitt Whoosh davor, Einschlag darauf
  Ende          letzter Einschlag mit Nachhall

Stimmung nach Ampel: gruen = Dur und hell, gelb = schwebend (sus), rot = Moll, dunkel, mehr Druck.
Tonart und Melodie werden aus dem Datum abgeleitet: jeder Tag klingt etwas anders, derselbe Tag immer gleich.

  python scripts/klang.py rot 20 aus.wav [seed] [schnitt1,schnitt2,...]
"""
import hashlib
import math
import sys
import wave

import numpy as np

SR = 48000
BPM = 120
SCHLAG = 60 / BPM

# Akkorde als Tonklassen relativ zur Tonart, dazu der Basston (relativ). Ein Akkord je Takt.
STIMMUNGEN = {
    "gruen": {
        "akkorde": [({0, 4, 7, 11}, 0), ({7, 11, 2}, 7), ({9, 0, 4, 7}, 9), ({5, 9, 0, 4}, 5)],
        "hell": 7.0, "pad_lage": 64, "arp_lage": 76, "clap": 0.30, "hat": 0.085, "boom": 0.6, "herz": False,
    },
    "gelb": {
        "akkorde": [({0, 2, 7}, 0), ({8, 0, 3, 7}, 8), ({3, 7, 10, 2}, 3), ({10, 2, 5}, 10)],
        "hell": 5.0, "pad_lage": 62, "arp_lage": 74, "clap": 0.27, "hat": 0.08, "boom": 0.8, "herz": False,
    },
    "rot": {
        "akkorde": [({0, 3, 7}, 0), ({8, 0, 3}, 8), ({5, 8, 0}, 5), ({7, 11, 2, 5}, 7)],
        "hell": 3.5, "pad_lage": 58, "arp_lage": 70, "clap": 0.24, "hat": 0.07, "boom": 1.0, "herz": True,
    },
}

MUSTER = [[0, 1, 2, 3], [0, 2, 1, 3], [0, 1, 2, 1], [0, 2, 3, 2], [3, 2, 1, 0]]


def ton(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def stimme(tonklassen, zentrum):
    """Jede Tonklasse in die Oktave um das Zentrum legen (enge Lage)."""
    aus = []
    for pc in tonklassen:
        m = zentrum + ((pc - zentrum) % 12)
        if m - zentrum > 6:
            m -= 12
        aus.append(m)
    return sorted(aus)


def huelle(n, an, ab):
    """Weiches Ein- und Ausblenden (sin²) über an/ab Sekunden."""
    h = np.ones(n)
    a, b = min(n, int(an * SR)), min(n, int(ab * SR))
    if a:
        h[:a] = np.sin(np.linspace(0, np.pi / 2, a)) ** 2
    if b:
        h[n - b:] *= np.cos(np.linspace(0, np.pi / 2, b)) ** 2
    return h


def legen(spur, sek, klang):
    """Klang ab Sekunde sek in die Spur addieren (mono oder stereo), am Ende abschneiden."""
    start = int(round(sek * SR))
    if start >= len(spur) or start < 0:
        return
    k = klang[: len(spur) - start]
    if k.ndim == 1 and spur.ndim == 2:
        k = np.stack([k, k], axis=1)
    spur[start: start + len(k)] += k


def pan(mono, p):
    """p von -1 (links) bis +1 (rechts), gleiche Lautheit."""
    w = (p + 1) * np.pi / 4
    return np.stack([mono * np.cos(w), mono * np.sin(w)], axis=1)


def tiefpass(x, cutoff):
    """Einpoliger Tiefpass; cutoff als Zahl oder als Verlauf (Array) in Hz."""
    c = np.broadcast_to(np.asarray(cutoff, dtype=float), x.shape)
    a = 1 - np.exp(-2 * np.pi * c / SR)
    y = np.empty_like(x)
    z = 0.0
    for i in range(len(x)):
        z += a[i] * (x[i] - z)
        y[i] = z
    return y


# ---------- Instrumente ----------

def kick(staerke=1.0):
    n = int(0.4 * SR)
    t = np.arange(n) / SR
    f = 48 + 115 * np.exp(-t / 0.028)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.2)
    klick = np.random.default_rng(7).normal(size=n) * np.exp(-t / 0.0025) * 0.25
    return np.tanh((s + klick) * 1.6) * huelle(n, 0.001, 0.04) * staerke


def clap(rng):
    n = int(0.3 * SR)
    t = np.arange(n) / SR
    r = rng.normal(size=n + 1)
    r = np.diff(np.convolve(r, np.ones(3) / 3, mode="same"))  # mittlere Frequenzen
    h = 0.6 * np.exp(-np.maximum(t - 0.022, 0) / 0.09) * (t >= 0.022)
    for off in (0.0, 0.011, 0.022):
        h += np.exp(-np.maximum(t - off, 0) / 0.006) * (t >= off)
    return r * h * 0.5


def hat(rng, offen=False):
    n = int((0.25 if offen else 0.06) * SR)
    t = np.arange(n) / SR
    r = np.diff(rng.normal(size=n + 1))  # einmal ableiten = Hochpass, aber nicht schrill
    r = np.convolve(r, np.ones(2) / 2, mode="same")
    return r * np.exp(-t / (0.11 if offen else 0.018)) * 0.35


def sub(f, n):
    t = np.arange(n) / SR
    return np.tanh(1.4 * np.sin(2 * np.pi * f * t)) * huelle(n, 0.004, 0.03)


def zupf(f, rng, dauer=0.45):
    """Gezupfter Synth: obere Obertöne klingen schneller ab als der Grundton."""
    n = int(dauer * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for k in range(1, 8):
        if f * k > 10000:
            break
        s += np.sin(2 * np.pi * f * k * t + rng.uniform(0, 6.28)) / k * np.exp(-t / (0.32 / k ** 0.8))
    return s * huelle(n, 0.002, 0.05)


def teppich(freqs, n, hell, rng):
    """Weiche Klangfläche: je Ton drei leicht verstimmte Stimmen aus Obertönen."""
    t = np.arange(n) / SR
    # Eine Schwingung als Tabelle vorberechnen (schnell); 12 Obertöne bleiben bei Pad-Lagen unter 9 kHz
    tab_n = 4096
    x = np.arange(tab_n) / tab_n
    tabelle = sum(np.sin(2 * np.pi * k * x) * np.exp(-k / hell) / k for k in range(1, 13))
    l, r = np.zeros(n), np.zeros(n)
    for f in freqs:
        for cent, p in ((-8, -0.7), (0, 0.0), (8, 0.7)):
            ff = f * 2 ** (cent / 1200)
            phase = (ff * t + rng.uniform(0, 1)) % 1.0
            s = tabelle[(phase * tab_n).astype(np.int64)]
            w = (p + 1) * np.pi / 4
            l += s * np.cos(w)
            r += s * np.sin(w)
    g = 1 / (len(freqs) * 3)
    return np.stack([l * g, r * g], axis=1)


def riser(dauer, rng, staerke=1.0):
    """Ansteigendes Rauschen mit sich öffnendem Filter und steigendem Ton: baut Spannung vor dem Drop auf."""
    n = int(dauer * SR)
    t = np.arange(n) / SR
    x = t / dauer
    rauschen = tiefpass(rng.normal(size=n), 250 * (40 ** x))
    f = 180 * (6 ** x)
    sweep = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25
    return pan((rauschen * 1.6 + sweep) * x ** 2.2, 0) * staerke


def whoosh(rng, dauer=0.45):
    """Kurzer Luftzug vor einem Schnitt, wandert von links nach rechts."""
    n = int(dauer * SR)
    t = np.arange(n) / SR
    x = t / dauer
    r = tiefpass(rng.normal(size=n), 400 * (15 ** x)) * np.sin(np.pi * x) ** 2 * 1.4
    w = x * np.pi / 2
    return np.stack([r * np.cos(w), r * np.sin(w)], axis=1)


def einschlag(rng, boom=1.0):
    """Schlag auf den Schnitt: Kick, tiefer Boom, kurzes Crash-Rauschen."""
    n = int(1.6 * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    k = kick(1.3)
    s[: len(k)] += k
    s += np.sin(2 * np.pi * np.cumsum(36 + 30 * np.exp(-t / 0.08)) / SR) * np.exp(-t / 0.7) * 0.7 * boom
    crash = np.diff(rng.normal(size=n + 1)) * np.exp(-t / 0.35) * 0.07
    return s, crash


def hall(x, rng, dauer=2.4, abfall=0.55):
    """Raumhall per Faltung mit abklingendem Rauschen (links und rechts verschieden)."""
    n = int(dauer * SR)
    t = np.arange(n) / SR
    aus = np.zeros_like(x)
    m = 1 << int(math.ceil(math.log2(len(x) + n)))
    for c in range(2):
        ir = rng.normal(size=n) * np.exp(-t / abfall)
        ir = np.convolve(ir, np.ones(8) / 8, mode="same")
        ir[: int(0.015 * SR)] = 0
        ir /= np.sqrt(np.sum(ir ** 2))
        y = np.fft.irfft(np.fft.rfft(x[:, c], m) * np.fft.rfft(ir, m), m)
        aus[:, c] = y[: len(x)]
    return aus


# ---------- Arrangement ----------

def erzeugen(stimmung, sekunden, seed="aktienampel", schnitte=None):
    """schnitte: Sekunden, an denen das Video die Szene wechselt (erster Schnitt = Drop)."""
    cfg = STIMMUNGEN[stimmung]
    rng = np.random.default_rng(int.from_bytes(hashlib.sha256(f"{seed}:{stimmung}".encode()).digest()[:8], "big"))
    schnitte = sorted(s for s in (schnitte or [4.0]) if 0 < s < sekunden)
    drop = schnitte[0] if schnitte else min(4.0, sekunden / 3)
    ende_beat = sekunden - 1.0  # danach nur noch der Schlussakkord
    tonart = int(rng.integers(0, 12))
    bass_grund = 33 + (tonart % 9)  # A1 bis F2
    muster = MUSTER[int(rng.integers(0, len(MUSTER)))]
    n = int(sekunden * SR)
    takt = 4 * SCHLAG

    trocken = np.zeros((n, 2))
    send = np.zeros((n, 2))
    bass_spur = np.zeros(n)
    pad_spur = np.zeros((n, 2))
    kicks = []

    for a in range(int(math.ceil(sekunden / takt))):
        t0 = a * takt
        tonklassen, grund = cfg["akkorde"][a % len(cfg["akkorde"])]
        tk = {(tonart + p) % 12 for p in tonklassen}
        voll = t0 >= drop - 1e-6

        # Klangfläche, überlappt in den nächsten Takt
        lang = int((takt + 1.2) * SR)
        p = teppich([ton(m) for m in stimme(tk, cfg["pad_lage"])], lang, cfg["hell"] * (1.0 if voll else 0.6), rng)
        legen(pad_spur, t0, p * huelle(lang, 0.25 if voll else 0.8, 1.0)[:, None])

        bm = bass_grund + grund
        bf = ton(bm - 12 if bm > 44 else bm)
        arp = stimme(tk, cfg["arp_lage"])
        while len(arp) < 4:
            arp.append(arp[len(arp) % max(1, len(arp))] + 12)

        for s16 in range(16):
            t = t0 + s16 * SCHLAG / 4
            if t >= ende_beat:
                break
            schlag, rest = divmod(s16, 4)
            if voll:
                if rest == 0:
                    kicks.append(t)
                    legen(trocken, t, pan(kick(), 0) * 0.85)
                if rest == 0 and schlag in (1, 3):
                    legen(trocken, t, pan(clap(rng), 0.05) * cfg["clap"])
                    legen(send, t, pan(clap(rng), 0) * cfg["clap"] * 0.5)
                if rest == 2:
                    legen(trocken, t, pan(hat(rng, offen=(schlag == 3)), 0.3) * cfg["hat"] * 1.4)
                elif rest in (1, 3):
                    legen(trocken, t, pan(hat(rng), -0.3) * cfg["hat"] * 0.55)
                if rest % 2 == 0:  # Bass in Achteln
                    legen(bass_spur, t, sub(bf * (2 if rest == 2 else 1), int(SCHLAG / 2 * SR * 0.9)) * 0.5)
                m = arp[muster[s16 % 4]] + (12 if s16 % 8 == 7 else 0)
                z = zupf(ton(m), rng) * (0.20 if rest == 0 else 0.13)
                legen(trocken, t, pan(z, 0.35 if s16 % 2 else -0.35))
                legen(send, t, pan(z, 0) * 0.5)
            else:
                # Einstieg: Herzschlag oder Kick auf 1 und 3, leises Ticken, Arpeggio in Achteln
                if rest == 0 and schlag in (0, 2):
                    kicks.append(t)
                    legen(trocken, t, pan(kick(0.8), 0) * 0.7)
                    if cfg["herz"]:
                        legen(trocken, t + 0.16, pan(kick(0.45), 0) * 0.7)
                if rest in (1, 3):
                    legen(trocken, t, pan(hat(rng), 0.4 if rest == 1 else -0.4) * cfg["hat"] * 0.45)
                if rest == 0 and schlag in (0, 2):
                    legen(bass_spur, t, sub(bf, int(SCHLAG * 2 * SR * 0.95)) * huelle(int(SCHLAG * 2 * SR * 0.95), 0.05, 0.3) * 0.45)
                if rest % 2 == 0 and t > 0.9:
                    m = arp[muster[(s16 // 2) % 4]]
                    z = zupf(ton(m), rng) * 0.10 * min(1.0, t / max(drop, 0.1) + 0.3)
                    legen(trocken, t, pan(z, -0.3 if s16 % 4 else 0.3))
                    legen(send, t, pan(z, 0) * 0.7)

    # Riser in den Drop, Whoosh vor jedem weiteren Schnitt, Einschlag auf jeden Schnitt
    r_dauer = min(1.8, drop)
    legen(trocken, drop - r_dauer, riser(r_dauer, rng) * 0.32)
    for i, s in enumerate(schnitte):
        if i:
            legen(trocken, s - 0.45, whoosh(rng) * 0.30)
        e, crash = einschlag(rng, cfg["boom"])
        legen(trocken, s, pan(e, 0) * 0.75)
        legen(send, s, pan(e, 0) * 0.25 + pan(crash, 0.0))
        kicks.append(s)
    # Schluss: Einschlag und ausklingender Akkord
    e, crash = einschlag(rng, cfg["boom"])
    legen(trocken, ende_beat, pan(e, 0) * 0.8)
    legen(send, ende_beat, pan(e, 0) * 0.35 + pan(crash, 0))
    kicks.append(ende_beat)

    # Pumpen: Bass und Fläche ducken sich unter jeden Kick (Sidechain)
    t = np.arange(n) / SR
    duck = np.ones(n)
    for k in kicks:
        i = int(k * SR)
        m = min(n - i, int(0.35 * SR))
        if m > 0:
            duck[i: i + m] = np.minimum(duck[i: i + m], 1 - 0.75 * np.exp(-t[:m] / 0.11))
    trocken += pan(bass_spur * duck, 0) * 0.9
    pad = pad_spur * duck[:, None]
    trocken += pad * 0.30
    send += pad * 0.25

    mix = trocken + hall(send, rng) * 0.45

    # sanft die Höhen abrunden, damit nichts schrill klingt
    mix = np.stack([tiefpass(mix[:, c], 8500) for c in range(2)], axis=1)
    mix -= mix.mean(axis=0)
    rms = np.sqrt(np.mean(mix ** 2))
    mix *= 0.115 / max(rms, 1e-9)
    mix = np.tanh(mix * 1.2) / 1.2
    spitze = np.max(np.abs(mix))
    if spitze > 0.9:
        mix *= 0.9 / spitze
    mix *= huelle(n, 0.02, 0.6)[:, None]
    return mix, {"bpm": BPM, "tonart": tonart, "stimmung": stimmung}


def speichern(mix, pfad):
    daten = (np.clip(mix, -1, 1) * 32767).astype("<i2")
    with wave.open(pfad, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(daten.tobytes())


def stimmung_aus(d):
    """Ampel aus dem Mittel der Skalen-Folien (Qualität, Timing) einer Karussell-Datei."""
    werte = [s["wert"] for s in d.get("slides", []) if s.get("typ") == "skala" and isinstance(s.get("wert"), (int, float))]
    if not werte:
        return "gelb"
    m = sum(werte) / len(werte)
    return "gruen" if m >= 60 else "gelb" if m >= 45 else "rot"


if __name__ == "__main__":
    st, sek, aus = sys.argv[1], float(sys.argv[2]), sys.argv[3]
    seed = sys.argv[4] if len(sys.argv) > 4 else "aktienampel"
    schn = [float(x) for x in sys.argv[5].split(",")] if len(sys.argv) > 5 else None
    mix, info = erzeugen(st, sek, seed, schn)
    speichern(mix, aus)
    print(aus, info)
