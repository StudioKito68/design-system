#!/usr/bin/env python3
"""Planche « croquis annoté » Studio Kito.

Prend un croquis (PNG/JPG, généré sans texte par une IA image) et une
spécification JSON, puis compose une planche A4/A3 prête à envoyer au client :
croquis centré, annotations manuscrites reliées par des traits de rappel,
cotes éventuelles et cartouche Studio Kito.

Usage :
    python annotate.py spec.json                 # -> planche.pdf + planche.png
    python annotate.py spec.json -o sortie/      # dossier de sortie
    python annotate.py --grille croquis.png      # -> croquis_grille.png (repérage des ancres)

Dépendance : Pillow (pip install pillow).
"""

import argparse
import json
import math
import os
import random
import sys
import zlib

from PIL import Image, ImageDraw, ImageFont

DPI = 300
FORMATS_MM = {"A4": (297, 210), "A3": (420, 297)}

ICI = os.path.dirname(os.path.abspath(__file__))
DOSSIER_POLICES = os.path.join(ICI, "..", "assets", "fonts")

# Police manuscrite : d'abord assets/fonts/, puis polices système macOS / Linux.
POLICES_MANUSCRITES = [
    os.path.join(DOSSIER_POLICES, "Caveat-Regular.ttf"),
    os.path.join(DOSSIER_POLICES, "Caveat[wght].ttf"),
    os.path.join(DOSSIER_POLICES, "manuscrite.ttf"),
    "/System/Library/Fonts/Supplemental/Bradley Hand Bold.ttf",
    "/System/Library/Fonts/Noteworthy.ttc",
    "/System/Library/Fonts/Supplemental/Chalkboard.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]
POLICES_TITRE = [
    os.path.join(DOSSIER_POLICES, "titre.ttf"),
    "/System/Library/Fonts/Supplemental/Futura.ttc",
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]
POLICES_TEXTE = [
    os.path.join(DOSSIER_POLICES, "texte.ttf"),
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]

ENCRE = (43, 43, 43)
ENCRE_CLAIRE = (100, 100, 100)
PAPIER = (253, 251, 247)


def police(candidats, taille):
    for chemin in candidats:
        if os.path.exists(chemin):
            try:
                return ImageFont.truetype(chemin, taille)
            except OSError:
                continue
    print("⚠ Aucune police TrueType trouvée, police par défaut utilisée.", file=sys.stderr)
    return ImageFont.load_default()


def hex_rgb(valeur, defaut):
    if not valeur:
        return defaut
    valeur = valeur.lstrip("#")
    return tuple(int(valeur[i:i + 2], 16) for i in (0, 2, 4))


def mm(v):
    return int(round(v / 25.4 * DPI))


def largeur_texte(draw, texte, fnt):
    x0, _, x1, _ = draw.textbbox((0, 0), texte, font=fnt)
    return x1 - x0


def couper(draw, texte, fnt, largeur_max):
    """Retour à la ligne simple au mot."""
    lignes = []
    for paragraphe in texte.split("\n"):
        courant = ""
        for mot in paragraphe.split():
            essai = (courant + " " + mot).strip()
            if largeur_texte(draw, essai, fnt) <= largeur_max or not courant:
                courant = essai
            else:
                lignes.append(courant)
                courant = mot
        lignes.append(courant)
    return lignes


def trait_main_levee(draw, p0, p1, couleur, epaisseur, graine):
    """Trait légèrement ondulé, comme tracé au feutre fin."""
    rnd = random.Random(graine)
    (x0, y0), (x1, y1) = p0, p1
    longueur = math.hypot(x1 - x0, y1 - y0)
    if longueur < 1:
        return
    n = max(8, int(longueur / 25))
    nx, ny = -(y1 - y0) / longueur, (x1 - x0) / longueur
    amplitude = min(6.0, longueur * 0.006)
    phase, freq = rnd.uniform(0, math.pi), rnd.uniform(1.2, 2.2)
    points = []
    for i in range(n + 1):
        t = i / n
        d = amplitude * math.sin(phase + t * freq * math.pi) * math.sin(t * math.pi)
        points.append((x0 + (x1 - x0) * t + nx * d, y0 + (y1 - y0) * t + ny * d))
    draw.line(points, fill=couleur, width=epaisseur, joint="curve")


def point_ancre(draw, centre, rayon, couleur):
    x, y = centre
    draw.ellipse((x - rayon, y - rayon, x + rayon, y + rayon), fill=couleur)


def texte_tourne(page, texte, fnt, couleur, centre, angle_deg):
    boite = ImageDraw.Draw(page).textbbox((0, 0), texte, font=fnt)
    w, h = boite[2] - boite[0] + 20, boite[3] - boite[1] + 20
    calque = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(calque).text((10 - boite[0], 10 - boite[1]), texte, font=fnt, fill=couleur)
    calque = calque.rotate(angle_deg, expand=True, resample=Image.BICUBIC)
    page.paste(calque, (int(centre[0] - calque.width / 2), int(centre[1] - calque.height / 2)), calque)


def repartir(elements, haut, bas, ecart):
    """Place des étiquettes (y souhaité, hauteur) sans chevauchement dans [haut, bas]."""
    elements.sort(key=lambda e: e["y_souhaite"])
    y = haut
    for e in elements:
        e["y"] = max(e["y_souhaite"] - e["h"] / 2, y)
        y = e["y"] + e["h"] + ecart
    # Si ça déborde en bas, on remonte depuis le bas.
    limite = bas
    for e in reversed(elements):
        if e["y"] + e["h"] > limite:
            e["y"] = limite - e["h"]
        limite = e["y"] - ecart
    if elements and elements[0]["y"] < haut:
        print("⚠ Trop d'annotations pour la hauteur disponible : réduire le texte ou passer en A3.",
              file=sys.stderr)


def composer(spec, dossier_spec):
    fmt = spec.get("format", "A4").upper()
    if fmt not in FORMATS_MM:
        raise SystemExit(f"Format inconnu : {fmt} (A4 ou A3)")
    w_mm, h_mm = FORMATS_MM[fmt]
    if spec.get("orientation", "paysage").lower().startswith("portrait"):
        w_mm, h_mm = h_mm, w_mm
    W, H = mm(w_mm), mm(h_mm)
    echelle = H / mm(210) if w_mm > h_mm else W / mm(210)  # tailles relatives à un A4

    accent = hex_rgb(spec.get("couleur_accent"), (181, 86, 60))
    page = Image.new("RGB", (W, H), PAPIER)
    draw = ImageDraw.Draw(page)

    marge = mm(10)
    h_cartouche = int(mm(20) * echelle)
    zone_haut, zone_bas = marge, H - marge - h_cartouche - mm(4)

    f_titre_ann = police(POLICES_MANUSCRITES, int(62 * echelle))
    f_detail_ann = police(POLICES_MANUSCRITES, int(46 * echelle))
    f_cote = police(POLICES_MANUSCRITES, int(50 * echelle))

    annotations = spec.get("annotations", [])
    for a in annotations:
        cote = a.get("cote", "auto").lower()
        a["_cote"] = cote if cote in ("gauche", "droite") else ("gauche" if a["ancre"][0] < 0.5 else "droite")
    a_gauche = any(a["_cote"] == "gauche" for a in annotations)
    a_droite = any(a["_cote"] == "droite" for a in annotations)

    l_colonne = int(W * float(spec.get("largeur_colonne", 0.2)))
    ecart_col = mm(6)
    x_zone0 = marge + (l_colonne + ecart_col if a_gauche else 0)
    x_zone1 = W - marge - (l_colonne + ecart_col if a_droite else 0)

    # --- Croquis ---
    chemin_img = spec["image"]
    if not os.path.isabs(chemin_img):
        chemin_img = os.path.join(dossier_spec, chemin_img)
    croquis = Image.open(chemin_img).convert("RGB")
    # Rognage optionnel [x0, y0, x1, y1] en fractions de l'image source.
    # Les ancres restent exprimées dans le repère de l'image source (celui de --grille).
    rognage = spec.get("rognage") or [0, 0, 1, 1]
    if rognage != [0, 0, 1, 1]:
        cw, ch = croquis.size
        croquis = croquis.crop((int(rognage[0] * cw), int(rognage[1] * ch),
                                int(rognage[2] * cw), int(rognage[3] * ch)))
    zw, zh = x_zone1 - x_zone0, zone_bas - zone_haut
    ratio = min(zw / croquis.width, zh / croquis.height)
    iw, ih = int(croquis.width * ratio), int(croquis.height * ratio)
    croquis = croquis.resize((iw, ih), Image.LANCZOS)
    ix, iy = x_zone0 + (zw - iw) // 2, zone_haut + (zh - ih) // 2
    page.paste(croquis, (ix, iy))

    def vers_page(p):
        u = (p[0] - rognage[0]) / (rognage[2] - rognage[0])
        v = (p[1] - rognage[1]) / (rognage[3] - rognage[1])
        return ix + u * iw, iy + v * ih

    # --- Annotations ---
    interligne = int(8 * echelle)
    for cote in ("gauche", "droite"):
        groupe = [a for a in annotations if a["_cote"] == cote]
        for a in groupe:
            lignes_t = couper(draw, a["texte"], f_titre_ann, l_colonne)
            lignes_d = couper(draw, a["detail"], f_detail_ann, l_colonne) if a.get("detail") else []
            h_t = f_titre_ann.size + interligne
            h_d = f_detail_ann.size + interligne
            a.update(_lt=lignes_t, _ld=lignes_d, _ht=h_t, _hd=h_d,
                     h=len(lignes_t) * h_t + len(lignes_d) * h_d,
                     y_souhaite=vers_page([0, a.get("etiquette_y", a["ancre"][1])])[1])
        repartir(groupe, zone_haut, zone_bas, int(mm(4) * echelle))

        for i, a in enumerate(groupe):
            aligne_droite = cote == "gauche"
            x_bord = marge + l_colonne if aligne_droite else W - marge - l_colonne
            y = a["y"]
            for ligne in a["_lt"]:
                lw = largeur_texte(draw, ligne, f_titre_ann)
                draw.text((x_bord - lw if aligne_droite else x_bord, y), ligne, font=f_titre_ann, fill=ENCRE)
                y += a["_ht"]
            for ligne in a["_ld"]:
                lw = largeur_texte(draw, ligne, f_detail_ann)
                draw.text((x_bord - lw if aligne_droite else x_bord, y), ligne, font=f_detail_ann, fill=ENCRE_CLAIRE)
                y += a["_hd"]
            # Trait de rappel : du milieu de la première ligne jusqu'à l'ancre.
            y_depart = a["y"] + a["_ht"] * 0.6
            x_depart = x_bord + (mm(2) if aligne_droite else -mm(2))
            ancre = vers_page(a["ancre"])
            trait_main_levee(draw, (x_depart, y_depart), ancre, ENCRE, max(3, int(4 * echelle)),
                             graine=zlib.crc32(f"{cote}{i}{a['texte']}".encode()))
            point_ancre(draw, ancre, int(9 * echelle), accent)

    # --- Cotes ---
    for k, c in enumerate(spec.get("cotes", [])):
        p0, p1 = vers_page(c["de"]), vers_page(c["a"])
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        dec = float(c.get("decalage", 0.04)) * max(iw, ih)
        q0 = (p0[0] + nx * dec, p0[1] + ny * dec)
        q1 = (p1[0] + nx * dec, p1[1] + ny * dec)
        ep = max(2, int(3 * echelle))
        for p, q in ((p0, q0), (p1, q1)):  # lignes d'attache
            draw.line([(p[0] + nx * mm(1), p[1] + ny * mm(1)),
                       (q[0] + nx * mm(1.5), q[1] + ny * mm(1.5))], fill=ENCRE_CLAIRE, width=ep - 1)
        trait_main_levee(draw, q0, q1, ENCRE, ep, graine=1000 + k)
        t = mm(1.6)
        for q in (q0, q1):  # petits traits obliques façon architecte
            ux, uy = (dx / L + nx) * t, (dy / L + ny) * t
            draw.line([(q[0] - ux, q[1] - uy), (q[0] + ux, q[1] + uy)], fill=ENCRE, width=ep + 1)
        angle = -math.degrees(math.atan2(dy, dx))
        if angle > 90 or angle < -90:
            angle += 180
        milieu = ((q0[0] + q1[0]) / 2 + nx * mm(4), (q0[1] + q1[1]) / 2 + ny * mm(4))
        texte = str(c["texte"]).strip()
        if texte.replace(" ", "").replace(",", "").isdigit():  # nombre seul : cm par convention
            texte += " cm"
        texte_tourne(page, texte, f_cote, ENCRE, milieu, angle)

    # --- Cartouche ---
    y_c = H - marge - h_cartouche
    draw.line([(marge, y_c), (W - marge, y_c)], fill=ENCRE, width=3)
    f_marque = police(POLICES_TITRE, int(44 * echelle))
    f_petit = police(POLICES_TEXTE, int(26 * echelle))
    f_titre = police(POLICES_MANUSCRITES, int(74 * echelle))
    pad = mm(3)

    marque = " ".join(spec.get("marque", "STUDIO KITO"))
    signature = spec.get("signature", "Conception & fabrication de mobilier sur mesure")
    draw.text((marge, y_c + pad), marque, font=f_marque, fill=ENCRE)
    draw.text((marge, y_c + pad + f_marque.size + mm(1.5)), signature, font=f_petit, fill=ENCRE_CLAIRE)
    l_gauche = max(largeur_texte(draw, marque, f_marque), largeur_texte(draw, signature, f_petit))

    infos = [v for v in (spec.get("date"), spec.get("version") and f"Version {spec['version']}") if v]
    infos.append(spec.get("mention", "Croquis d'intention – non contractuel"))
    y = y_c + pad
    l_droite = 0
    for ligne in infos:
        lw = largeur_texte(draw, ligne, f_petit)
        l_droite = max(l_droite, lw)
        draw.text((W - marge - lw, y), ligne, font=f_petit, fill=ENCRE_CLAIRE)
        y += f_petit.size + mm(1.2)

    # Titre centré entre les deux blocs, réduit si nécessaire pour ne rien chevaucher.
    x_c0, x_c1 = marge + l_gauche + mm(6), W - marge - l_droite - mm(6)
    titre = spec.get("titre", "")
    taille = f_titre.size
    while taille > 20 and largeur_texte(draw, titre, f_titre) > x_c1 - x_c0:
        taille -= 2
        f_titre = police(POLICES_MANUSCRITES, taille)
    sous_titre = " · ".join(v for v in (spec.get("projet"), spec.get("client") and f"Client : {spec['client']}") if v)
    centre = (x_c0 + x_c1) / 2
    tw = largeur_texte(draw, titre, f_titre)
    draw.text((centre - tw / 2, y_c + pad - mm(1)), titre, font=f_titre, fill=ENCRE)
    if sous_titre:
        ligne = couper(draw, sous_titre, f_petit, x_c1 - x_c0)[0]  # une seule ligne dans le cartouche
        sw = largeur_texte(draw, ligne, f_petit)
        draw.text((centre - sw / 2, y_c + pad + f_titre.size + mm(0.5)), ligne, font=f_petit, fill=ENCRE_CLAIRE)

    return page


def grille(chemin, pas=10):
    """Superpose une grille graduée 0–1 pour repérer les coordonnées des ancres."""
    img = Image.open(chemin).convert("RGB")
    draw = ImageDraw.Draw(img, "RGBA")
    w, h = img.size
    fnt = police(POLICES_TEXTE, max(12, w // 70))
    for i in range(pas + 1):
        x, y = w * i / pas, h * i / pas
        epais = 2 if i % 5 == 0 else 1
        draw.line([(x, 0), (x, h)], fill=(220, 30, 30, 150), width=epais)
        draw.line([(0, y), (w, y)], fill=(220, 30, 30, 150), width=epais)
        if 0 < i < pas:
            draw.text((x + 3, 3), f"{i / pas:.1f}", font=fnt, fill=(200, 0, 0, 255))
            draw.text((3, y + 3), f"{i / pas:.1f}", font=fnt, fill=(200, 0, 0, 255))
    base, _ = os.path.splitext(chemin)
    sortie = base + "_grille.png"
    img.save(sortie)
    return sortie


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", nargs="?", help="fichier JSON de spécification")
    ap.add_argument("-o", "--sortie", default=None, help="dossier de sortie (défaut : celui du JSON)")
    ap.add_argument("--nom", default="planche", help="nom de base des fichiers produits")
    ap.add_argument("--grille", metavar="IMAGE", help="produit IMAGE_grille.png pour repérer les ancres")
    args = ap.parse_args()

    if args.grille:
        print(grille(args.grille))
        return
    if not args.spec:
        ap.error("spec.json requis (ou --grille IMAGE)")

    with open(args.spec, encoding="utf-8") as f:
        spec = json.load(f)
    dossier_spec = os.path.dirname(os.path.abspath(args.spec))
    sortie = args.sortie or dossier_spec
    os.makedirs(sortie, exist_ok=True)

    page = composer(spec, dossier_spec)
    pdf = os.path.join(sortie, args.nom + ".pdf")
    png = os.path.join(sortie, args.nom + ".png")
    page.save(pdf, "PDF", resolution=DPI)
    apercu = page.copy()
    apercu.thumbnail((2000, 2000))
    apercu.save(png)
    print(pdf)
    print(png)


if __name__ == "__main__":
    main()
