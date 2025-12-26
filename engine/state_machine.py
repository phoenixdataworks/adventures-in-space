"""
State machine for managing game states (menu, playing, paused, game over, etc.)
"""

from abc import ABC, abstractmethod


class GameState(ABC):
    """
    Abstract base class for game states.
    
    Usage:
        class PlayingState(GameState):
            def enter(self):
                self.game.reset_level()
            
            def handle_events(self, events):
                for event in events:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.game.state_machine.change('paused')
            
            def update(self, dt):
                self.game.player.update(dt)
                self.game.check_collisions()
            
            def draw(self, screen):
                self.game.draw_world(screen)
                self.game.draw_hud(screen)
    """
    
    def __init__(self, game):
        """
        Initialize the state.
        
        Args:
            game: Reference to the main game object
        """
        self.game = game
    
    def enter(self):
        """Called when entering this state"""
        pass
    
    def exit(self):
        """Called when leaving this state"""
        pass
    
    @abstractmethod
    def handle_events(self, events):
        """
        Handle input events.
        
        Args:
            events: List of pygame events
        """
        pass
    
    @abstractmethod
    def update(self, dt):
        """
        Update game logic.
        
        Args:
            dt: Delta time since last frame
        """
        pass
    
    @abstractmethod
    def draw(self, screen):
        """
        Draw the state.
        
        Args:
            screen: Pygame surface to draw on
        """
        pass


class StateMachine:
    """
    Manages transitions between game states.
    
    Usage:
        sm = StateMachine()
        sm.register('menu', MenuState(game))
        sm.register('playing', PlayingState(game))
        sm.register('paused', PausedState(game))
        sm.register('game_over', GameOverState(game))
        
        sm.change('menu')  # Start with menu
        
        # In game loop:
        sm.handle_events(pygame.event.get())
        sm.update(dt)
        sm.draw(screen)
    """
    
    def __init__(self):
        self.states = {}
        self.current_state = None
        self.previous_state = None
        self.state_history = []
        self.max_history = 5
    
    def register(self, name, state):
        """
        Register a state.
        
        Args:
            name: String identifier for the state
            state: GameState instance
        """
        self.states[name] = state
    
    def change(self, state_name, **kwargs):
        """
        Transition to a new state.
        
        Args:
            state_name: Name of the state to transition to
            **kwargs: Additional arguments passed to the new state's enter() method
        """
        if state_name not in self.states:
            raise ValueError(f"Unknown state: {state_name}")
        
        # Exit current state
        if self.current_state is not None:
            self.current_state.exit()
            
            # Track history
            self.previous_state = self.current_state
            current_name = self._get_state_name(self.current_state)
            self.state_history.append(current_name)
            if len(self.state_history) > self.max_history:
                self.state_history.pop(0)
        
        # Enter new state
        self.current_state = self.states[state_name]
        self.current_state.enter(**kwargs) if kwargs else self.current_state.enter()
    
    def _get_state_name(self, state):
        """Get the name of a state"""
        for name, s in self.states.items():
            if s == state:
                return name
        return None
    
    def go_back(self):
        """Return to the previous state"""
        if self.state_history:
            previous_name = self.state_history.pop()
            self.change(previous_name)
    
    def handle_events(self, events):
        """Pass events to the current state"""
        if self.current_state:
            self.current_state.handle_events(events)
    
    def update(self, dt=1.0):
        """Update the current state"""
        if self.current_state:
            self.current_state.update(dt)
    
    def draw(self, screen):
        """Draw the current state"""
        if self.current_state:
            self.current_state.draw(screen)
    
    @property
    def current_state_name(self):
        """Get the name of the current state"""
        return self._get_state_name(self.current_state)
    
    def is_state(self, state_name):
        """Check if we're in a specific state"""
        return self.current_state == self.states.get(state_name)


class TransitionState(GameState):
    """
    A special state for transitions between states with effects.
    
    Usage:
        transition = TransitionState(game, 'fade')
        transition.setup(from_state='playing', to_state='level2', duration=30)
        sm.register('transition', transition)
    """
    
    def __init__(self, game, effect='fade'):
        super().__init__(game)
        self.effect = effect
        self.from_state = None
        self.to_state = None
        self.duration = 30
        self.current_frame = 0
        self.callback = None
    
    def setup(self, from_state=None, to_state=None, duration=30, callback=None):
        """
        Configure the transition.
        
        Args:
            from_state: State to transition from (optional, uses current)
            to_state: State to transition to
            duration: Transition duration in frames
            callback: Function to call at midpoint (e.g., to load level)
        """
        self.from_state = from_state
        self.to_state = to_state
        self.duration = duration
        self.callback = callback
    
    def enter(self):
        self.current_frame = 0
    
    def handle_events(self, events):
        pass  # No input during transitions
    
    def update(self, dt):
        self.current_frame += 1
        
        # At midpoint, execute callback and change state
        if self.current_frame == self.duration // 2:
            if self.callback:
                self.callback()
        
        # Transition complete
        if self.current_frame >= self.duration:
            if self.to_state:
                self.game.state_machine.change(self.to_state)
    
    def draw(self, screen):
        import pygame
        
        progress = self.current_frame / self.duration
        
        if self.effect == 'fade':
            # Fade to black then fade in
            if progress < 0.5:
                alpha = int(255 * (progress * 2))
            else:
                alpha = int(255 * (1 - (progress - 0.5) * 2))
            
            overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, alpha))
            screen.blit(overlay, (0, 0))
        
        elif self.effect == 'wipe':
            # Horizontal wipe
            width = int(screen.get_width() * progress)
            pygame.draw.rect(screen, (0, 0, 0), (0, 0, width, screen.get_height()))


