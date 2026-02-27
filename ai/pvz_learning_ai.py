#!/usr/bin/env python3
"""
Plants vs Zombies - AI Learning System
Uses genetic algorithm to learn optimal strategies
"""

import pygame
import random
import time
import math
import json
import os

# Initialize
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
GRID_COLS = 9
GRID_ROWS = 5
CELL_WIDTH = 80
CELL_HEIGHT = 90
GRID_OFFSET_X = 120
GRID_OFFSET_Y = 85
TOP_BAR_HEIGHT = 75
SIDEBAR_WIDTH = 110

# Color Palette
BLACK = (20, 20, 20)
WHITE = (250, 248, 240)
PAPER_COLOR = (255, 253, 245)
GREEN_PENCIL = (46, 139, 87)
YELLOW_PENCIL = (255, 220, 50)
BROWN_PENCIL = (160, 120, 70)
RED_PENCIL = (220, 60, 60)
GRAY_PENCIL = (150, 150, 150)
GRASS_1 = (180, 220, 120)
GRASS_2 = (160, 200, 100)
GRASS_3 = (140, 180, 80)

# Setup screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("PVZ - AI Learning Edition")
clock = pygame.time.Clock()

font = pygame.font.Font(None, 24)
title_font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 18)

# ============================================
# AI LEARNING SYSTEM
# ============================================

