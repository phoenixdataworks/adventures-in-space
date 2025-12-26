"""
Simple leaderboard system using browser localStorage for Pygbag games.
Works offline and persists across sessions on the same device.

For web deployment (Pygbag), scores are saved to browser localStorage.
For desktop, scores are saved to a local JSON file.
"""

import json
import sys

# Check if running in web/Pygbag environment
IS_WEB = sys.platform == "emscripten"

if IS_WEB:
    from platform import window
else:
    import os

class Leaderboard:
    """
    Simple leaderboard that stores top scores.
    Uses localStorage in web, JSON file on desktop.
    """
    
    def __init__(self, game_id: str, max_entries: int = 10):
        """
        Initialize the leaderboard.
        
        Args:
            game_id: Unique identifier for the game (e.g., "snake-jump")
            max_entries: Maximum number of scores to keep
        """
        self.game_id = game_id
        self.max_entries = max_entries
        self.storage_key = f"leaderboard_{game_id}"
        self._scores = []
        self.load()
    
    def load(self) -> list:
        """Load scores from storage."""
        try:
            if IS_WEB:
                data = window.localStorage.getItem(self.storage_key)
                if data:
                    self._scores = json.loads(data)
            else:
                filepath = self._get_file_path()
                if os.path.exists(filepath):
                    with open(filepath, 'r') as f:
                        self._scores = json.load(f)
        except Exception as e:
            print(f"Error loading leaderboard: {e}")
            self._scores = []
        
        return self._scores
    
    def save(self):
        """Save scores to storage."""
        try:
            data = json.dumps(self._scores)
            if IS_WEB:
                window.localStorage.setItem(self.storage_key, data)
            else:
                filepath = self._get_file_path()
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                with open(filepath, 'w') as f:
                    f.write(data)
        except Exception as e:
            print(f"Error saving leaderboard: {e}")
    
    def _get_file_path(self) -> str:
        """Get the file path for desktop storage."""
        # Store in user's home directory
        home = os.path.expanduser("~")
        return os.path.join(home, ".arcade_games", f"{self.game_id}_scores.json")
    
    def add_score(self, name: str, score: int, level: int = 0) -> int:
        """
        Add a new score to the leaderboard.
        
        Args:
            name: Player name (will be uppercased, max 10 chars)
            score: The score achieved
            level: Optional level reached
            
        Returns:
            The rank (1-based) of the new score, or 0 if not in top scores
        """
        name = name.upper()[:10].strip() or "ANON"
        
        entry = {
            "name": name,
            "score": score,
            "level": level
        }
        
        # Insert in sorted position
        self._scores.append(entry)
        self._scores.sort(key=lambda x: x["score"], reverse=True)
        
        # Find rank before trimming
        rank = 0
        for i, s in enumerate(self._scores):
            if s is entry:
                rank = i + 1
                break
        
        # Keep only top entries
        self._scores = self._scores[:self.max_entries]
        
        # If entry was trimmed, rank is 0
        if rank > self.max_entries:
            rank = 0
        
        self.save()
        return rank
    
    def get_scores(self) -> list:
        """Get all scores in order."""
        return self._scores.copy()
    
    def get_top(self, n: int = 5) -> list:
        """Get top N scores."""
        return self._scores[:n].copy()
    
    def is_high_score(self, score: int) -> bool:
        """Check if a score would make the leaderboard."""
        if len(self._scores) < self.max_entries:
            return True
        return score > self._scores[-1]["score"]
    
    def get_rank(self, score: int) -> int:
        """Get the rank a score would achieve (1-based), or 0 if not ranked."""
        for i, entry in enumerate(self._scores):
            if score > entry["score"]:
                return i + 1
        if len(self._scores) < self.max_entries:
            return len(self._scores) + 1
        return 0
    
    def clear(self):
        """Clear all scores."""
        self._scores = []
        self.save()


# Convenience functions for simple usage
_leaderboards = {}

def get_leaderboard(game_id: str) -> Leaderboard:
    """Get or create a leaderboard for a game."""
    if game_id not in _leaderboards:
        _leaderboards[game_id] = Leaderboard(game_id)
    return _leaderboards[game_id]

def add_score(game_id: str, name: str, score: int, level: int = 0) -> int:
    """Add a score to a game's leaderboard."""
    return get_leaderboard(game_id).add_score(name, score, level)

def get_top_scores(game_id: str, n: int = 5) -> list:
    """Get top N scores for a game."""
    return get_leaderboard(game_id).get_top(n)

def is_high_score(game_id: str, score: int) -> bool:
    """Check if a score would make the leaderboard."""
    return get_leaderboard(game_id).is_high_score(score)


