import pygame
import sys
import random
from collections import Counter

# --- Constants ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
GREEN = (50, 200, 80)
BLUE = (60, 120, 220)
LIGHT_GREY = (220, 220, 220)
HOVER_GREY = (180, 180, 180)
DARK_GREY = (100, 100, 100)
WATER_BLUE = (80, 180, 255)

# --- Example LEVELS Data ---
LEVELS = [
    {
        'name': 'Grog the Ogre',
        'ai_class': 'Grog',
        'max_hp': 5,
        'jar_capacity': 5
    },
    {
        'name': 'Sylph the Sprite',
        'ai_class': 'Sylph',
        'max_hp': 7,
        'jar_capacity': 6
    },
    {
        'name': 'KRAKEN',
        'ai_class': 'KRAKEN',
        'max_hp': 10,
        'jar_capacity': 7
    }
]

# --- Reusable UI Classes ---
class Button:
    """A clickable button class."""
    def __init__(self, x, y, width, height, text, action_value=None, enabled=True):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action_value = action_value
        self.enabled = enabled
        self.font = pygame.font.SysFont('Arial', 30)

    def draw(self, surface):
        """Draws the button and handles hover effect."""
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)

        if not self.enabled:
            color = DARK_GREY
        elif is_hovered:
            color = HOVER_GREY
        else:
            color = LIGHT_GREY

        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2) # Border

        text_surf = self.font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, event):
        """Checks if the button was clicked."""
        if self.enabled and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

class HealthBar:
    """A health bar that visually represents HP."""
    def __init__(self, x, y, width, height, max_hp):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.max_hp = max_hp

    def draw(self, surface, current_hp):
        """Draws the health bar based on current HP."""
        if self.max_hp <= 0:
            ratio = 0
        else:
            ratio = max(0, min(1, current_hp / self.max_hp))
        
        # Background (max health)
        pygame.draw.rect(surface, RED, (self.x, self.y, self.width, self.height))
        # Foreground (current health)
        pygame.draw.rect(surface, GREEN, (self.x, self.y, self.width * ratio, self.height))
        # Border
        pygame.draw.rect(surface, BLACK, (self.x, self.y, self.width, self.height), 2)

# --- Core Game Logic ---

def determine_rps_outcome(player_move, monster_move):
    """Determines the winner of an RPS round."""
    if player_move == monster_move:
        return 'DRAW'
    elif (player_move == 'rock' and monster_move == 'scissors') or \
         (player_move == 'paper' and monster_move == 'rock') or \
         (player_move == 'scissors' and monster_move == 'paper'):
        return 'WIN'
    else:
        return 'LOSE'

# --- Monster AI Classes ---

class Monster:
    """Base class for all monsters."""
    def __init__(self, name, max_hp):
        self.name = name
        self.max_hp = max_hp
        self.current_hp = max_hp

    def choose_move(self, game_state):
        """AI logic for choosing a move. To be overridden by subclasses."""
        return random.choice(['rock', 'paper', 'scissors'])

class Grog(Monster):
    """Predictable AI: Follows a fixed pattern."""
    def __init__(self, name, max_hp):
        super().__init__(name, max_hp)
        self.pattern = ['rock', 'rock', 'paper', 'paper', 'scissors', 'scissors']
        self.turn_count = 0

    def choose_move(self, game_state):
        move = self.pattern[self.turn_count % len(self.pattern)]
        self.turn_count += 1
        return move

class Sylph(Monster):
    """Reactive AI: Counters the player's previous move."""
    def __init__(self, name, max_hp):
        super().__init__(name, max_hp)
        self.counter_moves = {'rock': 'paper', 'paper': 'scissors', 'scissors': 'rock'}

    def choose_move(self, game_state):
        if not game_state.player_move_history:
            return random.choice(['rock', 'paper', 'scissors'])
        
        player_last_move = game_state.player_move_history[-1]
        return self.counter_moves[player_last_move]

class KRAKEN(Monster):
    """Adaptive AI: Learns from player's move frequency."""
    def __init__(self, name, max_hp):
        super().__init__(name, max_hp)

    def choose_move(self, game_state):
        if not game_state.player_move_history:
            return random.choice(['rock', 'paper', 'scissors'])

        # Analyze player's move history
        move_counts = Counter(game_state.player_move_history)
        most_common_move = move_counts.most_common(1)[0][0]  # FIXED

        # Determine the counter to the player's most frequent move
        counter_move = {'rock': 'paper', 'paper': 'scissors', 'scissors': 'rock'}[most_common_move]

        # Create a weighted list to bias the choice
        # 60% chance to play the counter, 20% for each other move
        weighted_choices = [counter_move] * 6 + \
                           [m for m in ['rock', 'paper', 'scissors'] if m != counter_move] * 2

        return random.choice(weighted_choices)

