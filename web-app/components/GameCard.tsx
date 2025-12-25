"use client";

import { motion } from "motion/react";
import { LucideIcon } from "lucide-react";
import { useState } from "react";

interface Game {
  id: string;
  title: string;
  genre: string;
  description: string;
  icon: LucideIcon;
  color: string;
  features: string[];
  buttonText: string;
}

interface GameCardProps {
  game: Game;
  index: number;
}

const colorMap: Record<string, { border: string; glow: string; bg: string; text: string }> = {
  cyan: {
    border: "border-neon-cyan",
    glow: "shadow-[0_0_30px_rgba(0,255,255,0.3)]",
    bg: "from-neon-cyan/20 to-transparent",
    text: "text-neon-cyan",
  },
  red: {
    border: "border-neon-red",
    glow: "shadow-[0_0_30px_rgba(255,68,68,0.3)]",
    bg: "from-neon-red/20 to-transparent",
    text: "text-neon-red",
  },
  green: {
    border: "border-neon-green",
    glow: "shadow-[0_0_30px_rgba(0,255,136,0.3)]",
    bg: "from-neon-green/20 to-transparent",
    text: "text-neon-green",
  },
  orange: {
    border: "border-neon-orange",
    glow: "shadow-[0_0_30px_rgba(255,136,0,0.3)]",
    bg: "from-neon-orange/20 to-transparent",
    text: "text-neon-orange",
  },
  purple: {
    border: "border-neon-purple",
    glow: "shadow-[0_0_30px_rgba(170,136,255,0.3)]",
    bg: "from-neon-purple/20 to-transparent",
    text: "text-neon-purple",
  },
};

export default function GameCard({ game, index }: GameCardProps) {
  const [isHovered, setIsHovered] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const colors = colorMap[game.color] || colorMap.cyan;
  const Icon = game.icon;

  const handlePlay = () => {
    setIsLoading(true);
    // Navigate to the game player page
    const basePath = process.env.NODE_ENV === 'production' ? '/adventures-in-space' : '';
    window.location.href = `${basePath}/play/${game.id}/`;
  };

  return (
    <motion.div
      className={`game-card relative rounded-2xl p-6 bg-gradient-to-br from-dark-card to-dark-bg border border-white/10 overflow-hidden ${
        isHovered ? `${colors.border} ${colors.glow}` : ""
      }`}
      variants={{
        hidden: { opacity: 0, y: 50 },
        visible: { opacity: 1, y: 0 },
      }}
      transition={{ duration: 0.5, delay: index * 0.1 }}
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
      whileHover={{ scale: 1.02 }}
    >
      {/* Top accent line */}
      <div
        className={`absolute top-0 left-0 right-0 h-1 bg-gradient-to-r ${colors.bg}`}
      />

      {/* Icon */}
      <motion.div
        className={`w-16 h-16 rounded-xl bg-gradient-to-br ${colors.bg} flex items-center justify-center mb-4`}
        animate={isHovered ? { rotate: [0, -10, 10, 0] } : {}}
        transition={{ duration: 0.5 }}
      >
        <Icon className={`w-8 h-8 ${colors.text}`} />
      </motion.div>

      {/* Title & Genre */}
      <h2 className={`text-xl font-bold ${colors.text} mb-1`}>{game.title}</h2>
      <p className="text-xs text-gray-500 uppercase tracking-widest mb-3">
        {game.genre}
      </p>

      {/* Description */}
      <p className="text-gray-400 text-sm leading-relaxed mb-4 min-h-[60px]">
        {game.description}
      </p>

      {/* Features */}
      <div className="flex flex-wrap gap-2 mb-6">
        {game.features.map((feature, i) => (
          <span
            key={i}
            className="text-xs px-2 py-1 rounded bg-white/5 text-gray-400 uppercase tracking-wider"
          >
            {feature}
          </span>
        ))}
      </div>

      {/* Play Button */}
      <motion.button
        className={`w-full py-3 rounded-lg font-bold uppercase tracking-wider text-sm relative overflow-hidden border ${colors.border} ${colors.text} bg-gradient-to-r ${colors.bg} hover:bg-opacity-100 transition-all duration-300`}
        onClick={handlePlay}
        disabled={isLoading}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        {/* Shine effect */}
        <motion.div
          className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
          initial={{ x: "-100%" }}
          whileHover={{ x: "100%" }}
          transition={{ duration: 0.5 }}
        />
        
        {isLoading ? (
          <span className="flex items-center justify-center gap-2">
            <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
            Loading...
          </span>
        ) : (
          game.buttonText
        )}
      </motion.button>

      {/* Hover glow effect */}
      {isHovered && (
        <motion.div
          className={`absolute -inset-1 rounded-2xl bg-gradient-to-r ${colors.bg} opacity-50 blur-xl -z-10`}
          initial={{ opacity: 0 }}
          animate={{ opacity: 0.5 }}
        />
      )}
    </motion.div>
  );
}

