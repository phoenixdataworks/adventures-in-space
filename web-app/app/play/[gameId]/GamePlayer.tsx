"use client";

import { useState, useEffect, useRef } from "react";
import { motion } from "motion/react";
import { ArrowLeft, Maximize2 } from "lucide-react";
import Link from "next/link";

const gameInfo: Record<string, { title: string; color: string }> = {
  "adventures-in-space": { title: "Adventures in Space", color: "#00ffff" },
  "santa-vs-grunch": { title: "Santa vs. Grunch", color: "#ff4444" },
  "snake-jump": { title: "Snake Jump", color: "#00ff88" },
  bible_stories: { title: "Journey to Egypt", color: "#ff8800" },
  joseph_mary_run: { title: "Joseph & Mary Run", color: "#aa88ff" },
};

interface GamePlayerProps {
  gameId: string;
}

export default function GamePlayer({ gameId }: GamePlayerProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const iframeRef = useRef<HTMLIFrameElement>(null);

  const game = gameInfo[gameId];
  const basePath =
    process.env.NODE_ENV === "production" ? "/adventures-in-space" : "";
  const gameSrc = `${basePath}/games/${gameId}/index.html`;

  useEffect(() => {
    if (!game) {
      setError(true);
      return;
    }

    // Pygbag games take time to initialize after iframe loads
    // Hide loading overlay after a reasonable timeout
    const timeout = setTimeout(() => {
      setLoading(false);
    }, 3000);

    return () => clearTimeout(timeout);
  }, [game]);

  const handleIframeLoad = () => {
    // Give Pygbag a moment to start rendering
    setTimeout(() => setLoading(false), 1000);
  };

  const toggleFullscreen = () => {
    const iframe = iframeRef.current;
    if (iframe) {
      if (!document.fullscreenElement) {
        iframe.requestFullscreen?.();
      } else {
        document.exitFullscreen?.();
      }
    }
  };

  if (error || !game) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-8">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center"
        >
          <h1 className="text-4xl font-bold text-red-500 mb-4">
            Game Not Found
          </h1>
          <p className="text-gray-400 mb-8">
            The game you&apos;re looking for doesn&apos;t exist or hasn&apos;t been built yet.
          </p>
          <Link
            href="/"
            className="inline-flex items-center gap-2 px-6 py-3 bg-neon-cyan/20 border border-neon-cyan text-neon-cyan rounded-lg hover:bg-neon-cyan/30 transition-all"
          >
            <ArrowLeft size={20} />
            Back to Games
          </Link>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <motion.header
        className="flex items-center justify-between p-4 border-b border-white/10"
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
      >
        <div className="flex items-center gap-4">
          <Link
            href="/"
            className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
          >
            <ArrowLeft size={20} />
            <span className="hidden sm:inline">Back</span>
          </Link>
          <div
            className="h-6 w-px bg-white/20 hidden sm:block"
            aria-hidden="true"
          />
          <h1 className="text-lg font-bold" style={{ color: game.color }}>
            {game.title}
          </h1>
        </div>

        <button
          onClick={toggleFullscreen}
          className="p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
          title="Fullscreen"
        >
          <Maximize2 size={20} />
        </button>
      </motion.header>

      {/* Game Container */}
      <div className="flex-1 relative bg-black">
        {/* Loading overlay - fades out */}
        <motion.div
          className="absolute inset-0 flex flex-col items-center justify-center bg-dark-bg z-10 pointer-events-none"
          initial={{ opacity: 1 }}
          animate={{ opacity: loading ? 1 : 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="relative w-16 h-16 mb-4">
            <div className="absolute inset-0 border-4 border-transparent border-t-neon-cyan rounded-full animate-spin" />
            <div
              className="absolute inset-2 border-4 border-transparent border-t-neon-pink rounded-full animate-spin"
              style={{ animationDirection: "reverse", animationDuration: "1.5s" }}
            />
          </div>
          <p className="text-gray-400">Loading {game.title}...</p>
          <p className="text-gray-500 text-sm mt-2">
            This may take a moment for the first load
          </p>
        </motion.div>

        <iframe
          ref={iframeRef}
          src={gameSrc}
          className="w-full h-full min-h-[600px]"
          style={{ border: "none" }}
          onLoad={handleIframeLoad}
          allow="autoplay; fullscreen; cross-origin-isolated"
          title={game.title}
        />
      </div>

      {/* Controls hint */}
      <motion.footer
        className="p-4 border-t border-white/10 text-center text-gray-500 text-sm"
        initial={{ y: 50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.5 }}
      >
        <p>
          Use <kbd className="px-2 py-1 bg-white/10 rounded">Arrow Keys</kbd> to
          move • <kbd className="px-2 py-1 bg-white/10 rounded">Space</kbd> to
          shoot/jump
        </p>
      </motion.footer>
    </div>
  );
}
