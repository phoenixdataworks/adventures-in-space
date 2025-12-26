"""
Font management to avoid recreating fonts every frame.
"""

import pygame


class Fonts:
    """
    Centralized font management.
    
    Usage:
        # At game start:
        Fonts.init()
        
        # When drawing:
        text = Fonts.medium.render("Hello", True, (255, 255, 255))
        
        # Or with custom sizes:
        title_font = Fonts.get_size(72)
    """
    
    _initialized = False
    _cache = {}
    
    # Standard sizes
    tiny = None      # 16
    small = None     # 24
    medium = None    # 36
    large = None     # 48
    huge = None      # 72
    title = None     # 96
    
    @classmethod
    def init(cls, font_name=None):
        """
        Initialize standard font sizes.
        
        Args:
            font_name: Optional font file path or system font name
        """
        if cls._initialized:
            return
        
        # Initialize pygame font if needed
        if not pygame.font.get_init():
            pygame.font.init()
        
        cls.tiny = cls._create_font(font_name, 16)
        cls.small = cls._create_font(font_name, 24)
        cls.medium = cls._create_font(font_name, 36)
        cls.large = cls._create_font(font_name, 48)
        cls.huge = cls._create_font(font_name, 72)
        cls.title = cls._create_font(font_name, 96)
        
        cls._initialized = True
    
    @classmethod
    def _create_font(cls, font_name, size):
        """Create a font, with fallback to default"""
        try:
            if font_name:
                return pygame.font.Font(font_name, size)
            else:
                return pygame.font.Font(None, size)
        except Exception:
            return pygame.font.Font(None, size)
    
    @classmethod
    def get_size(cls, size, font_name=None):
        """
        Get a font of a specific size, cached for reuse.
        
        Args:
            size: Font size in pixels
            font_name: Optional font file path
            
        Returns:
            pygame.font.Font object
        """
        cache_key = (font_name, size)
        
        if cache_key not in cls._cache:
            cls._cache[cache_key] = cls._create_font(font_name, size)
        
        return cls._cache[cache_key]
    
    @classmethod
    def render_text(cls, text, size='medium', color=(255, 255, 255), antialias=True):
        """
        Convenience method to render text directly.
        
        Args:
            text: String to render
            size: 'tiny', 'small', 'medium', 'large', 'huge', 'title', or int
            color: RGB tuple
            antialias: Whether to antialias
            
        Returns:
            pygame.Surface with rendered text
        """
        cls.init()  # Ensure initialized
        
        if isinstance(size, int):
            font = cls.get_size(size)
        else:
            font = getattr(cls, size, cls.medium)
        
        return font.render(str(text), antialias, color)
    
    @classmethod
    def render_centered(cls, surface, text, y, size='medium', color=(255, 255, 255)):
        """
        Render text centered horizontally on a surface.
        
        Args:
            surface: Surface to draw on
            text: String to render
            y: Y position
            size: Font size (name or int)
            color: RGB tuple
        """
        rendered = cls.render_text(text, size, color)
        x = (surface.get_width() - rendered.get_width()) // 2
        surface.blit(rendered, (x, y))
    
    @classmethod
    def get_text_size(cls, text, size='medium'):
        """
        Get the size of rendered text without actually rendering it.
        
        Args:
            text: String to measure
            size: Font size (name or int)
            
        Returns:
            (width, height) tuple
        """
        cls.init()
        
        if isinstance(size, int):
            font = cls.get_size(size)
        else:
            font = getattr(cls, size, cls.medium)
        
        return font.size(str(text))
    
    @classmethod
    def clear_cache(cls):
        """Clear the font cache"""
        cls._cache.clear()
        cls._initialized = False
        cls.tiny = None
        cls.small = None
        cls.medium = None
        cls.large = None
        cls.huge = None
        cls.title = None