# --- Central Game State Class ---

class GameStateData:
    """A single source of truth for all game data."""
    def __init__(self):
        self.current_level_index = 0
        self.monster = None
        self.jar_capacity = 0
        self.water_level = 0
        self.power_meter_charge = 0
        self.player_move_history = []  # FIXED
        self.feedback_message = "Choose your move to begin!"
        self.last_round_outcome = None
        self.clairvoyance_active = False
        self.clairvoyance_reveal = None
        self.righteous_fury_active = False

    def setup_level(self):
        """Configures the game state for the current level."""
        if self.current_level_index < 0 or self.current_level_index >= len(LEVELS):
            self.current_level_index = 0

        level_data = LEVELS[self.current_level_index]
        ai_class_name = level_data['ai_class']
        
        # Instantiate the correct monster AI class
        if ai_class_name == 'Grog':
            self.monster = Grog(level_data['name'], level_data['max_hp'])
        elif ai_class_name == 'Sylph':
            self.monster = Sylph(level_data['name'], level_data['max_hp'])
        elif ai_class_name == 'KRAKEN':
            self.monster = KRAKEN(level_data['name'], level_data['max_hp'])
        else: # Default fallback
            self.monster = Monster(level_data['name'], level_data['max_hp'])

        self.jar_capacity = level_data['jar_capacity']
        self.water_level = 0
        self.power_meter_charge = 0
        self.player_move_history = []  # FIXED
        self.feedback_message = f"A new foe appears: {self.monster.name}!"
        self.last_round_outcome = None
        self.clairvoyance_active = False
        self.clairvoyance_reveal = None
        self.righteous_fury_active = False

# --- Game State Machine ---

class BaseState:
    """Base class for all game states."""
    def __init__(self, state_manager, game_data):
        self.state_manager = state_manager
        self.game_data = game_data

    def handle_events(self, events):
        pass

    def update(self):
        pass

    def render(self, screen):
        pass

class MainMenuState(BaseState):
    def __init__(self, state_manager, game_data):
        super().__init__(state_manager, game_data)
        self.title_font = pygame.font.SysFont('Arial', 60)
        self.start_button = Button(SCREEN_WIDTH // 2 - 150, 400, 300, 80, "Start Game")

    def handle_events(self, events):
        for event in events:
            if self.start_button.is_clicked(event):
                self.game_data.setup_level()
                self.state_manager.transition_to(PlayingState)

    def render(self, screen):
        screen.fill(BLUE)
        title_surf = self.title_font.render("The Prince in the Perilous Pot", True, WHITE)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 200))
        screen.blit(title_surf, title_rect)
        self.start_button.draw(screen)

