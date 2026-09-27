# Annotations et `spec.json`

## Rédaction

- **Titre** (1re ligne, plus gros) : l'élément + le matériau → « Plateau chêne massif ».
- **Détail** (facultatif, plus petit, gris) : dimension, finition, quincaillerie →
  « ép. 30 mm – huile naturelle ».
- Français, majuscule initiale, pas de point final, 4 mots max pour le titre.
- Unités : cm pour les dimensions d'ensemble, mm pour les épaisseurs.
- 4 à 8 annotations sur A4 ; au-delà, passer en A3 ou regrouper.
- Ordre de lecture naturel : de haut en bas de chaque côté (le script trie automatiquement).

## Format du fichier

```json
{
  "image": "croquis.png",
  "rognage": [0.0, 0.0, 1.0, 1.0],
  "format": "A4",
  "orientation": "paysage",
  "titre": "Buffet bas – chêne & laiton",
  "projet": "Séjour Dupont",
  "client": "Mme Dupont",
  "date": "27/09/2026",
  "version": "V1",
  "mention": "Croquis d'intention – non contractuel",
  "couleur_accent": "#b5563c",
  "largeur_colonne": 0.2,
  "annotations": [
    {"texte": "Plateau chêne massif", "detail": "ép. 30 mm – huile naturelle", "ancre": [0.45, 0.32]},
    {"texte": "Poignées laiton brossé", "ancre": [0.62, 0.55], "cote": "droite"},
    {"texte": "Pieds fuselés", "ancre": [0.30, 0.85], "cote": "gauche", "etiquette_y": 0.9}
  ],
  "cotes": [
    {"de": [0.20, 0.80], "a": [0.78, 0.80], "texte": "180 cm", "decalage": 0.05}
  ]
}
```

| Champ | Rôle |
|---|---|
| `image` | Chemin du croquis (relatif au JSON). Obligatoire. |
| `rognage` | Recadrage `[x0, y0, x1, y1]` en fractions de l'image source. |
| `format` / `orientation` | `A4`/`A3`, `paysage`/`portrait`. Défaut A4 paysage. |
| `titre`, `projet`, `client`, `date`, `version`, `mention` | Cartouche. |
| `marque`, `signature` | Remplacent « STUDIO KITO » et la ligne sous la marque. |
| `couleur_accent` | Couleur des points d'ancrage (défaut terracotta). |
| `largeur_colonne` | Largeur des colonnes d'annotations, fraction de la page (défaut 0.2). |
| `annotations[].ancre` | Point visé `[x, y]`, fractions de l'image **source** (lire sur `--grille`). |
| `annotations[].cote` | `gauche`, `droite` ou `auto` (défaut : selon la position de l'ancre). |
| `annotations[].etiquette_y` | Force la hauteur souhaitée de l'étiquette (même repère que l'ancre). |
| `cotes[]` | Ligne de cote entre `de` et `a` ; `decalage` (fraction de l'image, signe = côté) écarte la ligne de l'objet. |

## Bonnes pratiques de placement

- Mettre l'ancre **au cœur** de la surface désignée (milieu d'un panneau, pas son arête).
- Éviter que deux traits de rappel se croisent : basculer une annotation de côté
  (`"cote"`) ou ajuster `etiquette_y`.
- Cotes : suivre une arête réelle du meuble (arête avant basse pour la longueur,
  arête verticale pour la hauteur). Si la cote passe sur le dessin, inverser le signe de `decalage`.
- Toujours regarder l'aperçu PNG et corriger avant d'envoyer le PDF.
