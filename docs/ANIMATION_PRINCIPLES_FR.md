# BIBLE ANIMATION — fiche de travail (d'après *The Animator's Survival Kit*, R. Williams, éd. espagnole)

*English version: [ANIMATION_PRINCIPLES.md](ANIMATION_PRINCIPLES.md)*

Notes de travail personnelles (le livre n'est pas fourni ici : achetez-le !). Numéros = pages imprimées du livre.
À relire AVANT toute animation. Chaque règle → son réglage concret dans `scripts/motion_intro/doodle.py`.

## 1. Timing et espacement (p. 35-39, 50-51, 84-92)
- Tout est **timing** (quand) + **espacement** (combien entre deux images). Même durée, espacement différent = autre mouvement.
- **Ease in / ease out** (« amortir », *cushion*) vers et depuis les extrêmes. Jamais de mouvement linéaire sauf mécanique.
- Ce qui **tombe accélère** (gravité), ne ralentit jamais en tombant (p. 92). → chute = `y += g·t²`.
- Objet **dur** (balle de golf, lettre) : se déforme au contact **1-2 images** puis reprend sa forme très vite (p. 89, 39).
  Le squash & stretch partout = « tout en caoutchouc », à doser. → texte/objets durs : écrasement ≤ 10 %, retour < 0,15 s.
- **Contraste de tempo** : un peu plus vite que la normale, puis brusquement plus lent ; jamais un rythme uniforme (p. 297).

## 2. Clés, extrêmes, breakdowns (p. 48-49, 57, 218-222)
- Les **clés** racontent l'histoire ; le **breakdown** (position de passage) décide du caractère du mouvement.
- « Ne va pas de A à B : va de **A à X à B** » (Emery Hawkins, p. 218) → passer par une pose intermédiaire inattendue.

## 3. Arcs (p. 90-92)
- Presque tout se déplace en **arc** (souvent en vague ou en 8). Ligne droite = puissance, à réserver aux coups.
  → déplacements avec une flèche d'arc (`arc=`).

## 4. Anticipation (p. 273-284)
- Anticipation → Action → Réaction (Tytla). Chaplin : « dis ce que tu vas faire, fais-le, dis ce que tu as fait ».
- L'anticipation va **dans le sens opposé** à l'action ; **lente**, puis action **rapide** (« zip ! »).
- Reculer avant d'avancer, descendre avant de monter, etc.
- **Anticipation invisible** : 1-2 images à contresens juste avant un mouvement vif = le *snap* (p. 283).
  → `antic=` : petit recul de 6-10 % de la distance pendant 0,08-0,15 s avant chaque déplacement.

## 5. Takes et accents (p. 285-296)
- **Take** = voit → **descend** (antic.) → **monte** très vite (accent, 2-3 images) → se pose. Disney ≈ 2/3 s, Warner ≈ 1/2 s.
- Une **pose de « collapse » en plus** donne plus de vie (p. 292). Garder le même volume en écrasant (Milt Kahl).
- Il faut **≥ 5-6 images (à 24 i/s ≈ 0,25 s)** pour qu'un accent / une pose se lise (p. 293).
- **Accent dur = rebondit en arrière** (marteau sur enclume, son 1 image après le contact).
  **Accent doux = continue** sur sa lancée (chef d'orchestre) (p. 294-295).

## 6. Souplesse, chevauchement (p. 217-255)
- Les parties ne bougent pas en même temps : une partie mène, les autres **suivent avec 2-4 images de retard**
  (oreilles, antennes, pancartes, bulles) → décalage `lag`.
- Mouvement dans le mouvement : ajouter une petite action secondaire dans l'action principale.

## 7. Poids (p. 213-216, 256-264)
- Savoir à chaque image où est le poids. Objet lourd = préparation longue. Saut : bras qui partent, une jambe en retard
  → pas de « flottement ». « Quand tu crois être allé assez loin, va deux fois plus loin. »

## 8. Vibrations, fouet, onde (p. 297-302)
- Tremblement = **exposition irrégulière** (sauter des images, tenir certaines 2-3 images), jamais mécanique.
- Fouet : la pointe claque 1 image, le son 1 image après ; onde = fouet sans claquement.

## 9. Dialogue (p. 304-314)
- Ne pas animer chaque syllabe : **phraser**, frapper les voyelles accentuées puis amortir.
- Consonnes qui ferment la bouche (M, B, P, F, V) : **≥ 2 images**. Synchro au niveau du son ou 1 image avant, **jamais après**.
- **Accents de tête 3-4 images avant** la voyelle, la bouche s'ouvre sur le son ; la tête accentue en général vers le haut.
- **Le secret : avancer vers quelque chose pendant qu'on parle** (Milt Kahl / Ken Harris).

## 10. Jeu d'acteur, yeux (p. 315-326)
- Une seule idée à la fois, claire comme du cristal. Pantomime d'abord (lisible sans les mots).
- Changer d'expression **à la fin** d'un mouvement (ou au début), pas au milieu ; un **temps de réflexion** avant d'agir.
- Le geste **avant** ou **après** le mot, jamais pile en même temps (p. 323).
- Les yeux bougent par saccades ; **clignement pendant un tour de tête** (p. 87, 326).

## Check-list avant rendu
1. Chaque mouvement a-t-il une anticipation (même invisible) ? 2. Arcs plutôt que droites ? 3. Poses tenues ≥ 0,25 s ?
4. Accents durs qui rebondissent / doux qui continuent ? 5. Chevauchement (rien ne part en même temps) ?
6. Chutes qui accélèrent ? 7. Objets durs peu déformés ? 8. Contraste de tempo ? 9. Gestes calés avant/après les mots ?
