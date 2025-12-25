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

# Install Python dependencies
pip install -r requirements.txt

# Build all games and the web app
./build.sh

# Or run the Next.js dev server:
cd web-app
npm install
npm run dev
# Opens at http://localhost:3000
```

---

## 🏆 Leaderboard System

The games use a simple localStorage-based leaderboard that works offline and persists per-device.

### Usage in Games

```python
from engine.leaderboard import Leaderboard, add_score, get_top_scores, is_high_score

# Simple API
if is_high_score("my-game", player_score):
    rank = add_score("my-game", player_name, player_score, level=current_level)
    print(f"New high score! Rank: {rank}")

# Get top 5 scores
for entry in get_top_scores("my-game", 5):
    print(f"{entry['name']}: {entry['score']}")

# Or use the class directly
leaderboard = Leaderboard("my-game", max_entries=10)
leaderboard.add_score("PLAYER", 1000)
```

**Features:**
- Works in browser (Pygbag/localStorage) and desktop (JSON file)
- Persistent across sessions
- Automatic sorting and ranking
- No external dependencies or API keys

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
│   └── public/games/           # Built Pygbag games
├── engine/                      # Shared Python game engine
│   ├── camera.py               # Camera with shake, zoom
│   ├── collision.py            # Spatial partitioning
│   ├── particles.py            # Particle effects
│   ├── object_pool.py          # Memory-efficient pooling
│   ├── leaderboard.py          # localStorage leaderboards
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
| Games | Python 3.12, Pygame 2.6 |
| Web Export | Pygbag 0.9 (WebAssembly) |
| Homepage | Next.js 15, React 19, Tailwind CSS |
| Animations | Motion (framer-motion) |
| Deployment | GitHub Pages + Actions |
| Leaderboards | Browser localStorage |

---

## 📄 License

MIT License - see LICENSE file for details.
