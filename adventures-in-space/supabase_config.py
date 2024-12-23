import os
import platform
import json


# Check if we're running in web mode
def is_web():
    return platform.system() == "Emscripten"


# Initialize variables
supabase = None
MOCK_LEADERBOARD = []

if not is_web():
    try:
        from supabase import create_client
        from dotenv import load_dotenv

        # Load environment variables
        load_dotenv()

        # Get environment variables with fallbacks
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY")

        if SUPABASE_URL and SUPABASE_KEY:
            # Initialize Supabase client
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except ImportError:
        print("Supabase or python-dotenv not installed. Using mock leaderboard.")
    except Exception as e:
        print(f"Error initializing Supabase: {e}")


async def save_score(player_name, score, level):
    if not supabase:
        # In web mode or if Supabase is not configured, save to mock leaderboard
        global MOCK_LEADERBOARD
        entry = {
            "player_name": player_name,
            "score": score,
            "level": level,
            "game_name": "adventures_in_space",
        }
        MOCK_LEADERBOARD.append(entry)
        # Sort by score in descending order
        MOCK_LEADERBOARD.sort(key=lambda x: x["score"], reverse=True)
        # Keep only top 5 scores
        MOCK_LEADERBOARD = MOCK_LEADERBOARD[:5]
        return entry

    try:
        data = {
            "player_name": player_name,
            "score": score,
            "level": level,
            "game_name": "adventures_in_space",
        }
        result = supabase.table("game_scores").insert(data).execute()
        return result.data
    except Exception as e:
        print(f"Error saving score: {e}")
        return None


async def get_leaderboard(limit=5):
    if not supabase:
        # In web mode or if Supabase is not configured, return mock leaderboard
        return MOCK_LEADERBOARD[:limit]

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