class LearningAI:
    """AI that learns from experience using genetic algorithm principles"""
    
    def __init__(self):
        self.generation = 1
        self.games_played = 0
        self.best_wave = 0
        self.best_level = 1
        self.history = []
        
        # Level system
        self.current_level = 1
        self.waves_per_level = 5
        self.total_waves_completed = 0
        
        # Learning weights (genome)
        self.strategy_genes = {
            'sunflower_priority': 1.0,
            'early_defense': 0.8,
            'row_coverage': 0.9,
            'wallnut_timing': 0.7,
            'peashooter_density': 1.0,
            'adapt_to_waves': 0.5,
            'aggressive': 0.6,
        }
        
        self.success_patterns = {
            'level_1_strategies': [],
            'level_3_strategies': [],
            'level_5_strategies': [],
        }
        
        self.current_actions = []
    
    def get_level_difficulty(self, level):
        """Get difficulty multipliers for a given level"""
        # Difficulty increases with each level
        zombie_hp_mult = 1.0 + (level - 1) * 0.2  # +20% HP per level
        zombie_speed_mult = 1.0 + (level - 1) * 0.1  # +10% speed per level
        zombie_damage_mult = 1.0 + (level - 1) * 0.15  # +15% damage per level
        spawn_rate_mult = max(0.5, 1.0 - (level - 1) * 0.08)  # Spawn faster
        
        return {
            'zombie_hp': zombie_hp_mult,
            'zombie_speed': zombie_speed_mult,
            'zombie_damage': zombie_damage_mult,
            'spawn_rate': spawn_rate_mult
        }
        
    def record_action(self, action, result):
        """Record an action and its result"""
        self.current_actions.append({
            'action': action,
            'result': result,
            'wave': self.wave,
            'sun': self.sun_count,
            'zombies': len(self.zombies)
        })
    
    def learn_from_game(self, level_reached, wave_reached_in_level):
        """Learn from the completed game"""
        self.games_played += 1
        
        # Calculate total waves
        total_waves = (level_reached - 1) * self.waves_per_level + wave_reached_in_level
        
        # Update best performance
        if total_waves > self.best_wave:
            self.best_wave = total_waves
        if level_reached > self.best_level:
            self.best_level = level_reached
        
        # Analyze what worked
        game_data = {
            'generation': self.generation,
            'level_reached': level_reached,
            'wave_reached': wave_reached_in_level,
            'total_waves': total_waves,
            'actions': self.current_actions.copy(),
            'timestamp': time.time()
        }
        
        self.history.append(game_data)
        
        # Extract successful patterns
        if level_reached >= 2:
            self._extract_success_patterns(game_data)
        
        # Adapt strategy based on results
        self._adapt_strategy(level_reached, wave_reached_in_level)
        
        # Reset for next game
        self.current_actions = []
        
        # Evolve every 5 games
        if self.games_played % 5 == 0:
            self._evolve()
    
    def _extract_success_patterns(self, game_data):
        """Extract what worked in successful games"""
        level = game_data['level_reached']
        
        # Count plant placements
        placements_by_level = {}
        for action in game_data['actions']:
            if action['action'].startswith('Placed'):
                lvl = action.get('level', 1)
                if lvl not in placements_by_level:
                    placements_by_level[lvl] = []
                placements_by_level[lvl].append(action['action'])
        
        # Store by level tiers
        for lvl, actions in placements_by_level.items():
            if lvl <= 2:
                self.success_patterns['level_1_strategies'].extend(actions)
            elif lvl <= 4:
                self.success_patterns['level_3_strategies'].extend(actions)
            else:
                self.success_patterns['level_5_strategies'].extend(actions)
    
    def _adapt_strategy(self, level_reached, wave_reached):
        """Adjust strategy based on performance"""
        total_progress = (level_reached - 1) * 5 + wave_reached
        
        if total_progress < 3:
            # Died very early - need more defense
            self.strategy_genes['sunflower_priority'] *= 0.9
            self.strategy_genes['early_defense'] *= 1.15
            self.strategy_genes['row_coverage'] *= 1.1
        elif total_progress < 7:
            # Struggling early
            self.strategy_genes['sunflower_priority'] *= 0.95
            self.strategy_genes['peashooter_density'] *= 1.08
        elif total_progress < 12:
            # Doing okay
            self.strategy_genes['sunflower_priority'] *= 1.03
            self.strategy_genes['aggressive'] *= 1.05
        else:
            # Doing well
            self.strategy_genes['aggressive'] *= 1.1
            self.strategy_genes['sunflower_priority'] *= 1.05
    
    def _evolve(self):
        """Evolve to next generation"""
        self.generation += 1
        
        # Mutation: randomly adjust some genes
        if random.random() < 0.3:
            gene = random.choice(list(self.strategy_genes.keys()))
            mutation = random.uniform(0.9, 1.1)
            self.strategy_genes[gene] *= mutation
            print(f"EVOLUTION: Mutation in {gene} = {self.strategy_genes[gene]:.2f}")
        
        print(f"GENERATION {self.generation} | Best: Wave {self.best_wave} | Games: {self.games_played}")
        print(f"Strategy: {self.strategy_genes}")
    
    def decide(self, game_state):
        """Make decision based on learned strategy"""
        self.level = game_state['level']
        self.wave = game_state['wave']
        self.sun_count = game_state['sun']
        self.zombies = game_state['zombies']
        self.grid = game_state['grid']
        self.plants = game_state['plants']
        
        # Get situational scores
        sunflowers = sum(1 for p in self.plants if p.type == "sunflower")
        peashooters_by_row = [0] * GRID_ROWS
        wallnuts_by_row = [0] * GRID_ROWS
        
        for plant in self.plants:
            if plant.type == "peashooter":
                peashooters_by_row[plant.row] += 1
            elif plant.type == "wallnut":
                wallnuts_by_row[plant.row] += 1
        
        # Score each possible action
        best_action = None
        best_score = -1
        
        # Evaluate all possible placements
        for col in range(GRID_COLS):
            for row in range(GRID_ROWS):
                if self.grid[col][row] is None:
                    for plant_type in ["sunflower", "peashooter", "wallnut"]:
                        score = self._score_action(col, row, plant_type, 
                                                 sunflowers, peashooters_by_row, 
                                                 wallnuts_by_row)
                        if score > best_score and self._can_afford(plant_type):
                            best_score = score
                            best_action = (col, row, plant_type)
        
        # Also consider collecting suns
        suns_available = len([s for s in game_state['suns'] if s.active])
        if suns_available > 0:
            return "collect_sun"
        
        if best_action:
            col, row, plant_type = best_action
            return f"place_{plant_type}_{col}_{row}"
        
        return "wait"
    
    def _score_action(self, col, row, plant_type, sunflowers, 
                     peashooters_by_row, wallnuts_by_row):
        """Score a potential action based on learned strategy"""
        score = 0
        
        # Level-based difficulty adjustment
        level_difficulty = (self.level - 1) * 0.2
        
        # Base scores from genes
        if plant_type == "sunflower":
            score = 50 * self.strategy_genes['sunflower_priority']
            score += (3 - col) * 10
            score -= sunflowers * 5
            # Higher levels need more economy
            score += self.level * 3
        
        elif plant_type == "peashooter":
            score = 60 * self.strategy_genes['row_coverage']
            score += (5 - abs(col - 4)) * 5
            
            # Check for zombies in this row
            zombies_in_row = sum(1 for z in self.zombies if z.row == row and not z.dying)
            if zombies_in_row > 0:
                score *= (1.5 + level_difficulty)
            
            score -= peashooters_by_row[row] * 20
            
            # Early defense more important at higher levels
            if self.wave <= 2 and col <= 3:
                score *= self.strategy_genes['early_defense'] * (1 + level_difficulty * 0.5)
        
        elif plant_type == "wallnut":
            score = 40 * self.strategy_genes['wallnut_timing']
            if peashooters_by_row[row] > 0:
                score *= 2
            score += col * 3
            score -= wallnuts_by_row[row] * 25
            # Wallnuts more important at higher levels
            score *= (1 + level_difficulty * 0.8)
        
        # Wave and level adjustments
        if self.level >= 3:
            if plant_type in ["peashooter", "wallnut"]:
                score *= 1.4
        
        if self.wave >= 4:
            if plant_type in ["peashooter", "wallnut"]:
                score *= 1.3
        
        return score
    
    def _can_afford(self, plant_type):
        costs = {"sunflower": 50, "peashooter": 100, "wallnut": 50}
        return self.sun_count >= costs.get(plant_type, 999)
    
    def save(self):
        """Save learning data"""
        data = {
            'generation': self.generation,
            'games_played': self.games_played,
            'best_wave': self.best_wave,
            'strategy_genes': self.strategy_genes,
            'history': self.history[-50:]  # Keep last 50 games
        }
        with open('ai_learning_data.json', 'w') as f:
            json.dump(data, f, indent=2)
    
    def load(self):
        """Load learning data"""
        if os.path.exists('ai_learning_data.json'):
            try:
                with open('ai_learning_data.json', 'r') as f:
                    data = json.load(f)
                    self.generation = data.get('generation', 1)
                    self.games_played = data.get('games_played', 0)
                    self.best_wave = data.get('best_wave', 0)
                    self.strategy_genes = data.get('strategy_genes', self.strategy_genes)
                    self.history = data.get('history', [])
                    print(f"Loaded AI: Gen {self.generation}, Best Wave {self.best_wave}")
            except Exception as e:
                print(f"Could not load AI data: {e}")

