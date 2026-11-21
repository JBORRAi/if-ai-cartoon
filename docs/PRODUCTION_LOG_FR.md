# IF — Journal de production (original, en français)

*Journal brut tenu pendant la production de l'épisode 1. Les chemins renvoient à l'arborescence de travail privée, non publiée ici.*

## 2026-10-07 — Création du projet
- Structure créée sur le modèle de KIMKATCHER. Cible : professionnels des formats cartoon.
- 2026-10-07 Turnaround Zak : v1 (Astra, réaliste) puis v2 caricature (Astra, édition) = base retenue : IF/BIBLE/TURNAROUND/3_RESULTATS/planche_v2_caricature.png

## 2026-10-07 — Zak : style, turnaround, modèle 3D, rig
- Bible de style BOR : IF/BIBLE/STYLE/STYLE.md + refs_cles/ + agent .claude/agents/style-bor.md.
- Turnaround : planche_v2_caricature.png (Astra) = base. Finition « douce » bloquée par la modération (laissée).
- Modèle : Hyper3D agentic mode depuis la planche, export FBX (9 608 faces, 69 % quads, textures PBR).
- Fichier de travail : IF/BIBLE/MODELE_3D/zak_rig.blend (ancien zak_modele.blend = archive).
  Découpé à la main avec Jérémie : ZAK (buste + tête + cheveux), ZAK_bras.L/R, ZAK_jambe.L/R.
  RIG_ZAK : buste (bassin, colonne, torse, cou, tête), bras (épaule, bras, avant-bras, main), jambes (cuisse, tibia, pied),
  4 doigts par main = pouce + 3 doigts (doigt1 = index), 3 phalanges chacun ; os des doigts L placés par Jérémie, R en miroir.
  Chaque objet n'est pondéré que sur ses os. Testé : bras, tête, jambes, doigts OK.
- À reprendre : axe d'ouverture de l'index (remonte au lieu de pointer), étirement paume/base des doigts, coutures épaules/hanches.
- Demain : la scène (grotte, décor, caméra fixe du plan IF).
- 2026-10-08 Yeux : globes séparés ZAK_oeil.L/R (pupille et iris réduits), orbites creusées (option « cavité »), os oeil.L/oeil.R indépendants sous tete, oeil.R écarté à -0,053 (L à 0,05). zak_rig.blend validé.

## 2026-10-08 — Décor EP01 (IF/EP01/SCENE_BLENDER/decor_ep01.blend)
- Plan fixe 21:9, contre-plongée légère (cam z 0,55, +7°), travelling vertical ciel->scène (frames 1->120), DOF sur Zak (f/0,6, herbes avant-plan floues).
- Zak à droite sur une cime (sol bombé), grotte 3D géante à gauche orientée vers lui sur une mini-plaine, rocher anguleux à gauche, foyer taillé (8 blocs + tipi de bûches).
- Plaine à perte de vue 14 m plus bas, collines lointaines masquant le pied du volcan qui fume, ptérodactyles.
- Herbe : touffes « Rayman » avant-plan (grosses + fines sombres), duvet sauvage en particules (P2_HERBE_zak 60 000 brins, plaine 30 000), dégagé autour de Zak et du foyer.
- À faire : matières/éclairage fin d après-midi, cassures de la grotte, acacia et mammouth.
- 2026-10-08 Rendu Astra du plan fixe : v1 trop collé au blockout ; v2 (prompt « layout seulement, tout repeindre ») validé -> EP01/PLANS/P01_plan_fixe/3_RESULTATS/P01_plan_fixe_v2.png.

## 2026-10-09
- Étape 4 (Main B) recoupée en 7 s : arrivée de la Main à l échelle + offre du briquet fermé ; Zak fixe la main, double clignement.
- Titre : fond passé en noir (BIBLE/TITRE/2_A_ENVOYER/titre_if_fond_noir.png) + PROMPT_titre_grok_anim.txt pour Grok, puis Topaz, fondu enchaîné.
- Titre animé depuis le PSD (scripts/anim_titre.py) : 3_RESULTATS/titre_if_anim.mov (+ _alpha). Sous-titre : « the art of timing... ».
- Titre v3 : fond beige uni, encre noire, sous-titre mot par mot avec rebond (titre_if_anim_beige_720p.mov).
- Titre v4 : départ beige direct, trait puis i et f lâchés (chute physique, rebond, motion blur), puis sous-titre.
- Titre VALIDÉ : 60 i/s, rythme dynamisé → 3_RESULTATS/TITRE_FINAL.mov (+ _alpha).
- Fin plan A (jeu d acteur, caméra fixe) : ETAPE_5_fin_A_ruse/PROMPT_fin_A_10s.txt. Plan B = travelling inversé Blender à faire.
- Fin plan B : CAM_ENVOL (copie de CAM_IF) dans SCENE_BLENDER/decor_ep01_fin.blend, plan fixe 1-36 puis montée z 0,55 -> 48 jusqu a f360 (15 s). Inverser une anim = erreur (easings et physique à l envers).
- MONTAGE/FINALCUT : 10 plans convertis en ProRes 422 HQ + PCM (scripts/finalcut_montage.py), numérotés par ordre de génération.
- Transition « What if?... » (scripts/anim_whatif.py, police fonts/AnnapurnaSIL OFL) calée sur la voix « Et si maintenant... Constatons... » : 3_RESULTATS/transition_whatif_720p.mov (+ _alpha).
- Plan STOP+Zippo validé (extend plan 02, fin sur 2_fin_9s) : FINALCUT/12_1009-1629_... Leçon : ne jamais retirer un bloc de prompt qui marche ; vérifier que la pose décrite = la keyframe.
- Musique : SON/BGM_SUNO.md (+ SUNO_1/2/3 .txt), style piano shuffle buddy song 112 BPM, calé sur EXPORTS/IF_EP01.mp4 (1:24.82).
- Panneau « What if?... » remplacé par « démonstration... » (2,75 s, scripts/anim_demonstration.py) ; VO_2 = « Démonstration... ».

