---
name: croquis-annote
description: Faire un croquis annoté Studio Kito. Transforme une photo de mobilier ou d'aménagement (réelle ou approchante) en croquis de présentation client en perspective, style crayon/feutre fin + aquarelle, puis ajoute des annotations manuscrites (matériaux, finitions, cotes) et compose une planche PDF A4/A3 avec cartouche Studio Kito. À utiliser dès que Franck demande « faire un croquis annoté », « croquis client », « rendu aquarelle d'un meuble », « perspective d'intention », « planche de présentation » ou fournit une photo de meuble à mettre en croquis.
---

# Faire un croquis annoté

Produire, à partir d'une photo, une **planche de présentation client** : un croquis
d'intention en perspective (crayon + aquarelle, style « carnet d'architecte
d'intérieur »), annoté à la main, avec le cartouche Studio Kito.

Référence de style : `assets/reference-style.jpg` (cuisine au feutre, perspective à
2 points de fuite, traits qui débordent aux angles, couleurs posées en lavis
avec réserves de blanc, ombres portées plates beige). La version Studio Kito est
plus légère et plus moderne : **crayon graphite + feutre fin + aquarelle**.

## Principe de répartition du travail

| Étape | Qui | Pourquoi |
|---|---|---|
| Analyse photo + brief | Claude | Identifier forme, proportions, matériaux, couleurs |
| Image croquis (sans texte) | IA image (ChatGPT/GPT-Image, Gemini, Midjourney) — lancée par Franck | Claude ne génère pas d'image peinte |
| Annotations, cotes, cartouche, PDF | Claude via `scripts/annotate.py` | Orthographe, cotes et mise en page fiables |

**Règle d'or : l'IA image ne doit écrire AUCUN texte.** Toutes les annotations sont
superposées par le script.

## Déroulé

### 1. Recueillir l'entrée

Il faut au minimum :
- **la photo** du meuble / de l'aménagement (réelle, catalogue ou approchante) ;
- **la liste des annotations** (souvent donnée dans la demande).

Compléter si absent (demander en une seule fois, proposer des valeurs par défaut) :
- titre de la planche, nom du projet, client ;
- format A4 ou A3 (défaut : A4 paysage ; choisir portrait seulement si l'objet est plus haut que large — armoire, bibliothèque) ;
- ce qui **diffère de la photo** (essence de bois, couleur, dimensions, poignées…) —
  c'est souvent le cœur de la demande : la photo sert de base, le croquis montre le projet ;
- mise en scène : objet seul sur fond blanc (défaut) ou dans un intérieur suggéré ;
- cotes à faire figurer (L × P × H), affichées **en cm ou en m** pour la lisibilité client
  (convertir si Franck donne des mm).

### 2. Analyser la photo

Écrire une fiche courte (visible par Franck, pour valider la compréhension) :
- **Objet** : type, style, nombre d'éléments.
- **Géométrie** : volumes principaux, proportions (ex. « plateau ≈ 2× la hauteur du piètement »),
  détails constructifs visibles (assemblages, chants, pieds, poignées, moulures).
- **Matériaux et couleurs** : essence / teinte / finition, avec 3 à 5 couleurs nommées.
- **Point de vue retenu** : vue 3/4 en perspective à 2 points de fuite, hauteur d'œil
  (debout ≈ 1,60 m pour un meuble bas ; hauteur assise pour un bureau ; légère plongée
  pour un aménagement complet).
- **Écarts voulus** par rapport à la photo.

### 3. Rédiger le prompt image

Utiliser les gabarits de `references/prompts-image.md` (en anglais, meilleur rendu).
Toujours livrer :
1. **Prompt principal ChatGPT / Gemini** (joindre la photo + `assets/reference-style.jpg`) ;
2. **Variante Midjourney** (avec `--sref` / `--no text`) ;
3. une ligne « **Que joindre** » (quelles images, dans quel ordre).

Contraintes à inclure systématiquement (détail dans `references/guide-style.md`) :
perspective 2 points, trait crayon/feutre fin qui déborde légèrement, lavis
aquarelle transparents avec réserves de blanc, palette limitée fidèle aux matériaux,
fond papier blanc qui s'estompe en vignette, ombre portée légère, **espace blanc
autour de l'objet**, **aucun texte / lettre / chiffre / logo / signature**, pas de rendu 3D
ni photoréaliste, format paysage 3:2.

Puis s'arrêter : demander à Franck de générer l'image et de la renvoyer.

### 4. Contrôler l'image reçue

Avant d'annoter, vérifier et dire franchement ce qui ne va pas :
- fidélité à la photo (forme, proportions, nombre de tiroirs/portes, pieds) ;
- écarts demandés bien appliqués (essence, couleur…) ;
- style conforme (pas de 3D lisse, pas de texte parasite, fond clair) ;
- perspective cohérente (verticales verticales, fuyantes convergentes).

Si un défaut est bloquant → proposer un **prompt de correction ciblé** (voir fin de
`references/prompts-image.md`) plutôt que de tout relancer.

### 5. Placer les annotations

1. Enregistrer l'image dans le dossier de travail (ex. `croquis.png`).
2. Générer la grille de repérage et la regarder :
   ```bash
   python scripts/annotate.py --grille croquis.png   # -> croquis_grille.png
   ```
3. Écrire `spec.json` (modèle : `exemples/cuisine.json`, règles :
   `references/annotations.md`). Les ancres `[x, y]` sont en fractions (0–1) de
   **l'image source**, lues sur la grille. Viser l'intérieur de la pièce désignée,
   pas son contour.
4. Composer la planche :
   ```bash
   pip install pillow   # si nécessaire
   python scripts/annotate.py spec.json -o sortie/ --nom <projet>_croquis_V1
   ```
5. **Regarder l'aperçu PNG** produit et corriger : point d'ancre à côté de la pièce,
   traits qui se croisent, étiquettes trop longues, cote mal placée. Itérer jusqu'à
   une planche propre.

### 6. Livrer

- Le **PDF** (planche client) + l'aperçu PNG.
- Rappeler en une ligne les hypothèses prises (dimensions supposées, couleur interprétée).
- Nommer les fichiers selon la convention de Franck si la skill
  `convention-nom-fichier-dossier` est disponible.

## Relecture avant livraison (checklist)

- [ ] Orthographe et accents des annotations (français, majuscule initiale, pas de point final).
- [ ] Dimensions lisibles pour le client : **cm** pour le mobilier (« 180 × 90 cm », « ép. 3 cm »),
  **m** au-delà de 3 m (« 3,20 m ») — pas de mm, virgule décimale française.
- [ ] Chaque ancre tombe bien sur l'élément nommé.
- [ ] Pas plus de 8 annotations sur A4 (au-delà : A3 ou regrouper).
- [ ] Cartouche complet : titre, projet, client, date, version.
- [ ] Mention « Croquis d'intention – non contractuel » présente.
- [ ] Aucun texte généré par l'IA dans le croquis.

## Fichiers de la skill

- `references/guide-style.md` — analyse du style de référence et règles graphiques.
- `references/prompts-image.md` — gabarits de prompts (ChatGPT/Gemini, Midjourney) et corrections.
- `references/annotations.md` — format du `spec.json`, conventions de rédaction.
- `scripts/annotate.py` — grille de repérage + composition de la planche (Pillow).
- `assets/reference-style.jpg` — image de style à joindre à l'IA image.
- `assets/fonts/` — déposer ici une police manuscrite (voir README).
- `exemples/cuisine.json` + `exemples/cuisine_planche.png` — exemple complet.
