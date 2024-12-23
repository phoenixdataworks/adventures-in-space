-- Enable Row Level Security
ALTER TABLE public.games ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.players ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.game_scores ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
CREATE POLICY "Enable read access for all users" ON public.games
    FOR SELECT USING (true);

CREATE POLICY "Enable read access for all users" ON public.players
    FOR SELECT USING (true);

CREATE POLICY "Enable users to update their own profile" ON public.players
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Enable users to insert their own profile" ON public.players
    FOR INSERT WITH CHECK (auth.uid() = id);

CREATE POLICY "Enable read access for all users" ON public.game_scores
    FOR SELECT USING (true);

CREATE POLICY "Enable insert for authenticated users" ON public.game_scores
    FOR INSERT WITH CHECK (auth.uid() = player_id);

-- Create trigger to update player stats
CREATE OR REPLACE FUNCTION update_player_stats()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE public.players
    SET total_games_played = total_games_played + 1,
        last_played_at = NOW()
    WHERE id = NEW.player_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_game_score_insert
    AFTER INSERT ON public.game_scores
    FOR EACH ROW
    EXECUTE FUNCTION update_player_stats(); 