class PlayingState(BaseState):
    def __init__(self, state_manager, game_data):
        super().__init__(state_manager, game_data)
        self.font = pygame.font.SysFont('Arial', 24)
        self.feedback_font = pygame.font.SysFont('Arial', 32, bold=True)
        self.setup_ui()

    def setup_ui(self):
        """Initializes UI elements for the current level."""
        # RPS Buttons
        self.rock_button = Button(200, 580, 150, 80, "Rock", 'rock')
        self.paper_button = Button(425, 580, 150, 80, "Paper", 'paper')
        self.scissors_button = Button(650, 580, 150, 80, "Scissors", 'scissors')
        self.rps_buttons = [self.rock_button, self.paper_button, self.scissors_button]

        # Power Buttons
        self.clairvoyance_button = Button(50, 450, 150, 50, "Clairvoyance", 'clairvoyance')
        self.bail_out_button = Button(50, 510, 150, 50, "Bail Out", 'bail_out')
        self.righteous_fury_button = Button(800, 450, 150, 50, "Righteous Fury", 'righteous_fury')
        self.power_buttons = [self.clairvoyance_button, self.bail_out_button, self.righteous_fury_button]

        # Health Bar
        self.monster_health_bar = HealthBar(50, 80, 400, 40, self.game_data.monster.max_hp)

    def handle_events(self, events):
        for event in events:
            # Handle RPS choice
            for button in self.rps_buttons:
                if button.is_clicked(event):
                    self.process_turn(button.action_value)
                    return # Process one action per frame

            # Handle Power activation
            for button in self.power_buttons:
                if button.is_clicked(event):
                    self.activate_power(button.action_value)
                    return

    def activate_power(self, power_name):
        if self.game_data.power_meter_charge < 3:
            self.game_data.feedback_message = "Power meter is not full!"
            return

        self.game_data.power_meter_charge = 0 # Consume power

        if power_name == 'clairvoyance':
            self.game_data.clairvoyance_active = True
            self.game_data.clairvoyance_reveal = self.game_data.monster.choose_move(self.game_data)
            self.game_data.feedback_message = "The monster's next move is revealed!"
        elif power_name == 'bail_out':
            self.game_data.water_level = max(0, self.game_data.water_level - 1)
            self.game_data.feedback_message = "The prince bailed out some water!"
        elif power_name == 'righteous_fury':
            self.game_data.righteous_fury_active = True
            self.game_data.feedback_message = "Your next win will be a critical hit!"

    def process_turn(self, player_move):
        # If clairvoyance was active, use the revealed move. Otherwise, get a new one.
        if self.game_data.clairvoyance_active:
            monster_move = self.game_data.clairvoyance_reveal
            self.game_data.clairvoyance_active = False
            self.game_data.clairvoyance_reveal = None
        else:
            monster_move = self.game_data.monster.choose_move(self.game_data)

        self.game_data.player_move_history.append(player_move)
        outcome = determine_rps_outcome(player_move, monster_move)
        self.game_data.last_round_outcome = outcome

        # Update game state based on outcome
        if outcome == 'WIN':
            damage = 2 if self.game_data.righteous_fury_active else 1
            self.game_data.monster.current_hp = max(0, self.game_data.monster.current_hp - damage)
            self.game_data.feedback_message = f"Your {player_move} beats {monster_move}! You deal {damage} damage!"
            if self.game_data.righteous_fury_active:
                self.game_data.righteous_fury_active = False # Consume buff
        elif outcome == 'LOSE':
            self.game_data.water_level = min(self.game_data.jar_capacity, self.game_data.water_level + 1)
            self.game_data.feedback_message = f"Their {monster_move} beats your {player_move}! The water rises!"
        elif outcome == 'DRAW':
            self.game_data.power_meter_charge = min(3, self.game_data.power_meter_charge + 1)
            self.game_data.feedback_message = f"A stalemate! You both chose {player_move}."

    def update(self):
        # Check for win/loss conditions
        if self.game_data.monster.current_hp <= 0:
            if self.game_data.current_level_index < len(LEVELS) - 1:
                self.state_manager.transition_to(LevelTransitionState)
            else:
                self.state_manager.transition_to(VictoryState)
        elif self.game_data.water_level >= self.game_data.jar_capacity:
            self.state_manager.transition_to(GameOverState)

        # Update power button enabled state
        power_ready = self.game_data.power_meter_charge >= 3
        for button in self.power_buttons:
            button.enabled = power_ready

    def render(self, screen):
        screen.fill(WHITE)
        
        # --- Draw Monster Side (Left) ---
        monster_name_surf = self.font.render(self.game_data.monster.name, True, BLACK)
        screen.blit(monster_name_surf, (50, 40))
        self.monster_health_bar.draw(screen, self.game_data.monster.current_hp)
        
        # Placeholder for monster graphic
        pygame.draw.rect(screen, RED, (150, 150, 200, 250))
        
        # --- Draw Prince Side (Right) ---
        prince_title_surf = self.font.render("Prince in the Perilous Pot", True, BLACK)
        screen.blit(prince_title_surf, (600, 40))
        
        # Jar visualization
        jar_rect = pygame.Rect(650, 150, 200, 350)
        pygame.draw.rect(screen, LIGHT_GREY, jar_rect)
        pygame.draw.rect(screen, BLACK, jar_rect, 3)

        # Water level
        water_height = (self.game_data.water_level / self.game_data.jar_capacity) * jar_rect.height
        water_rect = pygame.Rect(jar_rect.left, jar_rect.bottom - water_height, jar_rect.width, water_height)
        pygame.draw.rect(screen, WATER_BLUE, water_rect)

        # Placeholder for prince graphic
        prince_y_offset = water_height * 0.5 # Prince "floats" on water
        pygame.draw.circle(screen, (255, 220, 150), (jar_rect.centerx, jar_rect.bottom - 50 - prince_y_offset), 30)

        # Water level text
        water_text = f"Water Level: {self.game_data.water_level} / {self.game_data.jar_capacity}"
        water_surf = self.font.render(water_text, True, BLACK)
        screen.blit(water_surf, (650, 110))

        # --- Draw Power Meter ---
        power_meter_text = f"Power Meter: {self.game_data.power_meter_charge} / 3"
        power_surf = self.font.render(power_meter_text, True, BLACK)
        screen.blit(power_surf, (SCREEN_WIDTH // 2 - power_surf.get_width() // 2, 10))

        # --- Draw Feedback Text ---
        feedback_surf = self.feedback_font.render(self.game_data.feedback_message, True, BLACK)
        feedback_rect = feedback_surf.get_rect(center=(SCREEN_WIDTH // 2, 530))
        screen.blit(feedback_surf, feedback_rect)

        # --- Draw Clairvoyance Reveal ---
        if self.game_data.clairvoyance_active and self.game_data.clairvoyance_reveal:
            reveal_text = f"Monster's move: {self.game_data.clairvoyance_reveal.upper()}"
            reveal_surf = self.feedback_font.render(reveal_text, True, RED)
            reveal_rect = reveal_surf.get_rect(center=(SCREEN_WIDTH // 2, 100))
            screen.blit(reveal_surf, reveal_rect)

        # --- Draw Buttons ---
        for button in self.rps_buttons:
            button.draw(screen)
        for button in self.power_buttons:
            button.draw(screen)

class LevelTransitionState(BaseState):
    def __init__(self, state_manager, game_data):
        super().__init__(state_manager, game_data)
        self.message_font = pygame.font.SysFont('Arial', 50)
        self.timer_start = pygame.time.get_ticks()
        self.transition_delay = 3000 # 3 seconds

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.timer_start > self.transition_delay:
            self.game_data.current_level_index += 1
            self.game_data.setup_level()
            self.state_manager.transition_to(PlayingState)

    def render(self, screen):
        screen.fill(GREEN)
        message = f"{self.game_data.monster.name} has been defeated!"
        msg_surf = self.message_font.render(message, True, WHITE)
        msg_rect = msg_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(msg_surf, msg_rect)

class GameOverState(BaseState):
    def __init__(self, state_manager, game_data):
        super().__init__(state_manager, game_data)
        self.message_font = pygame.font.SysFont('Arial', 70)
        self.restart_button = Button(SCREEN_WIDTH // 2 - 150, 400, 300, 80, "Restart Game")

    def handle_events(self, events):
        for event in events:
            if self.restart_button.is_clicked(event):
                self.game_data.current_level_index = 0
                self.game_data.setup_level()
                self.state_manager.transition_to(PlayingState)

    def render(self, screen):
        screen.fill(RED)
        msg_surf = self.message_font.render("Game Over", True, WHITE)
        msg_rect = msg_surf.get_rect(center=(SCREEN_WIDTH // 2, 250))
        screen.blit(msg_surf, msg_rect)
        self.restart_button.draw(screen)

class VictoryState(BaseState):
    def __init__(self, state_manager, game_data):
        super().__init__(state_manager, game_data)
        self.message_font = pygame.font.SysFont('Arial', 70)
        self.restart_button = Button(SCREEN_WIDTH // 2 - 150, 400, 300, 80, "Play Again")

    def handle_events(self, events):
        for event in events:
            if self.restart_button.is_clicked(event):
                self.game_data.current_level_index = 0
                self.game_data.setup_level()
                self.state_manager.transition_to(PlayingState)

    def render(self, screen):
        screen.fill(GREEN)
        msg_surf = self.message_font.render("You Saved the Prince!", True, WHITE)
        msg_rect = msg_surf.get_rect(center=(SCREEN_WIDTH // 2, 250))
        screen.blit(msg_surf, msg_rect)
        self.restart_button.draw(screen)

# --- Game State Manager ---

class GameStateManager:
    """Manages the active game state and transitions."""
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("The Prince in the Perilous Pot")
        self.clock = pygame.time.Clock()
        self.game_data = GameStateData()
        self.current_state = MainMenuState(self, self.game_data)

    def transition_to(self, new_state_class):
        """Changes the current active state."""
        self.current_state = new_state_class(self, self.game_data)

    def run(self):
        """The main game loop."""
        running = True
        while running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False

            self.current_state.handle_events(events)
            self.current_state.update()
            self.current_state.render(self.screen)

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

# --- Main Execution ---

if __name__ == "__main__":
    game_manager = GameStateManager()
    game_manager.run()