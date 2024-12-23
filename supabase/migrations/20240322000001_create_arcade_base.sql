-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create games table
CREATE TABLE IF NOT EXISTS public.games (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    thumbnail_url TEXT,
    is_active BOOLEAN DEFAULT true,
    min_score INTEGER DEFAULT 0,
    max_score INTEGER,
    max_level INTEGER
);

-- Create players table (extends auth.users)
CREATE TABLE IF NOT EXISTS public.players (
    id UUID PRIMARY KEY REFERENCES auth.users(id),
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
    display_name TEXT NOT NULL,
    avatar_url TEXT,
    total_games_played INTEGER DEFAULT 0,
    last_played_at TIMESTAMPTZ
);

-- Create game_scores table
CREATE TABLE IF NOT EXISTS public.game_scores (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
    player_id UUID NOT NULL REFERENCES public.players(id),
    game_id UUID NOT NULL REFERENCES public.games(id),
    score INTEGER NOT NULL,
    level INTEGER NOT NULL,
    CONSTRAINT valid_score CHECK (score >= 0)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_game_scores_game_score 
    ON public.game_scores(game_id, score DESC);
CREATE INDEX IF NOT EXISTS idx_game_scores_player 
    ON public.game_scores(player_id);
CREATE INDEX IF NOT EXISTS idx_players_display_name 
    ON public.players(display_name);

-- Add comments
COMMENT ON TABLE public.games IS 'Available games in the arcade';
COMMENT ON TABLE public.players IS 'Player profiles extending auth.users';
COMMENT ON TABLE public.game_scores IS 'Game scores for all games'; 