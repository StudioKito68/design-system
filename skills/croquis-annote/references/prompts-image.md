# Gabarits de prompts image

Les prompts sont en anglais (meilleure compréhension des modèles image). Remplacer
les `[…]` à partir de la fiche d'analyse. Ne jamais y mettre les textes d'annotation.

## A. ChatGPT (GPT-Image) / Gemini — avec images jointes

**Que joindre, dans cet ordre :**
1. la photo du meuble (référence de forme) ;
2. `assets/reference-style.jpg` (référence de style).

```
Create a hand-drawn interior design presentation sketch.

SUBJECT — use image 1 as the exact reference for shape, proportions and construction
details: [description précise : type de meuble, volumes, nombre de portes/tiroirs,
piètement, poignées, détails d'assemblage].
Apply these changes compared to the photo: [écarts : essence, couleur, dimensions…
ou "none"].

STYLE — match the drawing style of image 2, but lighter and more modern:
- two-point perspective, 3/4 view, eye level at [hauteur d'œil],
- loose graphite pencil construction lines plus a fine black ink liner for contours,
  lines slightly overshooting at the corners, confident hand-drawn strokes,
- transparent watercolor washes applied in directional strokes, soft blooms and
  gradients, generous white paper highlights left unpainted on edges and reflections,
- limited palette faithful to the materials: [3–5 couleurs/matériaux],
- wood grain suggested with a few pencil strokes only,
- soft flat shadow on the floor, light coming from the upper left,
- [contexte : "object alone on white paper" OU "minimal room context drawn in thin
  lines only, barely colored: …"].

COMPOSITION — landscape 3:2, the object centered and occupying about 60% of the
width, plenty of empty white space around it, the drawing fades out softly towards
the edges like a vignette on watercolor paper.

STRICTLY NO text, letters, numbers, labels, arrows, dimensions, logo, watermark or
signature. Not a 3D render, not photorealistic, no CGI, no dark background.
```

## B. Midjourney (v6+)

Téléverser la photo (image prompt) et l'image de style (`--sref`).

```
[URL photo] hand-drawn interior design sketch of [objet court], two-point perspective
3/4 view, graphite pencil and fine ink liner, loose overshooting lines, transparent
watercolor washes with white paper highlights, [matériaux + couleurs], soft floor
shadow, isolated on white watercolor paper with vignette fade, lots of white space,
architect sketchbook style --sref [URL reference-style] --ar 3:2 --style raw
--no text, letters, numbers, labels, watermark, signature, 3d render, photorealistic
```

Réglages : `--iw 1.5` si la forme dérive trop de la photo ; `--sw 150–250` pour
renforcer le style.

## C. Prompts de correction ciblée (à envoyer dans la même conversation)

- **Proportions** : « Keep everything identical but make the [élément] [longer/thinner/
  lower] so that [rapport, ex. the top is twice as wide as it is tall]. »
- **Détail faux** : « Keep the drawing identical, only change: the [élément] should have
  [3 drawers instead of 2 / tapered legs / recessed handles]. »
- **Trop réaliste / 3D** : « Redraw with looser hand-drawn pencil lines and more
  transparent watercolor, visible brush strokes, more white paper left unpainted. »
- **Texte parasite** : « Remove every letter, number and label from the image. Nothing
  else changes. »
- **Cadrage serré** : « Zoom out: the object should occupy about 60% of the width with
  white space all around. »
- **Couleur** : « Change only the [élément] color to [couleur précise]. »

## Conseils

- Une seule modification par prompt de correction : les modèles dérivent sinon.
- Si après 3 corrections la forme reste fausse, relancer depuis A en décrivant mieux
  la géométrie (proportions chiffrées, vue souhaitée).
- Garder le meilleur tirage même imparfait : l'annotation peut masquer un petit défaut
  (rognage via `"rognage"` dans le spec).
