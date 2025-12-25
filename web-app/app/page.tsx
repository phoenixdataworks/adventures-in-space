"use client";

import { useState, useEffect } from "react";
import { motion } from "motion/react";
import { Rocket, Gift, Gamepad2, Star, Scroll } from "lucide-react";
import StarField from "@/components/StarField";
import GameCard from "@/components/GameCard";
import Header from "@/components/Header";

const games = [
  {
    id: "adventures-in-space",
    title: "Adventures in Space",
    genre: "Space Shooter",
    description:
      "Navigate through dangerous asteroid fields as an elite Space Defense pilot in the year 2157. Defend Earth's outposts with your advanced weapon system.",
    icon: Rocket,
    color: "cyan",
    features: ["Particles", "Power-ups", "Levels"],
    buttonText: "Launch Mission",
  },
  {
    id: "santa-vs-grunch",
    title: "Santa vs. Grunch",
    genre: "Platformer",
    description:
      "Help Santa collect stolen presents and deliver them through chimneys! Avoid the Grunch who's chasing you across the rooftops of Whoville.",
    icon: Gift,
    color: "red",
    features: ["Endless Runner", "Holiday Theme", "2 Modes"],
    buttonText: "Start Delivery",
  },
  {
    id: "snake-jump",
    title: "Snake Jump",
    genre: "Arcade",
    description:
      "A unique twist on the classic snake game! Control your snake, eat food to grow, and jump over AI snakes to survive.",
    icon: Gamepad2,
    color: "green",
    features: ["AI Opponents", "Jump Mechanic", "Endless"],
    buttonText: "Start Game",
  },
  {
    id: "bible_stories",
    title: "Journey to Egypt",
    genre: "Adventure / Stealth",
    description:
      "Guide Joseph, Mary, and baby Jesus through dangerous territories, avoiding Roman patrols as you make your way to safety in Egypt.",
    icon: Star,
    color: "orange",
    features: ["5 Levels", "Stealth", "Story Mode"],
    buttonText: "Begin Journey",
  },
  {
    id: "joseph_mary_run",
    title: "Joseph & Mary Run",
    genre: "Puzzle / Adventure",
    description:
      "Navigate through Bethlehem, find keys, avoid guards, and use tools wisely to escape through 5 challenging levels.",
    icon: Scroll,
    color: "purple",
    features: ["Puzzle", "Tools", "Guards"],
    buttonText: "Play Now",
  },
];

export default function Home() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return null;
  }

  return (
    <main className="relative min-h-screen overflow-hidden">
      {/* Animated Star Background */}
      <StarField />

      {/* Content */}
      <div className="relative z-10 container mx-auto px-4 py-8">
        <Header />

        {/* Game Grid */}
        <motion.div
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-12"
          initial="hidden"
          animate="visible"
          variants={{
            hidden: { opacity: 0 },
            visible: {
              opacity: 1,
              transition: {
                staggerChildren: 0.1,
              },
            },
          }}
        >
          {games.map((game, index) => (
            <GameCard key={game.id} game={game} index={index} />
          ))}
        </motion.div>

        {/* Footer */}
        <motion.footer
          className="text-center py-12 mt-12 text-gray-500 text-sm"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
        >
          <p>Built with Pygame & Next.js • © 2025 Arcade Games Collection</p>
          <p className="mt-2 text-xs text-gray-600">
            Press any game to start playing!
          </p>
        </motion.footer>
      </div>
    </main>
  );
}

