"use client";

import { useEffect, useState } from "react";
import { motion } from "motion/react";

interface Star {
  id: number;
  x: number;
  y: number;
  size: number;
  delay: number;
  duration: number;
}

interface Nebula {
  id: number;
  x: number;
  y: number;
  size: number;
  color: string;
  opacity: number;
}

export default function StarField() {
  const [stars, setStars] = useState<Star[]>([]);
  const [nebulae, setNebulae] = useState<Nebula[]>([]);

  useEffect(() => {
    // Generate stars
    const newStars: Star[] = [];
    for (let i = 0; i < 150; i++) {
      newStars.push({
        id: i,
        x: Math.random() * 100,
        y: Math.random() * 100,
        size: Math.random() * 3 + 1,
        delay: Math.random() * 3,
        duration: Math.random() * 2 + 2,
      });
    }
    setStars(newStars);

    // Generate nebulae
    const nebulaColors = [
      "rgba(128, 0, 255, 0.15)",
      "rgba(0, 128, 255, 0.12)",
      "rgba(255, 0, 128, 0.1)",
      "rgba(0, 255, 128, 0.08)",
    ];
    const newNebulae: Nebula[] = [];
    for (let i = 0; i < 6; i++) {
      newNebulae.push({
        id: i,
        x: Math.random() * 100,
        y: Math.random() * 100,
        size: Math.random() * 300 + 150,
        color: nebulaColors[Math.floor(Math.random() * nebulaColors.length)],
        opacity: Math.random() * 0.3 + 0.1,
      });
    }
    setNebulae(newNebulae);
  }, []);

  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none">
      {/* Nebulae */}
      {nebulae.map((nebula) => (
        <motion.div
          key={`nebula-${nebula.id}`}
          className="absolute rounded-full blur-3xl"
          style={{
            left: `${nebula.x}%`,
            top: `${nebula.y}%`,
            width: nebula.size,
            height: nebula.size,
            background: `radial-gradient(circle, ${nebula.color}, transparent)`,
          }}
          animate={{
            scale: [1, 1.2, 1],
            opacity: [nebula.opacity, nebula.opacity * 1.5, nebula.opacity],
          }}
          transition={{
            duration: 10,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
      ))}

      {/* Stars */}
      {stars.map((star) => (
        <motion.div
          key={`star-${star.id}`}
          className="absolute rounded-full bg-white"
          style={{
            left: `${star.x}%`,
            top: `${star.y}%`,
            width: star.size,
            height: star.size,
          }}
          animate={{
            opacity: [0.3, 1, 0.3],
            scale: [1, 1.3, 1],
          }}
          transition={{
            duration: star.duration,
            delay: star.delay,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
      ))}

      {/* Shooting star effect - occasional */}
      <motion.div
        className="absolute w-1 h-1 bg-white rounded-full"
        style={{
          boxShadow: "0 0 10px #fff, 0 0 20px #fff, -20px 0 30px #fff",
        }}
        initial={{ x: "-10%", y: "20%", opacity: 0 }}
        animate={{
          x: ["0%", "120%"],
          y: ["10%", "40%"],
          opacity: [0, 1, 0],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          repeatDelay: 8,
          ease: "easeOut",
        }}
      />
    </div>
  );
}

