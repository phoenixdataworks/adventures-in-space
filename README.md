# 🎮 Arcade Games Collection

A collection of retro-style arcade games built with Pygame, with a Next.js launcher for web deployment via GitHub Pages.

## 🕹️ Play Online

Visit: **https://bobbylansing.github.io/adventures-in-space/**

## Games

### 🚀 Adventures in Space
**Genre:** Space Shooter

In the year 2157, as an elite Space Defense pilot, you patrol the dangerous Asteroid Belt. Defend Earth's outposts with your advanced weapon system.

**Features:** Parallax star field, particle effects, object pooling, multiple asteroid patterns

**Controls:** `←` `→` to move, `SPACE` to shoot

---

### 🎅 Santa vs. The Grunch
**Genre:** Platformer / Endless Runner

Help Santa collect stolen presents and deliver them through chimneys while avoiding the Grunch.

**Features:** Two game modes, dynamic platforms, animated Grunch AI

**Controls:** `←` `→` to move, `SPACE` to jump

---

### 🐍 Snake Jump
**Genre:** Arcade

A unique twist on the classic snake game! Control your snake, eat food to grow, and **jump over AI snakes** to survive.

**Features:** AI opponents, jump mechanic, smooth snake physics

**Controls:** `←` `→` or `A` `D` to turn, `SPACE` to jump

---

### 🏛️ Journey to Egypt
**Genre:** Adventure / Runner

Guide Joseph, Mary, and baby Jesus through dangerous territories, avoiding Roman patrols.

**Controls:** `←` `→` to move, `SPACE` to jump, `↓` to duck

---

### ⭐ Joseph & Mary Run
**Genre:** Puzzle / Stealth

Navigate through Bethlehem, find keys, avoid guards, and use tools to escape through 5 levels.

**Controls:** `←` `→` `↑` `↓` to move

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ with `pygame` and `pygbag`
- Node.js 18+

### Local Development

```bash
# Clone the repository
git clone https://github.com/bobbylansing/adventures-in-space.git
cd adventures-in-space

# Build all games and the web app
./build.sh

# Or manually:

# 1. Install Python dependencies
pip install pygame pygbag

# 2. Build games with Pygbag
cd adventures-in-space && python -m pygbag --build main.py && cd ..
cd santa-vs-grunch && python -m pygbag --build main.py && cd ..
cd snake-jump && python -m pygbag --build snake-jump.py && cd ..
cd bible_stories && python -m pygbag --build main.py && cd ..
cd joseph_mary_run && python -m pygbag --build main.py && cd ..

# 3. Setup Next.js
cd web-app
npm install

# 4. Copy games to public folder
mkdir -p public/games
cp -r ../adventures-in-space/build/web public/games/adventures-in-space
cp -r ../santa-vs-grunch/build/web public/games/santa-vs-grunch
cp -r ../snake-jump/build/web public/games/snake-jump
cp -r ../bible_stories/build/web public/games/bible_stories
cp -r ../joseph_mary_run/build/web public/games/joseph_mary_run

# 5. Run dev server
npm run dev
# Opens at http://localhost:3000
```

---

## 🌐 GitHub Pages Deployment

The site automatically deploys on push to `main` via GitHub Actions.

### Setup (One-time)
1. Go to your repo → **Settings** → **Pages**
2. Under "Build and deployment", select **GitHub Actions**
3. Push to main branch

The workflow will:
1. Build all Pygame games with Pygbag
2. Build the Next.js homepage
3. Deploy to GitHub Pages

---

## 📁 Project Structure

```
adventures-in-space/
├── .github/workflows/
│   └── deploy.yml              # GitHub Actions deployment
├── web-app/                     # Next.js homepage
│   ├── app/
│   │   ├── page.tsx            # Home with game cards
│   │   └── play/[gameId]/      # Game player pages
│   ├── components/
│   │   ├── GameCard.tsx        # Animated game cards
│   │   ├── Header.tsx          # Neon header
│   │   └── StarField.tsx       # Animated stars
│   └── public/games/           # Built Pygbag games (gitignored)
├── engine/                      # Shared Python game engine
│   ├── camera.py               # Camera with shake, zoom
│   ├── collision.py            # Spatial partitioning
│   ├── particles.py            # Particle effects
│   ├── object_pool.py          # Memory-efficient pooling
│   └── ...
├── adventures-in-space/         # Space shooter
├── santa-vs-grunch/             # Christmas platformer
├── snake-jump/                  # Snake arcade
├── bible_stories/               # Journey to Egypt
├── joseph_mary_run/             # Stealth puzzle
├── build.sh                     # Master build script
└── README.md
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Games | Python, Pygame |
| Web Export | Pygbag (WebAssembly) |
| Homepage | Next.js 14, React, Tailwind CSS |
| Animations | Framer Motion |
| Deployment | GitHub Pages + Actions |

---

## 📄 License

MIT License - see LICENSE file for details.