## 2026-10-09 — PAUSE, reprise ici
- Montage V2 : `EP01/MONTAGE/EXPORTS/IF_EP01_V2.mp4` (1:33). Jérémie a recoupé la voix off et extrait l'audio seul en mp3 dans `EXPORTS/` → c'est LA référence de calage (pas les prises ElevenLabs brutes de `SON/VOIX_OFF/`).
- EN COURS : sous-titre animé de l'intro (centre écran, motion design stylisé, versions alpha + plein écran, même charte beige/encre/Annapurna SIL), calé au mot près sur ce mp3.
- Calage : Whisper local bloqué (modèle faster-whisper-small incomplet, téléchargement HF refusé hors sandbox). Plan B : pauses (silencedetect) sur le mp3 + texte connu de VO_1_intro.txt.
- Fait aujourd'hui : TITRE_FINAL (60 i/s), panneau « démonstration... » (lettre par lettre), 4 prompts Suno (piano shuffle, NOLA, funk, chambre à cailloux), VO ElevenLabs v4 + Voice Design (timbre rocailleux pince-sans-rire), plan STOP+Zippo validé (FINALCUT/12).
- Reste : sous-titres intro → musique Suno à caler → montage → upscale Topaz → montage final.
- 2026-10-11 : motion design intro calé au mot (Whisper sur EXPORTS/IF_EP01.mp3) : MOTION_INTRO/3_RESULTATS/intro_doodle_720p (A, dessins doodle) + intro_texte_720p (B, typo animée + graphismes), chacun en _alpha ; aperçus avec voix. Moteur : MOTION_INTRO/scripts/doodle.py.
- 2026-10-12 : version C « une seule ligne » (morphing continu calé au mot) : MOTION_INTRO/3_RESULTATS/intro_ligne_720p (+ _alpha, + FINALCUT/, + aperçu avec voix).
- 2026-10-12 : version D « affiche mid-century » (papier découpé, Futura, volets couleur) : MOTION_INTRO/3_RESULTATS/intro_affiche_720p (+ _alpha, FINALCUT/, aperçu avec voix).
- 2026-10-12 : BIBLE_ANIMATION.md (Williams) + moteur (anticipation/back, arcs, respiration, sortie anticipée, gravité 4200) ; version A2 intro_doodle_v2_720p (bonhomme articulé, takes, accents, écran vierge début/fin).
- A2 : traits arrondis (Chaikin), pression variable, contours épais / détails fins (param epais), grain papier + grain d encre.
- A2 : cycle de marche (Marcheur : pieds plantés, bob, bras opposés, course), marche du progrès singe->debout, formes fermées évidées, encre à densité variable « imprimée ».
- A2 : encre plus dense, 3 personnages de l évolution (singe, mi-debout, homme), épaules + bras longs au soulevé (bras visibles à côté de la tête).
- 2026-10-12 : version B2 typo animée expressive (intro_texte_v2_720p) : chaque mot animé selon son sens, Noteworthy Bold, grain papier, sorties avant chaque phrase.
- 2026-10-12 : version B3 typo (intro_texte_v3_720p) : police du titre, minuscules + CAPITALES espacées, mots entiers, flou de mouvement (5 sous-images), zooms arrière + balayages, PRODUCTIF en volets mécaniques, FORT échelle/rebond, RAPIDE flou, ampoules colorées avec halo.
- B3 : « fort » -> « FORT » (Impact) avec tassement puis rebond d échelle ; RAPIDE se pose puis démarre en trombe, fumée (planche 6 dessins, miroir, sur deux : ASSETS/fumee, scripts/extraire_fumee.py) plantée derrière le R.
- B3 : fumée plus petite (72 px), 24 dessins/s, dessins 4-6 recalés (centre de masse) sur la continuité.
- B3 : fumée validée (base sur la ligne de base de RAPIDE, pointe au début du R, passe sur « plus »), 28,8 dessins/s, fondu + agrandissement 2 % depuis le coin bas-droit.
- 2026-10-12 : passage en 24p natif (flou de mouvement recalculé) : TITRE_FINAL_24p (+alpha), intro_texte_v3_24p (+alpha), generique_IF_24p ; versions Final Cut dans les dossiers FINALCUT/.
- Panneau « démonstration... » en 24p avec grain papier + encre imprimée (comme l intro) : BIBLE/TITRE/3_RESULTATS/FINALCUT/transition_demonstration_24p(+_alpha).mov
- 2026-10-12 : générique v2 : 20 images toutes différentes (dédoublonnage par contenu), recadrage auto sur le sujet + format portrait pour Zak en pied, crayonné Grok + croquis papier du décor, captures 3D du 12/10, nuit Runway ; 3,3 s par carton (47,6 s).
- Titre TITRE_FINAL_24p re-rendu avec grain papier + encre imprimée (cohérent avec l intro) ; tous les rendus 24p encodés Final Cut réunis dans EP01/MONTAGE/RENDUS_24P/.