# ============================================
# GAME CLASSES (simplified for readability)
# ============================================

class Plant:
    def __init__(self, col, row, plant_type):
        self.col = col
        self.row = row
        self.type = plant_type
        self.x = GRID_OFFSET_X + col * CELL_WIDTH + CELL_WIDTH // 2
        self.y = GRID_OFFSET_Y + row * CELL_HEIGHT + CELL_HEIGHT // 2
        
        if plant_type == "sunflower":
            self.hp = 80
            self.cost = 50
            self.last_sun = time.time()
        elif plant_type == "peashooter":
            self.hp = 100
            self.cost = 100
            self.last_shot = time.time()
        elif plant_type == "wallnut":
            self.hp = 400
            self.cost = 50
        
        self.max_hp = self.hp
        self.anim_offset = random.random() * math.pi * 2
    
    def draw(self, surface):
        bounce = math.sin(time.time() * 2 + self.anim_offset) * 3
        
        if self.type == "sunflower":
            # Simple sunflower
            pygame.draw.circle(surface, YELLOW_PENCIL, (self.x, int(self.y - 10 + bounce)), 20)
            pygame.draw.circle(surface, BLACK, (self.x, int(self.y - 10 + bounce)), 20, 2)
            # Face
            pygame.draw.circle(surface, BLACK, (self.x - 5, int(self.y - 12 + bounce)), 3)
            pygame.draw.circle(surface, BLACK, (self.x + 5, int(self.y - 12 + bounce)), 3)
            
            # Countdown
            time_until_sun = 10 - (time.time() - self.last_sun)
            if time_until_sun > 0:
                timer = small_font.render(str(int(time_until_sun)), True, YELLOW_PENCIL)
                surface.blit(timer, (self.x - 5, int(self.y - 50 + bounce)))
        
        elif self.type == "peashooter":
            # Simple peashooter
            pygame.draw.circle(surface, GREEN_PENCIL, (self.x, int(self.y - 15 + bounce)), 25)
            pygame.draw.circle(surface, BLACK, (self.x, int(self.y - 15 + bounce)), 25, 2)
            # Eye
            pygame.draw.circle(surface, WHITE, (self.x + 5, int(self.y - 18 + bounce)), 6)
            pygame.draw.circle(surface, BLACK, (self.x + 7, int(self.y - 18 + bounce)), 3)
        
        elif self.type == "wallnut":
            # Simple wallnut
            pygame.draw.ellipse(surface, BROWN_PENCIL, (self.x - 20, int(self.y - 30 + bounce), 40, 60))
            pygame.draw.ellipse(surface, BLACK, (self.x - 20, int(self.y - 30 + bounce), 40, 60), 2)
            # Eyes
            pygame.draw.circle(surface, WHITE, (self.x - 8, int(self.y - 15 + bounce)), 6)
            pygame.draw.circle(surface, WHITE, (self.x + 8, int(self.y - 15 + bounce)), 6)
            pygame.draw.circle(surface, BLACK, (self.x - 8, int(self.y - 15 + bounce)), 3)
            pygame.draw.circle(surface, BLACK, (self.x + 8, int(self.y - 15 + bounce)), 3)
        
        # Health bar
        if self.hp < self.max_hp:
            bar_width = 50
            bar_height = 6
            hp_percent = max(0, self.hp / self.max_hp)
            y_pos = self.y - 50 + bounce
            
            pygame.draw.rect(surface, (200, 200, 200), (self.x - bar_width//2, y_pos, bar_width, bar_height))
            pygame.draw.rect(surface, BLACK, (self.x - bar_width//2, y_pos, bar_width, bar_height), 2)
            
            health_color = GREEN_PENCIL if hp_percent > 0.5 else (YELLOW_PENCIL if hp_percent > 0.25 else RED_PENCIL)
            pygame.draw.rect(surface, health_color, (self.x - bar_width//2 + 2, y_pos + 2, (bar_width - 4) * hp_percent, bar_height - 4))

class Zombie:
    def __init__(self, row, level=1):
        self.row = row
        self.x = SCREEN_WIDTH + 50
        self.y = GRID_OFFSET_Y + row * CELL_HEIGHT + CELL_HEIGHT // 2
        
        # Level-based difficulty
        self.level = level
        difficulty = LearningAI().get_level_difficulty(level)
        
        self.hp = int(120 * difficulty['zombie_hp'])
        self.max_hp = self.hp
        self.speed = 0.35 * difficulty['zombie_speed']
        self.damage = 1.5 * difficulty['zombie_damage']
        self.eating = False
        self.last_attack = time.time()
        self.attack_speed = 0.5
        self.walk_cycle = 0
        self.blink_timer = random.random() * 3
        self.dying = False
        self.death_timer = 0
        self.death_duration = 1.5
    
    def move(self):
        if not self.eating and not self.dying:
            self.x -= self.speed
            self.walk_cycle += 0.12
        
        if self.dying:
            self.death_timer += 0.016
    
    def draw(self, surface):
        if self.dying:
            progress = self.death_timer / self.death_duration
            if progress < 0.3:
                # Flash red
                alpha = int(200 * (1 - progress / 0.3))
                overlay = pygame.Surface((80, 120), pygame.SRCALPHA)
                overlay.fill((255, 0, 0, alpha))
                surface.blit(overlay, (self.x - 40, self.y - 60))
            elif progress < 0.6:
                # Mix with skeleton
                self._draw_body(surface)
                self._draw_skeleton(surface, int(255 * (progress - 0.3) / 0.3))
            else:
                # Pure skeleton fading
                alpha = int(255 * (1 - (progress - 0.6) / 0.4))
                if alpha > 0:
                    self._draw_skeleton(surface, alpha)
            return
        
        self._draw_body(surface)
    
    def _draw_body(self, surface):
        leg_swing = math.sin(self.walk_cycle) * 8
        
        # Simple body
        body_y = self.y - 45
        pygame.draw.rect(surface, (100, 120, 140), (self.x - 20, body_y, 40, 55))
        pygame.draw.rect(surface, BLACK, (self.x - 20, body_y, 40, 55), 2)
        
        # Head
        pygame.draw.circle(surface, (110, 140, 110), (self.x, int(body_y - 25)), 28)
        pygame.draw.circle(surface, BLACK, (self.x, int(body_y - 25)), 28, 2)
        
        # Eyes
        eye_y = int(body_y - 28)
        eye_bg = YELLOW_PENCIL if self.eating else WHITE
        pygame.draw.circle(surface, eye_bg, (self.x - 10, eye_y), 8)
        pygame.draw.circle(surface, eye_bg, (self.x + 10, eye_y), 8)
        pygame.draw.circle(surface, BLACK, (self.x - 8, eye_y), 4)
        pygame.draw.circle(surface, BLACK, (self.x + 12, eye_y), 4)
        
        # Health bar
        if self.hp < self.max_hp:
            bar_width = 50
            bar_height = 5
            hp_percent = max(0, self.hp / self.max_hp)
            bar_y = body_y - 60
            pygame.draw.rect(surface, (200, 200, 200), (self.x - bar_width//2, bar_y, bar_width, bar_height))
            pygame.draw.rect(surface, GREEN_PENCIL if hp_percent > 0.5 else RED_PENCIL, 
                          (self.x - bar_width//2 + 2, bar_y + 2, (bar_width - 4) * hp_percent, bar_height - 4))
    
    def _draw_skeleton(self, surface, alpha=255):
        # Simple skeleton
        skull_y = self.y - 75
        pygame.draw.circle(surface, (240, 230, 210), (self.x, skull_y), 25)
        pygame.draw.circle(surface, (80, 80, 80), (self.x, skull_y), 25, 2)
        pygame.draw.circle(surface, (30, 30, 30), (self.x - 8, skull_y - 5), 8)
        pygame.draw.circle(surface, (30, 30, 30), (self.x + 8, skull_y - 5), 8)

class Pea:
    def __init__(self, x, y, row):
        self.x = x
        self.y = y
        self.row = row
        self.speed = 8
        self.damage = 25
        self.active = True
    
    def move(self):
        self.x += self.speed
        if self.x > SCREEN_WIDTH:
            self.active = False
    
    def draw(self, surface):
        pygame.draw.circle(surface, GREEN_PENCIL, (int(self.x), int(self.y)), 10)
        pygame.draw.circle(surface, BLACK, (int(self.x), int(self.y)), 10, 2)

class Sun:
    def __init__(self, x, y, value=25, is_bright=False):
        self.x = x
        self.y = y
        self.value = value
        self.radius = 25
        self.active = True
        self.spawn_time = time.time()
        self.target_y = y if y > 50 else random.randint(120, SCREEN_HEIGHT - 100)
        self.is_bright = is_bright
    
    def update(self):
        if self.y < self.target_y:
            self.y += 1.5
        if time.time() - self.spawn_time > 12:
            self.active = False
    
    def draw(self, surface):
        color = (255, 255, 200) if self.is_bright else YELLOW_PENCIL
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, BLACK, (int(self.x), int(self.y)), self.radius, 2)
        pygame.draw.circle(surface, BLACK, (int(self.x - 8), int(self.y)), 4)
        pygame.draw.circle(surface, BLACK, (int(self.x + 8), int(self.y)), 4)

# ============================================
# MAIN GAME CLASS
# ============================================

class Game:
    def __init__(self):
        self.grid = [[None for _ in range(GRID_ROWS)] for _ in range(GRID_COLS)]
        self.plants = []
        self.zombies = []
        self.peas = []
        self.suns = []
        self.sun_count = 350  # Enough for immediate defense setup
        self.selected_plant = None
        self.game_over = False
        self.paused = False
        self.ai_mode = False
        self.auto_play = False  # Auto-play 5 games
        self.level = 1
        self.level = 1
        self.wave = 1
        self.current_level_waves = 0
        self.waves_per_level = 5
        self.current_level_waves = 0
        self.zombies_spawned = 0
        self.zombies_to_spawn = 3
        self.last_spawn = time.time()
        self.spawn_interval = 20  # Very slow to give AI time to build
        self.last_sun_spawn = time.time()
        
        # Learning AI
        self.learning_ai = LearningAI()
        self.learning_ai.load()
        
        # AI logging
        self.ai_logs = []
        self.max_logs = 10
        self.last_ai_action = time.time()
        self.ai_action_interval = 0.5
        
        # Auto-play state
        self.auto_play_count = 0
        self.auto_play_results = []
        self.game_speed = 1  # Speed multiplier (1, 2, 4, 8)
        
        # Pre-generate grass
        self.grass_textures = []
        for col in range(GRID_COLS):
            for row in range(GRID_ROWS):
                color_idx = (col + row) % 3
                bg_color = [GRASS_1, GRASS_2, GRASS_3][color_idx]
                grass_surf = pygame.Surface((CELL_WIDTH - 2, CELL_HEIGHT - 2))
                grass_surf.fill(bg_color)
                self.grass_textures.append(grass_surf)
    
    def ai_log(self, message):
        self.ai_logs.append(message)
        if len(self.ai_logs) > self.max_logs:
            self.ai_logs.pop(0)
        print(message)
    
    def auto_play_ai_decide(self):
        """AI makes decisions during auto-play"""
        if self.game_over or self.paused:
            return
        
        current_time = time.time()
        if current_time - self.last_ai_action < self.ai_action_interval:
            return
        
        self.last_ai_action = current_time
        
        # Get game state for AI
        game_state = {
            'wave': self.wave,
            'sun': self.sun_count,
            'zombies': self.zombies,
            'grid': self.grid,
            'plants': self.plants,
            'suns': self.suns
        }
        
        # Add level to game state
        game_state['level'] = self.level
        
        # Get decision from learning AI
        decision = self.learning_ai.decide(game_state)
        
        # Execute decision
        if decision == "collect_sun":
            for sun in self.suns[:]:
                if sun.active:
                    self.sun_count += sun.value
                    self.suns.remove(sun)
                    self.ai_log(f"Collected sun (+{sun.value}) = {self.sun_count}")
                    return
        elif decision.startswith("place_"):
            parts = decision.split('_')
            plant_type = parts[1]
            col = int(parts[2])
            row = int(parts[3])
            
            if self.grid[col][row] is None:
                plant = Plant(col, row, plant_type)
                self.plants.append(plant)
                self.grid[col][row] = plant
                
                costs = {"sunflower": 50, "peashooter": 100, "wallnut": 50}
                self.sun_count -= costs[plant_type]
                self.ai_log(f"Placed {plant_type} at ({col},{row})")
                return
        
        self.ai_log(f"Waiting | L{self.level}-{self.wave} | Sun {self.sun_count}")
    
    def update(self):
        if self.game_over or self.paused:
            return
        
        current_time = time.time()
        
        # Auto-play mode
        if self.auto_play or self.ai_mode:
            self.auto_play_ai_decide()
        
        # Spawn zombies
        if current_time - self.last_spawn > self.spawn_interval:
            if self.zombies_spawned < self.zombies_to_spawn:
                row = random.randint(0, GRID_ROWS - 1)
                self.zombies.append(Zombie(row, self.level))
                self.zombies_spawned += 1
            self.last_spawn = current_time
        
        # Wave completion
        if self.zombies_spawned >= self.zombies_to_spawn:
            alive_zombies = [z for z in self.zombies if not z.dying]
            if len(alive_zombies) == 0:
                self.wave += 1
                self.zombies_spawned = 0
                self.zombies_to_spawn = 3 + self.wave
                self.spawn_interval = max(3, 8 - self.wave * 0.5)
        
        # Natural sun
        if current_time - self.last_sun_spawn > 10:
            x = random.randint(GRID_OFFSET_X, GRID_OFFSET_X + GRID_COLS * CELL_WIDTH - 50)
            self.suns.append(Sun(x, -30))
            self.last_sun_spawn = current_time
        
        # Update plants
        for plant in self.plants[:]:
            if plant.type == "sunflower":
                if current_time - plant.last_sun > 10:
                    self.suns.append(Sun(plant.x, plant.y - 30, is_bright=True))
                    plant.last_sun = current_time
            elif plant.type == "peashooter":
                has_zombie = any(z.row == plant.row and z.x > plant.x for z in self.zombies if not z.dying)
                if has_zombie and current_time - plant.last_shot > 1.5:
                    self.peas.append(Pea(plant.x + 20, plant.y - 15, plant.row))
                    plant.last_shot = current_time
            
            if plant.hp <= 0:
                self.plants.remove(plant)
                self.grid[plant.col][plant.row] = None
        
        # Update zombies
        for zombie in self.zombies[:]:
            if zombie.dying:
                zombie.move()
                if zombie.death_timer >= zombie.death_duration:
                    self.zombies.remove(zombie)
                continue
            
            zombie.eating = False
            for plant in self.plants:
                if plant.row == zombie.row and abs(zombie.x - plant.x) < 30:
                    zombie.eating = True
                    if current_time - zombie.last_attack > zombie.attack_speed:
                        plant.hp -= zombie.damage
                        zombie.last_attack = current_time
                    break
            
            zombie.move()
            
            if zombie.hp <= 0:
                zombie.dying = True
                continue
            
            if zombie.x < GRID_OFFSET_X - 20:
                self.game_over = True
                if self.auto_play:
                    self._handle_game_over()
        
        # Update peas
        for pea in self.peas[:]:
            pea.move()
            for zombie in self.zombies:
                if zombie.row == pea.row and abs(zombie.x - pea.x) < 25:
                    zombie.hp -= pea.damage
                    pea.active = False
                    break
            if not pea.active:
                self.peas.remove(pea)
        
        # Update suns
        for sun in self.suns[:]:
            sun.update()
            if not sun.active:
                self.suns.remove(sun)
    
    def _handle_game_over(self):
        """Handle game over in auto-play mode"""
        # Calculate total waves completed
        total_waves = (self.level - 1) * self.waves_per_level + self.current_level_waves
        if self.current_level_waves == 0 and self.level > 1:
            total_waves = (self.level - 2) * self.waves_per_level + self.waves_per_level
        
        level_reached = self.level
        wave_reached = self.current_level_waves
        
        self.auto_play_results.append({
            'level': level_reached,
            'wave': wave_reached,
            'total_waves': total_waves
        })
        self.auto_play_count += 1
        
        # Learn from this game
        self.learning_ai.learn_from_game(level_reached, wave_reached)
        
        # Save learning data
        self.learning_ai.save()
        
        self.ai_log(f"Game {self.auto_play_count}/5: Level {level_reached}-{wave_reached} | Best: Level {self.learning_ai.best_level}")
        
        # Check if auto-play complete
        if self.auto_play_count >= 5:
            self.ai_log("=" * 50)
            self.ai_log(f"Auto-play complete! Results:")
            for i, r in enumerate(self.auto_play_results, 1):
                if isinstance(r, dict):
                    self.ai_log(f"  Game {i}: Level {r['level']}-{r['wave']} ({r['total_waves']} total waves)")
                else:
                    self.ai_log(f"  Game {i}: Wave {r}")
            # Calculate average
            if all(isinstance(r, dict) for r in self.auto_play_results):
                avg_waves = sum(r['total_waves'] for r in self.auto_play_results) / len(self.auto_play_results)
                best_level = max(r['level'] for r in self.auto_play_results)
                self.ai_log(f"Average: {avg_waves:.1f} total waves")
                self.ai_log(f"Best: Level {best_level}")
            else:
                self.ai_log(f"Results: {self.auto_play_results}")
            self.ai_log("=" * 50)
            self.auto_play = False
        else:
            # Reset for next game
            time.sleep(1)  # Brief pause
            self._reset_game()
    
    def _reset_game(self):
        """Reset game state for next game"""
        self.grid = [[None for _ in range(GRID_ROWS)] for _ in range(GRID_COLS)]
        self.plants = []
        self.zombies = []
        self.peas = []
        self.suns = []
        self.sun_count = 350  # Enough for immediate defense setup
        self.game_over = False
        self.level = 1
        self.wave = 1
        self.waves_per_level = 5
        self.current_level_waves = 0
        self.zombies_spawned = 0
        self.zombies_to_spawn = 3
        self.last_spawn = time.time()
        self.spawn_interval = 20  # Very slow to give AI time to build
        self.last_sun_spawn = time.time()
        # Don't clear ai_logs, keep them for visibility
    
    def draw(self):
        screen.fill(PAPER_COLOR)
        
        # Draw grid
        texture_idx = 0
        for col in range(GRID_COLS):
            for row in range(GRID_ROWS):
                x = GRID_OFFSET_X + col * CELL_WIDTH
                y = GRID_OFFSET_Y + row * CELL_HEIGHT
                screen.blit(self.grass_textures[texture_idx], (x, y))
                texture_idx += 1
        
        # Draw entities
        for plant in self.plants:
            plant.draw(screen)
        
        for zombie in self.zombies:
            zombie.draw(screen)
        
        for pea in self.peas:
            pea.draw(screen)
        
        for sun in self.suns:
            sun.draw(screen)
        
        # Draw UI
        self._draw_ui()
        
        # Game over
        if self.game_over and not self.auto_play:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0, 0))
            
            game_over_text = title_font.render("GAME OVER", True, RED_PENCIL)
            wave_text = font.render(f"You survived {self.wave} waves", True, WHITE)
            restart_text = font.render("Press [R] to restart or [A] for auto-play", True, YELLOW_PENCIL)
            
            screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 60))
            screen.blit(wave_text, (SCREEN_WIDTH//2 - wave_text.get_width()//2, SCREEN_HEIGHT//2))
            screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 50))
        
        # Auto-play info
        if self.auto_play:
            info = font.render(f"Auto-Play: Game {self.auto_play_count}/5", True, (0, 150, 0))
            screen.blit(info, (SCREEN_WIDTH//2 - info.get_width()//2, 10))
    
    def _draw_ui(self):
        # Top bar
        pygame.draw.rect(screen, PAPER_COLOR, (0, 0, SCREEN_WIDTH, TOP_BAR_HEIGHT))
        pygame.draw.line(screen, BLACK, (0, TOP_BAR_HEIGHT), (SCREEN_WIDTH, TOP_BAR_HEIGHT), 3)
        
        # Sun counter
        sun_x = SIDEBAR_WIDTH + 15
        pygame.draw.circle(screen, YELLOW_PENCIL, (sun_x + 12, 18), 7)
        pygame.draw.circle(screen, BLACK, (sun_x + 12, 18), 7, 2)
        sun_text = font.render(f"{self.sun_count}", True, BLACK)
        screen.blit(sun_text, (sun_x + 30, 8))
        
        # Wave with progress
        wave_x = sun_x + 80
        level_text = small_font.render(f"L{self.level}-{self.wave}", True, BLACK)
        screen.blit(level_text, (wave_x, 12))
        
        progress_y = 32
        progress_width = 100
        pygame.draw.rect(screen, (230, 230, 230), (wave_x, progress_y, progress_width, 14))
        pygame.draw.rect(screen, BLACK, (wave_x, progress_y, progress_width, 14), 2)
        
        zombies_killed = self.zombies_spawned - len([z for z in self.zombies if not z.dying])
        progress_percent = zombies_killed / self.zombies_to_spawn if self.zombies_to_spawn > 0 else 0
        pygame.draw.rect(screen, GREEN_PENCIL, (wave_x + 2, progress_y + 2, (progress_width - 4) * progress_percent, 10))
        
        remaining_text = small_font.render(f"{zombies_killed}/{self.zombies_to_spawn}", True, BLACK)
        screen.blit(remaining_text, (wave_x + progress_width//2 - remaining_text.get_width()//2, progress_y - 1))
        
        # AI Info
        ai_info_x = wave_x + 120
        gen_text = small_font.render(f"Gen: {self.learning_ai.generation}", True, BLACK)
        best_text = small_font.render(f"Best: L{self.learning_ai.best_level}", True, (0, 150, 0))
        games_text = small_font.render(f"Games: {self.learning_ai.games_played}", True, BLACK)
        screen.blit(gen_text, (ai_info_x, 8))
        screen.blit(best_text, (ai_info_x, 28))
        screen.blit(games_text, (ai_info_x, 48))
        
        # Plant cards (mini version in top bar, visible during AI mode)
        plant_cards_start_x = ai_info_x + 100
        card_width = 70
        card_height = 60
        card_spacing = 10
        plant_types = [
            ("Sunflower", YELLOW_PENCIL, 50),
            ("Peashooter", GREEN_PENCIL, 100),
            ("Wallnut", BROWN_PENCIL, 50)
        ]
        
        for i, (name, color, cost) in enumerate(plant_types):
            card_x = plant_cards_start_x + i * (card_width + card_spacing)
            card_y = 10
            
            # Card background
            can_afford = self.sun_count >= cost
            bg_color = (255, 255, 250) if can_afford else (240, 240, 240)
            pygame.draw.rect(screen, bg_color, (card_x, card_y, card_width, card_height), border_radius=4)
            pygame.draw.rect(screen, (180, 180, 180) if can_afford else (150, 150, 150), 
                           (card_x, card_y, card_width, card_height), 2, border_radius=4)
            
            # Plant icon
            icon_y = card_y + 20
            pygame.draw.circle(screen, color, (card_x + card_width//2, icon_y), 15)
            pygame.draw.circle(screen, BLACK, (card_x + card_width//2, icon_y), 15, 2)
            
            # Name (abbreviated)
            name_surf = small_font.render(name[:4], True, BLACK)
            screen.blit(name_surf, (card_x + card_width//2 - name_surf.get_width()//2, card_y + 5))
            
            # Cost
            cost_surf = small_font.render(str(cost), True, (180, 140, 50) if can_afford else GRAY_PENCIL)
            screen.blit(cost_surf, (card_x + card_width//2 - cost_surf.get_width()//2, card_y + 45))
            
            # Plant count
            if name == "Sunflower":
                count = sum(1 for p in self.plants if p.type == "sunflower")
            elif name == "Peashooter":
                count = sum(1 for p in self.plants if p.type == "peashooter")
            else:
                count = sum(1 for p in self.plants if p.type == "wallnut")
            
            count_surf = small_font.render(f"x{count}", True, BLACK)
            screen.blit(count_surf, (card_x + card_width - count_surf.get_width() - 5, card_y + card_height - 12))
        
        # Auto-play button
        if not self.auto_play:
            button_x = SCREEN_WIDTH - 240
            button_y = 8
            pygame.draw.rect(screen, (200, 255, 200), (button_x, button_y, 110, 28), border_radius=5)
            pygame.draw.rect(screen, (0, 150, 0), (button_x, button_y, 110, 28), 2, border_radius=5)
            button_text = small_font.render("Auto-Play x5", True, (0, 100, 0))
            screen.blit(button_text, (button_x + 55 - button_text.get_width()//2, button_y + 5))
            self.autoplay_button_rect = pygame.Rect(button_x, button_y, 110, 28)
        
        # Speed control buttons (always visible, even in AI mode)
        speed_x = SCREEN_WIDTH - 120
        speed_y = 8
        
        # Speed down button
        pygame.draw.rect(screen, (255, 255, 255), (speed_x, speed_y, 25, 28), border_radius=3)
        pygame.draw.rect(screen, BLACK, (speed_x, speed_y, 25, 28), 2, border_radius=3)
        minus_text = small_font.render("-", True, BLACK)
        screen.blit(minus_text, (speed_x + 8, speed_y + 5))
        self.speed_down_rect = pygame.Rect(speed_x, speed_y, 25, 28)
        
        # Speed display
        speed_text = font.render(f"{self.game_speed}x", True, BLACK)
        screen.blit(speed_text, (speed_x + 30, speed_y + 5))
        
        # Speed up button
        pygame.draw.rect(screen, (255, 255, 255), (speed_x + 70, speed_y, 25, 28), border_radius=3)
        pygame.draw.rect(screen, BLACK, (speed_x + 70, speed_y, 25, 28), 2, border_radius=3)
        plus_text = small_font.render("+", True, BLACK)
        screen.blit(plus_text, (speed_x + 78, speed_y + 5))
        self.speed_up_rect = pygame.Rect(speed_x + 70, speed_y, 25, 28)
        
        # AI Log (bottom right)
        if self.ai_logs:
            log_width = 400
            log_height = 200
            log_x = SCREEN_WIDTH - log_width - 10
            log_y = SCREEN_HEIGHT - log_height - 10
            
            pygame.draw.rect(screen, (250, 250, 245), (log_x, log_y, log_width, log_height), border_radius=5)
            pygame.draw.rect(screen, BLACK, (log_x, log_y, log_width, log_height), 2, border_radius=5)
            
            title = small_font.render("AI Log:", True, BLACK)
            screen.blit(title, (log_x + 10, log_y + 8))
            
            for i, log in enumerate(self.ai_logs[-10:]):
                log_text = small_font.render(log, True, (50, 50, 50))
                screen.blit(log_text, (log_x + 10, log_y + 30 + i * 16))

def main():
    game = Game()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # Speed controls (always available)
                    if hasattr(game, 'speed_down_rect') and game.speed_down_rect.collidepoint(event.pos):
                        # Speed down: 8→4→2→1
                        old_speed = game.game_speed
                        if game.game_speed == 2:
                            game.game_speed = 1
                        elif game.game_speed == 4:
                            game.game_speed = 2
                        elif game.game_speed == 8:
                            game.game_speed = 4
                        if old_speed != game.game_speed:
                            game.ai_log(f"Speed: {old_speed}x -> {game.game_speed}x")
                    elif hasattr(game, 'speed_up_rect') and game.speed_up_rect.collidepoint(event.pos):
                        # Speed up: 1→2→4→8 (same as keyboard)
                        old_speed = game.game_speed
                        if game.game_speed == 1:
                            game.game_speed = 2
                        elif game.game_speed == 2:
                            game.game_speed = 4
                        elif game.game_speed == 4:
                            game.game_speed = 8
                        if old_speed != game.game_speed:
                            game.ai_log(f"Speed: {old_speed}x -> {game.game_speed}x")
                    # Auto-play button (only when not playing)
                    elif not game.auto_play and hasattr(game, 'autoplay_button_rect') and game.autoplay_button_rect.collidepoint(event.pos):
                        game.auto_play = True
                        game.auto_play_count = 0
                        game.auto_play_results = []
                        game._reset_game()
                        game.ai_log("Starting auto-play x5...")
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game = Game()
                elif event.key == pygame.K_a:
                    game.ai_mode = not game.ai_mode
                    game.ai_log(f"AI Mode: {'ON' if game.ai_mode else 'OFF'}")
                elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS or event.key == pygame.K_UP:  # Speed up
                    old_speed = game.game_speed
                    if game.game_speed == 1:
                        game.game_speed = 2
                    elif game.game_speed == 2:
                        game.game_speed = 4
                    elif game.game_speed == 4:
                        game.game_speed = 8
                    game.ai_log(f"Speed: {old_speed}x -> {game.game_speed}x")
                elif event.key == pygame.K_MINUS or event.key == pygame.K_DOWN:  # Speed down
                    old_speed = game.game_speed
                    if game.game_speed == 8:
                        game.game_speed = 4
                    elif game.game_speed == 4:
                        game.game_speed = 2
                    elif game.game_speed == 2:
                        game.game_speed = 1
                    game.ai_log(f"Speed: {old_speed}x -> {game.game_speed}x")
                elif event.key == pygame.K_ESCAPE:
                    if game.ai_mode or game.auto_play:
                        game.ai_mode = False
                        game.auto_play = False
                        game.ai_log("Stopped AI/Auto-play")
        
        game.update()
        game.draw()
        pygame.display.flip()
        
        # Speed control: update multiple times per frame for higher speeds
        game.update()
        game.draw()
        pygame.display.flip()
        
        # At higher speeds, update multiple times per frame
        if game.game_speed > 1:
            for _ in range(game.game_speed - 1):
                game.update()
        
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()
