from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client with environment variables
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))


async def save_score(player_name, score, level):
    try:
        data = {
            "player_name": player_name,
            "score": score,
            "level": level,
            "game_name": "adventures_in_space",  # Useful for multiple games
        }
        result = supabase.table("game_scores").insert(data).execute()
        return result.data
    except Exception as e:
        print(f"Error saving score: {e}")
        return None


async def get_leaderboard(limit=5):
    try:
        result = (
            supabase.table("game_scores")
            .select("*")
            .eq("game_name", "adventures_in_space")
            .order("score", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data
    except Exception as e:
        print(f"Error getting leaderboard: {e}")
        return []
