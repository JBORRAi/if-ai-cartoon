# Animation principles — working sheet (after *The Animator's Survival Kit*, R. Williams)

*French original: [ANIMATION_PRINCIPLES_FR.md](ANIMATION_PRINCIPLES_FR.md)*

Personal working notes (the book is not included here: buy it!). Numbers are the printed pages of the Spanish
edition. Read BEFORE any animation. Every rule maps to a concrete setting in `scripts/motion_intro/doodle.py`.

## 1. Timing and spacing (p. 35-39, 50-51, 84-92)
- Everything is **timing** (when) + **spacing** (how far between two drawings). Same duration, different spacing = a different movement.
- **Ease in / ease out** (*cushion*) towards and away from the extremes. Never linear, except for mechanical things.
- What **falls accelerates** (gravity) and never slows down while falling (p. 92). → fall = `y += g·t²`.
- A **hard** object (golf ball, a letter) deforms on contact for **1-2 frames**, then snaps back very fast (p. 89, 39).
  Squash & stretch everywhere = "everything is rubber", so dose it. → hard text/objects: squash ≤ 10 %, recovery < 0.15 s.
- **Tempo contrast**: a bit faster than normal, then suddenly slower; never a uniform rhythm (p. 297).

## 2. Keys, extremes, breakdowns (p. 48-49, 57, 218-222)
- **Keys** tell the story; the **breakdown** (passing position) decides the character of the move.
- "Don't go from A to B: go from **A to X to B**" (Emery Hawkins, p. 218) → pass through an unexpected in-between pose.

## 3. Arcs (p. 90-92)
- Almost everything moves in an **arc** (often a wave or a figure 8). A straight line = power, keep it for hits.
  → moves with an arc offset (`arc=`).

## 4. Anticipation (p. 273-284)
- Anticipation → Action → Reaction (Tytla). Chaplin: "tell them what you're going to do, do it, tell them what you did".
- Anticipation goes **the opposite way** to the action; **slow**, then a **fast** action ("zip!").
- Back up before going forward, go down before going up, etc.
- **Invisible anticipation**: 1-2 frames the wrong way just before a sharp move = the *snap* (p. 283).
  → `antic=`: a small 6-10 % recoil over 0.08-0.15 s before every move.

## 5. Takes and accents (p. 285-296)
- **Take** = sees → **goes down** (antic.) → **goes up** very fast (accent, 2-3 frames) → settles. Disney ≈ 2/3 s, Warner ≈ 1/2 s.
- An extra **"collapse" pose** adds life (p. 292). Keep the volume when squashing (Milt Kahl).
- An accent or pose needs **≥ 5-6 frames (≈ 0.25 s at 24 fps)** to read (p. 293).
- **Hard accent bounces back** (hammer on anvil, sound 1 frame after contact).
  **Soft accent carries on** (a conductor) (p. 294-295).

## 6. Flexibility, overlap (p. 217-255)
- Parts don't move at the same time: one leads, the others **follow 2-4 frames later**
  (ears, antennae, signs, bubbles) → `lag` offset.
- Movement within movement: add a small secondary action inside the main one.

## 7. Weight (p. 213-216, 256-264)
- Know where the weight is on every frame. Heavy object = long preparation. Jump: arms go first, one leg drags
  → no "floating". "When you think you've gone far enough, go twice as far."

## 8. Vibrations, whip, wave (p. 297-302)
- A shake = **irregular exposure** (skip frames, hold some for 2-3 frames), never mechanical.
- Whip: the tip cracks on 1 frame, the sound 1 frame later; a wave = a whip without the crack.

## 9. Dialogue (p. 304-314)
- Don't animate every syllable: **phrase it**, hit the stressed vowels, then cushion.
- Consonants that close the mouth (M, B, P, F, V): **≥ 2 frames**. Sync on the sound or 1 frame before, **never after**.
- **Head accents 3-4 frames before** the vowel; the mouth opens on the sound; the head usually accents upwards.
- **The secret: move towards something while talking** (Milt Kahl / Ken Harris).

## 10. Acting, eyes (p. 315-326)
- One idea at a time, crystal clear. Pantomime first (readable without words).
- Change expression **at the end** of a move (or at the start), not in the middle; a **thinking beat** before acting.
- The gesture comes **before** or **after** the word, never exactly on it (p. 323).
- Eyes move in saccades; **blink during a head turn** (p. 87, 326).

## Checklist before rendering
1. Does every move have an anticipation (even invisible)? 2. Arcs rather than straight lines? 3. Poses held ≥ 0.25 s?
4. Hard accents bounce back, soft ones carry on? 5. Overlap (nothing starts at the same time)?
6. Falls accelerate? 7. Hard objects barely deform? 8. Tempo contrast? 9. Gestures timed before/after the words?
