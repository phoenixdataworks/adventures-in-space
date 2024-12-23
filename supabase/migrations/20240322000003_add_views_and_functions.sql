-- Create views
CREATE OR REPLACE VIEW public.game_leaderboards AS
SELECT 
    g.name as game_name,
    p.display_name as player_name,
    gs.score,
    gs.level,
    gs.created_at,
    RANK() OVER (PARTITION BY g.id ORDER BY gs.score DESC) as rank
FROM public.game_scores gs
JOIN public.games g ON g.id = gs.game_id
JOIN public.players p ON p.id = gs.player_id;

-- Create functions
CREATE OR REPLACE FUNCTION get_game_top_scores(game_name_param TEXT, limit_param INTEGER DEFAULT 5)
RETURNS TABLE (
    rank BIGINT,
    player_name TEXT,
    score INTEGER,
    level INTEGER,
    created_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        l.rank,
        l.player_name,
        l.score,
        l.level,
        l.created_at
    FROM public.game_leaderboards l
    WHERE l.game_name = game_name_param
    AND l.rank <= limit_param
    ORDER BY l.rank;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to get player stats
CREATE OR REPLACE FUNCTION get_player_stats(player_id_param UUID)
RETURNS TABLE (
    display_name TEXT,
    total_games INTEGER,
    highest_score INTEGER,
    favorite_game TEXT,
    last_played TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.display_name,
        p.total_games_played,
        COALESCE(MAX(gs.score), 0) as highest_score,
        (
            SELECT g.name
            FROM public.game_scores gs2
            JOIN public.games g ON g.id = gs2.game_id
            WHERE gs2.player_id = player_id_param
            GROUP BY g.id, g.name
            ORDER BY COUNT(*) DESC
            LIMIT 1
        ) as favorite_game,
        p.last_played_at
    FROM public.players p
    LEFT JOIN public.game_scores gs ON gs.player_id = p.id
    WHERE p.id = player_id_param
    GROUP BY p.id, p.display_name, p.total_games_played, p.last_played_at;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Insert initial games
INSERT INTO public.games (name, description, min_score, max_score) VALUES
('Adventures in Space', 'Defend space territory from mysterious asteroids using your advanced Nerf weapon system.', 0, NULL),
('Snake Jump', 'Guide your snake through challenging obstacles while collecting power-ups.', 0, NULL)
ON CONFLICT (name) DO NOTHING;

-- Add comments
COMMENT ON VIEW public.game_leaderboards IS 'Consolidated view of all game leaderboards';
COMMENT ON FUNCTION get_game_top_scores IS 'Get top scores for a specific game';
COMMENT ON FUNCTION get_player_stats IS 'Get comprehensive stats for a player'; 