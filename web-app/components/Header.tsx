"use client";

import { motion } from "motion/react";

export default function Header() {
  return (
    <motion.header
      className="text-center py-8"
      initial={{ opacity: 0, y: -50 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8, ease: "easeOut" }}
    >
      <motion.h1
        className="font-arcade text-3xl md:text-5xl lg:text-6xl bg-gradient-to-r from-neon-pink via-neon-cyan to-neon-pink bg-clip-text text-transparent"
        animate={{
          backgroundPosition: ["0% 50%", "100% 50%", "0% 50%"],
        }}
        transition={{
          duration: 5,
          repeat: Infinity,
          ease: "linear",
        }}
        style={{
          backgroundSize: "200% 200%",
        }}
      >
        ARCADE GAMES
      </motion.h1>
      
      <motion.p
        className="mt-4 text-gray-400 tracking-[0.3em] text-xs md:text-sm uppercase"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
      >
        A Collection of Retro-Style Web Games
      </motion.p>

      {/* Decorative line */}
      <motion.div
        className="mt-6 mx-auto h-px w-48 bg-gradient-to-r from-transparent via-neon-cyan to-transparent"
        initial={{ scaleX: 0 }}
        animate={{ scaleX: 1 }}
        transition={{ delay: 0.8, duration: 0.8 }}
      />

      {/* Floating icons */}
      <div className="flex justify-center gap-4 mt-6">
        {["🚀", "🎮", "👾", "⭐", "🎯"].map((emoji, index) => (
          <motion.span
            key={index}
            className="text-2xl"
            animate={{
              y: [0, -10, 0],
            }}
            transition={{
              duration: 2,
              delay: index * 0.2,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          >
            {emoji}
          </motion.span>
        ))}
      </div>
    </motion.header>
  );
}

