#!/usr/bin/env python3
"""
logo_to_coloriage.py

Convertit un logo client en couleur (PNG, fond transparent de preference)
en version "coloriage" : contour noir sur fond transparent, dans le style
graphique des Petits Papiers.

Usage :
    python3 logo_to_coloriage.py entree.png sortie-coloriage.png
    python3 logo_to_coloriage.py dossier_logos/ dossier_sortie/   (traite tout le dossier)

Options :
    --thickness N   epaisseur du trait en pixels (defaut 2)
    --threshold N   sensibilite de detection des contours, 0-255 (defaut 60)
    --color "R,G,B" couleur du trait (defaut 45,45,58 -> #2d2d3a, le "dark" LPP)

Necessite : Pillow (pip install pillow --break-system-packages)
"""

import sys
import os
import argparse
from collections import deque
from PIL import Image, ImageFilter, ImageOps

try:
    import numpy as np
except ImportError:
    np = None


def despeckle(mask_img, min_area=12):
    """Supprime les petits ilots de pixels isoles (bruit de detection de
    contour sur les logos avec du texte fin / des degrades) tout en
    conservant les traits et details plus grands (points, apostrophes...)."""
    if np is None or min_area <= 0:
        return mask_img
    arr = np.array(mask_img) > 127
    h, w = arr.shape
    visited = np.zeros_like(arr, dtype=bool)
    out = np.zeros_like(arr, dtype=bool)
    neighbours = ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1))
    for y in range(h):
        row = arr[y]
        for x in range(w):
            if row[x] and not visited[y, x]:
                q = deque([(y, x)])
                visited[y, x] = True
                comp = [(y, x)]
                while q:
                    cy, cx = q.popleft()
                    for dy, dx in neighbours:
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < h and 0 <= nx < w and arr[ny, nx] and not visited[ny, nx]:
                            visited[ny, nx] = True
                            q.append((ny, nx))
                            comp.append((ny, nx))
                if len(comp) >= min_area:
                    for (cy, cx) in comp:
                        out[cy, cx] = True
    return Image.fromarray((out * 255).astype("uint8"), mode="L")


def logo_to_coloriage(input_path, output_path, thickness=2, threshold=180, color=(45, 45, 58), pad=24, blur=1.0, despeckle_area=12, close_gaps=True):
    img = Image.open(input_path).convert("RGBA")

    # On travaille sur un fond blanc pour que la detection de contours
    # fonctionne meme si le logo a un fond transparent. Une marge blanche
    # est ajoutee autour pour eviter que le bord de l'image ne soit lui-meme
    # detecte comme un contour (cadre noir indesirable).
    padded_size = (img.width + 2 * pad, img.height + 2 * pad)
    bg = Image.new("RGBA", padded_size, (255, 255, 255, 255))
    bg.paste(img, (pad, pad), img)
    flat = bg.convert("L")

    # Un leger flou attenue le bruit / les degrades avant la detection.
    smooth = flat.filter(ImageFilter.GaussianBlur(radius=blur))

    # CONTOUR donne un trait fin et continu (mieux adapte au texte / logos
    # detailles que FIND_EDGES, qui double souvent les traits fins).
    # Sortie : traits sombres sur fond clair.
    edges = smooth.filter(ImageFilter.CONTOUR)
    edges = ImageOps.autocontrast(edges)

    # Epaissir le trait (style feutre / marqueur).
    for _ in range(max(0, thickness - 1)):
        edges = edges.filter(ImageFilter.MinFilter(3))

    # Les traits sont sombres ici (contraire de FIND_EDGES) : on garde les
    # pixels en dessous du seuil.
    mask = edges.point(lambda p: 255 if p < threshold else 0)

    # "Closing" morphologique : referme les petites coupures dans les traits
    # fins (texte script, degrades) sans changer l'epaisseur finale.
    if close_gaps:
        mask = mask.filter(ImageFilter.MaxFilter(3))
        mask = mask.filter(ImageFilter.MinFilter(3))

    # Supprime les ilots de bruit isoles (poussiere de detection) tout en
    # gardant les traits continus.
    mask = despeckle(mask, min_area=despeckle_area)

    outline = Image.new("RGBA", padded_size, (0, 0, 0, 0))
    solid = Image.new("RGBA", padded_size, color + (255,))
    outline.paste(solid, (0, 0), mask)

    # On retire la marge pour revenir aux dimensions d'origine.
    outline = outline.crop((pad, pad, pad + img.width, pad + img.height))

    outline.save(output_path)
    print(f"OK  {input_path} -> {output_path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input", help="fichier PNG ou dossier de logos en couleur")
    parser.add_argument("output", help="fichier de sortie ou dossier de sortie")
    parser.add_argument("--thickness", type=int, default=2)
    parser.add_argument("--threshold", type=int, default=180)
    parser.add_argument("--blur", type=float, default=1.0)
    parser.add_argument("--color", type=str, default="45,45,58")
    parser.add_argument("--despeckle", type=int, default=12, help="taille min (px) des ilots conserves, 0 = desactive")
    parser.add_argument("--no-close", action="store_true", help="desactive le comblement des petites coupures")
    args = parser.parse_args()

    color = tuple(int(c.strip()) for c in args.color.split(","))

    if os.path.isdir(args.input):
        os.makedirs(args.output, exist_ok=True)
        for name in sorted(os.listdir(args.input)):
            if not name.lower().endswith((".png", ".jpg", ".jpeg")):
                continue
            base, _ = os.path.splitext(name)
            out_name = f"{base}-coloriage.png"
            logo_to_coloriage(
                os.path.join(args.input, name),
                os.path.join(args.output, out_name),
                thickness=args.thickness,
                threshold=args.threshold,
                color=color,
                blur=args.blur,
                despeckle_area=args.despeckle,
                close_gaps=not args.no_close,
            )
    else:
        logo_to_coloriage(
            args.input, args.output,
            thickness=args.thickness, threshold=args.threshold, color=color, blur=args.blur,
            despeckle_area=args.despeckle, close_gaps=not args.no_close,
        )


if __name__ == "__main__":
    main()
