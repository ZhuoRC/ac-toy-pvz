#!/usr/bin/env python3
"""
Plants vs Zombies - Doodle Style
Left sidebar: plants only
Top bar: all other info (sun, wave, settings)
"""

import pygame
import random
import time
import math

# Initialize
pygame.init()

# Constants
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
GRID_COLS = 15
GRID_ROWS = 5
CELL_WIDTH = 120
CELL_HEIGHT = 120
GRID_OFFSET_X = 140  # Reduced sidebar width
GRID_OFFSET_Y = 100   # Top bar height
TOP_BAR_HEIGHT = 75
SIDEBAR_WIDTH = 130

# Doodle Color Palette
BLACK = (20, 20, 20)
WHITE = (250, 248, 240)
PAPER_COLOR = (255, 253, 245)
GREEN_PENCIL = (46, 139, 87)
LIGHT_GREEN = (124, 200, 100)
YELLOW_PENCIL = (255, 220, 50)
ORANGE_PENCIL = (255, 165, 50)
BROWN_PENCIL = (160, 120, 70)
RED_PENCIL = (220, 60, 60)
BLUE_PENCIL = (100, 150, 220)
GRAY_PENCIL = (150, 150, 150)
GRASS_1 = (180, 220, 120)
GRASS_2 = (160, 200, 100)
GRASS_3 = (140, 180, 80)

# Setup screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("PVZ - Doodle Edition")
clock = pygame.time.Clock()

font = pygame.font.Font(None, 36)
title_font = pygame.font.Font(None, 54)
small_font = pygame.font.Font(None, 28)

def draw_thick_line(surface, color, start, end, width=3):
    """Draw a doodle-style thick line"""
    pygame.draw.line(surface, color, start, end, width)
    if width > 2:
        offset_x = random.randint(-1, 1)
        offset_y = random.randint(-1, 1)
        pygame.draw.line(surface, color, 
                        (start[0] + offset_x, start[1] + offset_y),
                        (end[0] + offset_x, end[1] + offset_y), 1)

def draw_doodle_circle(surface, color, center, radius, filled=False, outline=3):
    """Draw a hand-drawn style circle"""
    if filled:
        pygame.draw.circle(surface, color, center, radius)
        pygame.draw.circle(surface, BLACK, center, radius, 2)
    else:
        # Only draw once without random offset
        pygame.draw.circle(surface, color, center, radius, outline)

def draw_doodle_rect(surface, color, rect, filled=False, outline=3):
    """Draw a hand-drawn style rectangle"""
    if filled:
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, BLACK, rect, 2)
    else:
        x, y, w, h = rect
        # Only draw once without random offset
        pygame.draw.rect(surface, color, (x, y, w, h), outline)

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
        elif plant_type == "repeater":
            self.hp = 150
            self.cost = 200
            self.last_shot = time.time()
        elif plant_type == "wallnut":
            self.hp = 400
            self.cost = 50
        
        self.max_hp = self.hp
        self.anim_offset = random.random() * math.pi * 2

    def draw(self, surface):
        bounce = math.sin(time.time() * 2 + self.anim_offset) * 3
        
        if self.type == "sunflower":
            # Stem
            stem_points = []
            for i in range(10):
                y_pos = self.y + i * 4
                x_offset = math.sin(i * 0.5 + time.time()) * 2
                stem_points.append((self.x + x_offset, y_pos))
            pygame.draw.lines(surface, GREEN_PENCIL, False, stem_points, 4)
            
            # Leaves
            pygame.draw.ellipse(surface, GREEN_PENCIL, 
                              (self.x - 30, self.y + 15, 25, 12))
            pygame.draw.ellipse(surface, BLACK, 
                              (self.x - 30, self.y + 15, 25, 12), 2)
            pygame.draw.ellipse(surface, GREEN_PENCIL, 
                              (self.x + 5, self.y + 20, 25, 12))
            pygame.draw.ellipse(surface, BLACK, 
                              (self.x + 5, self.y + 20, 25, 12), 2)
            
            # Petals
            petal_y = self.y - 15 + bounce
            for i in range(12):
                angle = (i * 30 + time.time() * 15) * math.pi / 180
                petal_length = 30 + math.sin(time.time() * 3 + i) * 3
                px = self.x + math.cos(angle) * petal_length
                py = petal_y + math.sin(angle) * petal_length
                
                pygame.draw.line(surface, YELLOW_PENCIL, 
                                (self.x, petal_y), (px, py), 5)
                pygame.draw.circle(surface, BLACK, (int(px), int(py)), 6)
                pygame.draw.circle(surface, YELLOW_PENCIL, (int(px), int(py)), 5)
            
            # Face
            face_y = int(petal_y)
            draw_doodle_circle(surface, ORANGE_PENCIL, (self.x, face_y), 18, True)
            
            pygame.draw.circle(surface, BLACK, (self.x - 6, face_y - 3), 4)
            pygame.draw.circle(surface, BLACK, (self.x + 6, face_y - 3), 4)
            pygame.draw.circle(surface, WHITE, (self.x - 5, face_y - 4), 2)
            pygame.draw.circle(surface, WHITE, (self.x + 7, face_y - 4), 2)
            
            smile_points = []
            for i in range(5):
                sx = self.x - 8 + i * 4
                sy = face_y + 6 + math.sin(i) * 2
                smile_points.append((sx, sy))
            pygame.draw.lines(surface, BLACK, False, smile_points, 2)
            
            # Countdown timer for sun production
            time_until_sun = 15 - (time.time() - self.last_sun)
            if time_until_sun > 0:
                timer_text = small_font.render(f"{int(time_until_sun)}", True, YELLOW_PENCIL)
                # Draw timer above sunflower with black outline for visibility
                timer_y = self.y - 55 + bounce
                timer_x = self.x - timer_text.get_width() // 2
                
                # Black outline
                outline_offsets = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
                for ox, oy in outline_offsets:
                    outline_surf = small_font.render(f"{int(time_until_sun)}", True, BLACK)
                    surface.blit(outline_surf, (timer_x + ox, timer_y + oy))
                
                # Main timer
                surface.blit(timer_text, (timer_x, timer_y))
        
        elif self.type == "peashooter":
            # Stem
            stem_points = []
            for i in range(12):
                y_pos = self.y + i * 3.5
                x_offset = math.sin(i * 0.4 + time.time() * 0.5) * 2
                stem_points.append((self.x + x_offset, y_pos))
            pygame.draw.lines(surface, GREEN_PENCIL, False, stem_points, 5)
            
            # Leaves
            leaf_y = self.y + 10
            pygame.draw.ellipse(surface, GREEN_PENCIL, 
                              (self.x - 40, leaf_y, 30, 15))
            pygame.draw.ellipse(surface, BLACK, 
                              (self.x - 40, leaf_y, 30, 15), 2)
            pygame.draw.ellipse(surface, GREEN_PENCIL, 
                              (self.x + 10, leaf_y + 5, 30, 15))
            pygame.draw.ellipse(surface, BLACK, 
                              (self.x + 10, leaf_y + 5, 30, 15), 2)
            
            # Head
            head_y = self.y - 20 + bounce
            draw_doodle_circle(surface, GREEN_PENCIL, (self.x, int(head_y)), 28, True)
            
            # Snout
            snout_x = self.x + 15
            snout_y = int(head_y - 5)
            pygame.draw.ellipse(surface, GREEN_PENCIL, 
                              (snout_x, snout_y - 12, 35, 24))
            pygame.draw.ellipse(surface, BLACK, 
                              (snout_x, snout_y - 12, 35, 24), 2)
            
            # Eye
            eye_x = self.x + 8
            eye_y = int(head_y - 8)
            pygame.draw.circle(surface, WHITE, (eye_x, eye_y), 10)
            pygame.draw.circle(surface, BLACK, (eye_x, eye_y), 10, 2)
            pygame.draw.circle(surface, BLACK, (eye_x + 2, eye_y), 5)
            pygame.draw.circle(surface, WHITE, (eye_x + 3, eye_y - 2), 2)
            
            pygame.draw.line(surface, BLACK, 
                           (eye_x - 6, eye_y - 14),
                           (eye_x + 4, eye_y - 12), 2)
            
            pygame.draw.circle(surface, (255, 180, 180), (eye_x - 5, eye_y + 6), 5)
        
        elif self.type == "repeater":
            # Stem (thicker, angrier)
            stem_points = []
            for i in range(12):
                y_pos = self.y + i * 3.5
                x_offset = math.sin(i * 0.5 + time.time() * 0.5) * 2
                stem_points.append((self.x + x_offset, y_pos))
            pygame.draw.lines(surface, RED_PENCIL, False, stem_points, 6)
            
            # Leaves (sharper, reddish)
            leaf_y = self.y + 10
            pygame.draw.ellipse(surface, (200, 100, 50), 
                              (self.x - 40, leaf_y, 30, 15))
            pygame.draw.ellipse(surface, BLACK, 
                              (self.x - 40, leaf_y, 30, 15), 2)
            pygame.draw.ellipse(surface, (200, 100, 50), 
                              (self.x + 10, leaf_y + 5, 30, 15))
            pygame.draw.ellipse(surface, BLACK, 
                              (self.x + 10, leaf_y + 5, 30, 15), 2)
            
            # Head (larger, reddish-green)
            head_y = self.y - 20 + bounce
            draw_doodle_circle(surface, (150, 180, 100), (self.x, int(head_y)), 32, True)
            
            # Double snout (two heads!)
            snout_x = self.x + 12
            snout_y = int(head_y - 5)
            
            # Top snout
            pygame.draw.ellipse(surface, (150, 180, 100), 
                              (snout_x, snout_y - 18, 40, 26))
            pygame.draw.ellipse(surface, BLACK, 
                              (snout_x, snout_y - 18, 40, 26), 2)
            
            # Bottom snout (slightly offset)
            pygame.draw.ellipse(surface, (140, 170, 90), 
                              (snout_x + 5, snout_y + 2, 40, 26))
            pygame.draw.ellipse(surface, BLACK, 
                              (snout_x + 5, snout_y + 2, 40, 26), 2)
            
            # Angry eyes (two pairs!)
            for eye_offset in [-5, 8]:
                eye_x = self.x + 8 + eye_offset
                eye_y = int(head_y - 8)
                # Angry eyebrow (slanted)
                pygame.draw.line(surface, BLACK, 
                               (eye_x - 8, eye_y - 16),
                               (eye_x + 4, eye_y - 12), 3)
                # Eye
                pygame.draw.circle(surface, WHITE, (eye_x, eye_y), 9)
                pygame.draw.circle(surface, BLACK, (eye_x, eye_y), 9, 2)
                pygame.draw.circle(surface, RED_PENCIL, (eye_x + 1, eye_y), 6)
                pygame.draw.circle(surface, WHITE, (eye_x + 2, eye_y - 2), 2)
        
        elif self.type == "wallnut":
            nut_y = self.y + bounce
            
            # Body
            body_rect = (self.x - 25, nut_y - 35, 50, 70)
            pygame.draw.ellipse(surface, BROWN_PENCIL, body_rect)
            pygame.draw.ellipse(surface, BLACK, body_rect, 3)
            
            # Highlight
            pygame.draw.ellipse(surface, (200, 160, 100), 
                              (self.x - 18, nut_y - 45, 20, 20))
            
            # Cracks
            crack_points = [
                [(self.x - 5, nut_y - 25), (self.x + 3, nut_y - 15), (self.x - 2, nut_y - 5)],
                [(self.x + 8, nut_y - 20), (self.x + 12, nut_y - 8), (self.x + 6, nut_y + 5)]
            ]
            for crack in crack_points:
                pygame.draw.lines(surface, BLACK, False, crack, 2)
            
            # Face
            pygame.draw.circle(surface, WHITE, (self.x - 10, int(nut_y - 15)), 8)
            pygame.draw.circle(surface, BLACK, (self.x - 10, int(nut_y - 15)), 8, 2)
            pygame.draw.circle(surface, BLACK, (self.x - 9, int(nut_y - 15)), 4)
            
            pygame.draw.circle(surface, WHITE, (self.x + 10, int(nut_y - 15)), 8)
            pygame.draw.circle(surface, BLACK, (self.x + 10, int(nut_y - 15)), 8, 2)
            pygame.draw.circle(surface, BLACK, (self.x + 11, int(nut_y - 15)), 4)
            
            pygame.draw.line(surface, BLACK, 
                           (self.x - 18, nut_y - 25),
                           (self.x - 5, nut_y - 22), 2)
            pygame.draw.line(surface, BLACK, 
                           (self.x + 5, nut_y - 22),
                           (self.x + 18, nut_y - 25), 2)
            
            mouth_points = []
            for i in range(7):
                mx = self.x - 10 + i * 3.5
                my = nut_y + (3 if i == 0 or i == 6 else -2 + math.sin(i) * 2)
                mouth_points.append((mx, my))
            pygame.draw.lines(surface, BLACK, False, mouth_points, 2)
        
        # Health bar
        if self.hp < self.max_hp:
            bar_width = 55
            bar_height = 8
            hp_percent = max(0, self.hp / self.max_hp)
            y_pos = self.y - 55 + bounce
            
            pygame.draw.rect(surface, (200, 200, 200), 
                           (self.x - bar_width//2, y_pos, bar_width, bar_height))
            pygame.draw.rect(surface, BLACK, 
                           (self.x - bar_width//2, y_pos, bar_width, bar_height), 2)
            
            health_color = GREEN_PENCIL if hp_percent > 0.5 else (ORANGE_PENCIL if hp_percent > 0.25 else RED_PENCIL)
            pygame.draw.rect(surface, health_color, 
                           (self.x - bar_width//2 + 2, y_pos + 2, 
                            (bar_width - 4) * hp_percent, bar_height - 4))

class Zombie:
    def __init__(self, row, zombie_type="normal"):
        self.row = row
        self.zombie_type = zombie_type
        self.x = SCREEN_WIDTH + 50
        self.y = GRID_OFFSET_Y + row * CELL_HEIGHT + CELL_HEIGHT // 2
        
        if zombie_type == "cone":
            self.hp = 280  # Higher HP for conehead
            self.max_hp = 280
            self.speed = 0.35
        elif zombie_type == "football":
            self.hp = 600  # Very high HP for football zombie
            self.max_hp = 600
            self.speed = 0.6  # Moves faster
        else:
            self.hp = 120
            self.max_hp = 120
            self.speed = 0.35
        
        self.damage = 1.5
        self.eating = False
        self.last_attack = time.time()
        self.attack_speed = 0.5
        self.walk_cycle = 0
        self.blink_timer = random.random() * 3
        self.dying = False
        self.death_timer = 0
        self.death_duration = 1.5  # Death animation duration in seconds

    def move(self):
        if not self.eating and not self.dying:
            self.x -= self.speed
            self.walk_cycle += 0.12
        
        # Update death animation
        if self.dying:
            self.death_timer += 0.016

    def draw_skeleton(self, surface, x, y, alpha=255):
        """Draw a skeleton version of the zombie"""
        # Create a surface for alpha blending
        skeleton_surf = pygame.Surface((100, 120), pygame.SRCALPHA)
        
        # Skeleton color with alpha
        bone_color = (240, 230, 210, alpha)
        outline_color = (80, 80, 80, alpha)
        
        skull_y = 30
        
        # Skull - circle
        pygame.draw.circle(skeleton_surf, bone_color, (50, skull_y), 25)
        pygame.draw.circle(skeleton_surf, outline_color, (50, skull_y), 25, 2)
        
        # Eye sockets
        pygame.draw.circle(skeleton_surf, (30, 30, 30, alpha), (40, skull_y - 5), 8)
        pygame.draw.circle(skeleton_surf, (30, 30, 30, alpha), (60, skull_y - 5), 8)
        
        # Nose hole
        pygame.draw.polygon(skeleton_surf, (30, 30, 30, alpha), [
            (50, skull_y + 2),
            (45, skull_y + 12),
            (55, skull_y + 12)
        ])
        
        # Teeth - horizontal lines
        for i in range(5):
            tx = 35 + i * 8
            pygame.draw.line(skeleton_surf, outline_color, 
                           (tx, skull_y + 18), (tx + 4, skull_y + 18), 2)
        
        # Ribs - spine
        spine_y = skull_y + 30
        for i in range(5):
            rib_y = spine_y + i * 12
            # Left rib
            pygame.draw.arc(skeleton_surf, outline_color, 
                          (30, rib_y, 40, 8), 0, 3.14, 2)
            # Right rib
            pygame.draw.arc(skeleton_surf, outline_color, 
                          (30, rib_y, 40, 8), 3.14, 6.28, 2)
        
        # Spine line
        pygame.draw.line(skeleton_surf, outline_color, 
                        (50, skull_y + 25), (50, spine_y + 60), 2)
        
        # Pelvis
        pygame_draw_points = [
            (35, spine_y + 60),
            (65, spine_y + 60),
            (50, spine_y + 75)
        ]
        pygame.draw.polygon(skeleton_surf, bone_color, pygame_draw_points)
        pygame.draw.polygon(skeleton_surf, outline_color, pygame_draw_points, 2)
        
        # Arms - bones
        # Left arm
        pygame.draw.line(skeleton_surf, outline_color, 
                        (30, spine_y + 20), (10, spine_y + 50), 4)
        pygame.draw.circle(skeleton_surf, bone_color, (10, spine_y + 50), 6)
        pygame.draw.circle(skeleton_surf, outline_color, (10, spine_y + 50), 6, 1)
        # Right arm
        pygame.draw.line(skeleton_surf, outline_color, 
                        (70, spine_y + 20), (90, spine_y + 50), 4)
        pygame.draw.circle(skeleton_surf, bone_color, (90, spine_y + 50), 6)
        pygame.draw.circle(skeleton_surf, outline_color, (90, spine_y + 50), 6, 1)
        
        # Legs - bones
        # Left leg
        pygame.draw.line(skeleton_surf, outline_color, 
                        (40, spine_y + 70), (35, spine_y + 110), 4)
        pygame.draw.circle(skeleton_surf, bone_color, (35, spine_y + 110), 6)
        pygame.draw.circle(skeleton_surf, outline_color, (35, spine_y + 110), 6, 1)
        # Right leg
        pygame.draw.line(skeleton_surf, outline_color, 
                        (60, spine_y + 70), (65, spine_y + 110), 4)
        pygame.draw.circle(skeleton_surf, bone_color, (65, spine_y + 110), 6)
        pygame.draw.circle(skeleton_surf, outline_color, (65, spine_y + 110), 6, 1)
        
        # Blit to screen
        surface.blit(skeleton_surf, (x - 50, y - 40))

    def draw(self, surface):
        # If dying, show skeleton transformation
        if self.dying:
            progress = self.death_timer / self.death_duration
            
            if progress < 0.3:
                # Phase 1: Flash red
                flash_intensity = int(255 * (1 - progress / 0.3))
                flash_surf = pygame.Surface((80, 120), pygame.SRCALPHA)
                flash_surf.fill((255, 0, 0, flash_intensity))
                surface.blit(flash_surf, (self.x - 40, self.y - 60))
                # Still draw zombie
                self._draw_zombie_body(surface)
            elif progress < 0.6:
                # Phase 2: Fade to skeleton (mix zombie and skeleton)
                mix_progress = (progress - 0.3) / 0.3
                self._draw_zombie_body(surface)
                self.draw_skeleton(surface, self.x, self.y, int(255 * mix_progress))
            else:
                # Phase 3: Full skeleton fading out
                fade_alpha = int(255 * (1 - (progress - 0.6) / 0.4))
                if fade_alpha > 0:
                    self.draw_skeleton(surface, self.x, self.y, fade_alpha)
            return
        
        self._draw_zombie_body(surface)
    
    def _draw_zombie_body(self, surface):
        leg_swing = math.sin(self.walk_cycle) * 8
        arm_swing = math.sin(self.walk_cycle + math.pi) * 5
        
        # Legs
        leg_color = GRAY_PENCIL
        pygame.draw.line(surface, leg_color, 
                        (self.x - 8, self.y + 10),
                        (self.x - 8 - leg_swing, self.y + 40), 5)
        pygame.draw.line(surface, leg_color, 
                        (self.x + 8, self.y + 10),
                        (self.x + 8 + leg_swing, self.y + 40), 5)
        
        pygame.draw.ellipse(surface, BLACK, 
                          (self.x - 18 - leg_swing, self.y + 38, 20, 10), 2)
        pygame.draw.ellipse(surface, BLACK, 
                          (self.x - 2 + leg_swing, self.y + 38, 20, 10), 2)
        
        # Body
        body_y = self.y - 45
        pygame.draw.rect(surface, (100, 120, 140), 
                        (self.x - 20, body_y, 40, 55))
        pygame.draw.rect(surface, BLACK, 
                        (self.x - 20, body_y, 40, 55), 2)
        
        # Tie
        tie_points = [
            (self.x, body_y + 5),
            (self.x - 6, body_y + 25),
            (self.x, body_y + 30),
            (self.x + 6, body_y + 25)
        ]
        pygame.draw.polygon(surface, RED_PENCIL, tie_points)
        pygame.draw.polygon(surface, BLACK, tie_points, 2)
        
        # Arms
        arm_y = body_y + 15
        left_arm_y = arm_y + (20 if self.eating else arm_swing)
        pygame.draw.line(surface, (100, 130, 100), 
                        (self.x - 20, arm_y),
                        (self.x - 35, left_arm_y), 6)
        pygame.draw.circle(surface, BLACK, (int(self.x - 35), int(left_arm_y)), 10)
        pygame.draw.circle(surface, (100, 130, 100), (int(self.x - 35), int(left_arm_y)), 9)
        
        right_arm_y = arm_y + (20 if self.eating else arm_swing)
        pygame.draw.line(surface, (100, 130, 100), 
                        (self.x + 20, arm_y),
                        (self.x + 35, right_arm_y), 6)
        pygame.draw.circle(surface, BLACK, (int(self.x + 35), int(right_arm_y)), 10)
        pygame.draw.circle(surface, (100, 130, 100), (int(self.x + 35), int(right_arm_y)), 9)
        
        # Head
        head_y = body_y - 25
        draw_doodle_circle(surface, (110, 140, 110), (self.x, int(head_y)), 28, True)
        
        # Hair
        for i in range(5):
            hx = self.x - 15 + i * 8
            hy = head_y - 35
            pygame.draw.circle(surface, (60, 40, 20), (hx, hy), 6)
            pygame.draw.circle(surface, BLACK, (hx, hy), 6, 1)
        
        # Cone hat for conehead zombies
        if self.zombie_type == "cone":
            cone_base_y = head_y + 5
            cone_tip_y = head_y - 50
            
            # Orange cone
            cone_points = [
                (self.x - 25, cone_base_y),
                (self.x + 25, cone_base_y),
                (self.x, cone_tip_y)
            ]
            pygame.draw.polygon(surface, (255, 140, 50), cone_points)
            pygame.draw.polygon(surface, BLACK, cone_points, 3)
            
            # Cone stripes (white reflective stripes)
            stripe_y1 = cone_base_y - 12
            stripe_y2 = cone_base_y - 24
            pygame.draw.line(surface, WHITE, 
                           (self.x - 20, stripe_y1),
                           (self.x + 20, stripe_y1), 4)
            pygame.draw.line(surface, WHITE, 
                           (self.x - 15, stripe_y2),
                           (self.x + 15, stripe_y2), 3)
        
        # Football helmet for football zombies
        if self.zombie_type == "football":
            # Helmet base
            helmet_color = (80, 40, 40)  # Dark brown/maroon
            pygame.draw.ellipse(surface, helmet_color, 
                              (self.x - 32, head_y - 40, 64, 60))
            pygame.draw.ellipse(surface, BLACK, 
                              (self.x - 32, head_y - 40, 64, 60), 3)
            
            # Face mask (grid pattern)
            mask_y = head_y + 5
            pygame.draw.line(surface, WHITE, 
                           (self.x - 15, mask_y),
                           (self.x - 15, mask_y + 25), 2)
            pygame.draw.line(surface, WHITE, 
                           (self.x + 15, mask_y),
                           (self.x + 15, mask_y + 25), 2)
            pygame.draw.line(surface, WHITE, 
                           (self.x - 15, mask_y),
                           (self.x + 15, mask_y + 25), 2)
            pygame.draw.line(surface, WHITE, 
                           (self.x + 15, mask_y),
                           (self.x - 15, mask_y + 25), 2)
            
            # Helmet stripe (center stripe like American football)
            pygame.draw.ellipse(surface, WHITE, 
                              (self.x - 3, head_y - 38, 6, 55))
            
            # Chin strap
            pygame.draw.line(surface, BLACK, 
                           (self.x - 20, mask_y + 20),
                           (self.x + 20, mask_y + 20), 3)
            
            # Eye black (football player eye paint)
            eye_y = int(head_y - 3)
            pygame.draw.ellipse(surface, BLACK, 
                              (self.x - 12, eye_y - 8, 10, 12))
            pygame.draw.ellipse(surface, BLACK, 
                              (self.x + 2, eye_y - 8, 10, 12))
        
        # Eyes
        eye_y = int(head_y - 3)
        
        self.blink_timer -= 0.016
        if self.blink_timer <= 0:
            self.blink_timer = random.random() * 4 + 2
        
        is_blinking = self.blink_timer < 0.15
        
        eye_bg = YELLOW_PENCIL if self.eating else WHITE
        eye_pupil = RED_PENCIL if self.eating else BLACK
        
        # Left eye
        if is_blinking:
            pygame.draw.line(surface, BLACK, (self.x - 15, eye_y), (self.x - 5, eye_y), 3)
        else:
            pygame.draw.circle(surface, eye_bg, (self.x - 10, eye_y), 10)
            pygame.draw.circle(surface, BLACK, (self.x - 10, eye_y), 10, 2)
            pygame.draw.circle(surface, eye_pupil, (self.x - 8, eye_y), 5)
            pygame.draw.circle(surface, WHITE, (self.x - 7, eye_y - 2), 2)
        
        # Right eye
        if is_blinking:
            pygame.draw.line(surface, BLACK, (self.x + 5, eye_y), (self.x + 15, eye_y), 3)
        else:
            pygame.draw.circle(surface, eye_bg, (self.x + 10, eye_y), 10)
            pygame.draw.circle(surface, BLACK, (self.x + 10, eye_y), 10, 2)
            pygame.draw.circle(surface, eye_pupil, (self.x + 12, eye_y), 5)
            pygame.draw.circle(surface, WHITE, (self.x + 13, eye_y - 2), 2)
        
        # Mouth
        mouth_y = int(head_y + 15)
        if self.eating:
            pygame.draw.ellipse(surface, (40, 20, 20), 
                              (self.x - 12, mouth_y - 5, 24, 18))
            for i in range(4):
                tx = self.x - 8 + i * 5
                pygame.draw.line(surface, WHITE, (tx, mouth_y), (tx + 2, mouth_y + 8), 2)
        else:
            pygame.draw.line(surface, BLACK, 
                           (self.x - 8, mouth_y + 3),
                           (self.x + 8, mouth_y + 3), 3)
        
        # Health bar
        bar_width = 50
        bar_height = 7
        hp_percent = max(0, self.hp / self.max_hp)
        bar_y = head_y - 45
        
        pygame.draw.rect(surface, (220, 220, 220), 
                        (self.x - bar_width//2, bar_y, bar_width, bar_height))
        pygame.draw.rect(surface, BLACK, 
                        (self.x - bar_width//2, bar_y, bar_width, bar_height), 2)
        
        health_color = GREEN_PENCIL if hp_percent > 0.5 else (ORANGE_PENCIL if hp_percent > 0.25 else RED_PENCIL)
        pygame.draw.rect(surface, health_color, 
                        (self.x - bar_width//2 + 2, bar_y + 2, 
                         (bar_width - 4) * hp_percent, bar_height - 4))

class Pea:
    def __init__(self, x, y, row):
        self.x = x
        self.y = y
        self.row = row
        self.speed = 8
        self.damage = 25
        self.active = True
        self.wobble = random.random() * math.pi * 2

    def move(self):
        self.x += self.speed
        if self.x > SCREEN_WIDTH:
            self.active = False

    def draw(self, surface):
        wobble_y = math.sin(time.time() * 10 + self.wobble) * 3
        
        # Trail
        for i in range(4):
            trail_x = self.x - i * 12
            trail_size = 14 - i * 2
            alpha = 180 - i * 40
            trail_surface = pygame.Surface((trail_size * 2, trail_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surface, (*LIGHT_GREEN, alpha), 
                             (trail_size, trail_size), trail_size)
            screen.blit(trail_surface, (trail_x - trail_size, self.y + wobble_y - trail_size))
        
        # Main pea
        pea_y = int(self.y + wobble_y)
        pygame.draw.circle(surface, GREEN_PENCIL, (self.x, pea_y), 12)
        pygame.draw.circle(surface, BLACK, (self.x, pea_y), 12, 2)
        
        pygame.draw.circle(surface, (180, 255, 180), 
                         (self.x - 3, pea_y - 3), 4)

class Sun:
    def __init__(self, x, y, value=25, is_bright=False):
        self.x = x
        self.y = y
        self.value = value
        self.radius = 28
        self.active = True
        self.spawn_time = time.time()
        self.target_y = y if y > 50 else random.randint(120, SCREEN_HEIGHT - 100)
        self.pulse_offset = random.random() * math.pi * 2
        self.rotation = 0
        self.is_bright = is_bright

    def update(self):
        if self.y < self.target_y:
            self.y += 1.5
        self.rotation += 2
        
        if time.time() - self.spawn_time > 12:
            self.active = False

    def draw(self, surface):
        pulse = math.sin(time.time() * 2.5 + self.pulse_offset) * 2
        
        # Color
        if self.is_bright:
            ray_color = (255, 255, 150)
            center_color = (255, 250, 150)
            glow_color = (255, 255, 200)
        else:
            ray_color = YELLOW_PENCIL
            center_color = YELLOW_PENCIL
            glow_color = (255, 245, 150)
        
        # Rays
        num_rays = 10
        for i in range(num_rays):
            angle = (i * (360 / num_rays) + self.rotation) * math.pi / 180
            ray_length = 40 + pulse + math.sin(i + time.time() * 2) * 5
            
            end_x = self.x + math.cos(angle) * ray_length
            end_y = self.y + math.sin(angle) * ray_length
            
            pygame.draw.line(surface, ray_color, 
                           (self.x, self.y), (end_x, end_y), 4)
            pygame.draw.line(surface, ray_color, 
                           (self.x, self.y), (end_x, end_y), 2)
        
        # Center
        center_radius = int(self.radius + pulse)
        pygame.draw.circle(surface, BLACK, (int(self.x), int(self.y)), center_radius, 3)
        pygame.draw.circle(surface, center_color, (int(self.x), int(self.y)), center_radius - 2)
        
        # Highlight
        highlight_radius = 10 if self.is_bright else 8
        highlight_color = (255, 255, 255) if self.is_bright else glow_color
        pygame.draw.circle(surface, highlight_color, 
                         (int(self.x - 8), int(self.y - 8)), highlight_radius)
        
        # Outer glow for bright suns
        if self.is_bright:
            glow_surface = pygame.Surface((80, 80), pygame.SRCALPHA)
            for i in range(3):
                alpha = 40 - i * 10
                size = 50 - i * 10
                pygame.draw.circle(glow_surface, (*center_color, alpha), (40, 40), size)
            surface.blit(glow_surface, (self.x - 40, self.y - 40))
        
        # Face
        face_y = int(self.y + 2)
        pygame.draw.circle(surface, BLACK, (int(self.x - 9), face_y), 4)
        pygame.draw.circle(surface, BLACK, (int(self.x + 9), face_y), 4)
        
        smile_points = [
            (self.x - 7, face_y + 10),
            (self.x - 3, face_y + 13),
            (self.x + 3, face_y + 13),
            (self.x + 7, face_y + 10)
        ]
        pygame.draw.lines(surface, BLACK, False, smile_points, 2)

class Game:
    def __init__(self):
        self.grid = [[None for _ in range(GRID_ROWS)] for _ in range(GRID_COLS)]
        self.plants = []
        self.zombies = []
        self.peas = []
        self.suns = []
        self.sun_count = 150
        self.selected_plant = None
        self.game_over = False
        self.paused = False
        self.ai_mode = False  # AI Mode toggle
        self.wave = 1
        self.zombies_spawned = 0
        self.zombies_to_spawn = 3
        self.last_spawn = time.time()
        self.spawn_interval = 12  # Slower initial spawn
        self.last_sun_spawn = time.time()
        self.last_ai_action = time.time()
        self.ai_action_interval = 0.5  # AI makes decisions every 0.5 seconds
        
        # AI logging system
        self.ai_logs = []
        self.max_logs = 8  # Keep last 8 actions on screen
        
        # Pre-generate grass textures to avoid constant refreshing
        self.grass_textures = []
        for col in range(GRID_COLS):
            for row in range(GRID_ROWS):
                color_idx = (col + row) % 3
                if color_idx == 0:
                    bg_color = GRASS_1
                elif color_idx == 1:
                    bg_color = GRASS_2
                else:
                    bg_color = GRASS_3
                
                # Create grass texture surface
                grass_surf = pygame.Surface((CELL_WIDTH - 2, CELL_HEIGHT - 2))
                grass_surf.fill(bg_color)
                
                # Add static grass blades (only generated once)
                for i in range(5):
                    gx = random.randint(5, CELL_WIDTH - 10)
                    gy = random.randint(5, CELL_HEIGHT - 10)
                    grass_height = random.randint(8, 15)
                    grass_angle = random.uniform(-0.3, 0.3)
                    
                    end_x = gx + math.sin(grass_angle) * grass_height
                    end_y = gy - grass_height
                    
                    grass_color = (bg_color[0] - 30, bg_color[1] - 30, bg_color[2] - 30)
                    pygame.draw.line(grass_surf, grass_color, (gx, gy), (end_x, end_y), 2)
                
                self.grass_textures.append(grass_surf)
    
    def ai_log(self, message):
        """Add a log message and keep only the most recent ones"""
        timestamp = time.strftime("%H:%M:%S")
        self.ai_logs.append(f"[{timestamp}] {message}")
        if len(self.ai_logs) > self.max_logs:
            self.ai_logs.pop(0)
        
        # Also print to console for debugging
        print(f"AI: {message}")

    def draw_top_bar(self):
        # Top bar background
        pygame.draw.rect(screen, PAPER_COLOR, (0, 0, SCREEN_WIDTH, TOP_BAR_HEIGHT))
        pygame.draw.line(screen, BLACK, (0, TOP_BAR_HEIGHT), (SCREEN_WIDTH, TOP_BAR_HEIGHT), 3)
        
        # Sun counter (left)
        sun_x = SIDEBAR_WIDTH + 15
        
        # Small sun icon
        sun_icon_y = 18
        for i in range(6):
            angle = i * 60 * math.pi / 180
            end_x = sun_x + 12 + math.cos(angle) * 10
            end_y = sun_icon_y + math.sin(angle) * 10
            pygame.draw.line(screen, YELLOW_PENCIL, (sun_x + 12, sun_icon_y), (end_x, end_y), 2)
        
        pygame.draw.circle(screen, BLACK, (sun_x + 12, sun_icon_y), 7, 2)
        pygame.draw.circle(screen, YELLOW_PENCIL, (sun_x + 12, sun_icon_y), 6)
        
        sun_text = font.render(f"{self.sun_count}", True, BLACK)
        screen.blit(sun_text, (sun_x + 30, sun_icon_y - 10))
        
        # Wave with progress on same line (middle)
        wave_x = sun_x + 80
        
        # Wave text
        wave_text = small_font.render(f"Wave {self.wave}", True, BLACK)
        screen.blit(wave_text, (wave_x, 12))
        
        # Progress bar (inline with wave text)
        progress_y = 32
        progress_width = 100
        progress_height = 14
        
        pygame.draw.rect(screen, (230, 230, 230), (wave_x, progress_y, progress_width, progress_height))
        pygame.draw.rect(screen, BLACK, (wave_x, progress_y, progress_width, progress_height), 2)
        
        zombies_killed = self.zombies_spawned - len(self.zombies)
        total_zombies = self.zombies_to_spawn
        progress_percent = zombies_killed / total_zombies if total_zombies > 0 else 0
        
        progress_color = GREEN_PENCIL if progress_percent < 0.7 else (ORANGE_PENCIL if progress_percent < 0.9 else RED_PENCIL)
        pygame.draw.rect(screen, progress_color, 
                        (wave_x + 2, progress_y + 2, (progress_width - 4) * progress_percent, progress_height - 4))
        
        remaining_text = small_font.render(f"{zombies_killed}/{total_zombies}", True, BLACK)
        screen.blit(remaining_text, (wave_x + progress_width//2 - remaining_text.get_width()//2, progress_y - 1))
        
        # Controls help (right)
        help_x = wave_x + 120
        help_text = small_font.render("[1-3] Plant  [P] Pause  [R] Restart", True, GRAY_PENCIL)
        screen.blit(help_text, (help_x, 22))

    def draw_plant_icon(self, surface, plant_type, x, y, size=0.6):
        """Draw a mini version of the plant for the card icon"""
        scale = size
        
        if plant_type == "sunflower":
            # Stem
            stem_points = []
            for i in range(8):
                y_pos = y + i * 3 * scale
                x_offset = math.sin(i * 0.5) * 1.5
                stem_points.append((x + x_offset, y_pos))
            pygame.draw.lines(surface, GREEN_PENCIL, False, stem_points, 3)
            
            # Petals
            petal_y = y - 10 * scale
            for i in range(10):
                angle = (i * 36) * math.pi / 180
                petal_length = 18 * scale
                px = x + math.cos(angle) * petal_length
                py = petal_y + math.sin(angle) * petal_length
                
                pygame.draw.line(surface, YELLOW_PENCIL, (x, petal_y), (px, py), 3)
                pygame.draw.circle(surface, YELLOW_PENCIL, (int(px), int(py)), 4)
            
            # Face
            pygame.draw.circle(surface, ORANGE_PENCIL, (x, int(petal_y)), 12)
            pygame.draw.circle(surface, BLACK, (x, int(petal_y)), 12, 1)
            
            pygame.draw.circle(surface, BLACK, (x - 4, int(petal_y - 2)), 2)
            pygame.draw.circle(surface, BLACK, (x + 4, int(petal_y - 2)), 2)
            
            smile_points = [(x - 5, petal_y + 4), (x, petal_y + 6), (x + 5, petal_y + 4)]
            pygame.draw.lines(surface, BLACK, False, smile_points, 1)
        
        elif plant_type == "peashooter":
            # Stem
            stem_points = []
            for i in range(10):
                y_pos = y + i * 2.5 * scale
                x_offset = math.sin(i * 0.4) * 1.5
                stem_points.append((x + x_offset, y_pos))
            pygame.draw.lines(surface, GREEN_PENCIL, False, stem_points, 3)
            
            # Leaves
            leaf_y = y + 8
            pygame.draw.ellipse(surface, GREEN_PENCIL, (x - 25 * scale, leaf_y, 20 * scale, 10))
            pygame.draw.ellipse(surface, BLACK, (x - 25 * scale, leaf_y, 20 * scale, 10), 1)
            pygame.draw.ellipse(surface, GREEN_PENCIL, (x + 5 * scale, leaf_y + 3, 20 * scale, 10))
            pygame.draw.ellipse(surface, BLACK, (x + 5 * scale, leaf_y + 3, 20 * scale, 10), 1)
            
            # Head
            head_y = y - 15 * scale
            pygame.draw.circle(surface, GREEN_PENCIL, (x, int(head_y)), 18)
            pygame.draw.circle(surface, BLACK, (x, int(head_y)), 18, 2)
            
            # Snout
            pygame.draw.ellipse(surface, GREEN_PENCIL, (x + 8, head_y - 8, 22, 16))
            pygame.draw.ellipse(surface, BLACK, (x + 8, head_y - 8, 22, 16), 1)
            
            # Eye
            eye_x = x + 5
            eye_y = int(head_y - 5)
            pygame.draw.circle(surface, WHITE, (eye_x, eye_y), 6)
            pygame.draw.circle(surface, BLACK, (eye_x, eye_y), 6, 1)
            pygame.draw.circle(surface, BLACK, (eye_x + 1, eye_y), 3)
            pygame.draw.circle(surface, WHITE, (eye_x + 2, eye_y - 1), 1)
            
            pygame.draw.line(surface, BLACK, (eye_x - 4, eye_y - 9), (eye_x + 2, eye_y - 7), 1)
            
            pygame.draw.circle(surface, (255, 180, 180), (eye_x - 3, eye_y + 4), 3)
        
        elif plant_type == "wallnut":
            nut_y = y
            
            # Body
            body_rect = (x - 18 * scale, nut_y - 25 * scale, 36 * scale, 50 * scale)
            pygame.draw.ellipse(surface, BROWN_PENCIL, body_rect)
            pygame.draw.ellipse(surface, BLACK, body_rect, 2)
            
            # Highlight
            pygame.draw.ellipse(surface, (200, 160, 100), (x - 13 * scale, nut_y - 32 * scale, 14 * scale, 14 * scale))
            
            # Cracks
            crack1 = [(x - 3, nut_y - 18), (x + 2, nut_y - 10), (x - 1, nut_y - 3)]
            crack2 = [(x + 5, nut_y - 15), (x + 8, nut_y - 6), (x + 4, nut_y + 2)]
            pygame.draw.lines(surface, BLACK, False, crack1, 1)
            pygame.draw.lines(surface, BLACK, False, crack2, 1)
            
            # Eyes
            pygame.draw.circle(surface, WHITE, (x - 7, int(nut_y - 10)), 5)
            pygame.draw.circle(surface, BLACK, (x - 7, int(nut_y - 10)), 5, 1)
            pygame.draw.circle(surface, BLACK, (x - 6, int(nut_y - 10)), 2)
            
            pygame.draw.circle(surface, WHITE, (x + 7, int(nut_y - 10)), 5)
            pygame.draw.circle(surface, BLACK, (x + 7, int(nut_y - 10)), 5, 1)
            pygame.draw.circle(surface, BLACK, (x + 8, int(nut_y - 10)), 2)
            
            # Eyebrows
            pygame.draw.line(surface, BLACK, (x - 12, nut_y - 17), (x - 4, nut_y - 15), 1)
            pygame.draw.line(surface, BLACK, (x + 4, nut_y - 15), (x + 12, nut_y - 17), 1)
            
            # Mouth
            mouth_points = []
            for i in range(5):
                mx = x - 7 + i * 3.5
                my = nut_y + 2 if i == 0 or i == 4 else nut_y - 1
                mouth_points.append((mx, my))
            pygame.draw.lines(surface, BLACK, False, mouth_points, 1)

    def draw_sidebar(self):
        # Sidebar background
        sidebar_rect = pygame.Rect(0, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(screen, PAPER_COLOR, sidebar_rect)
        pygame.draw.rect(screen, BLACK, sidebar_rect, 3)
        
        # Title
        title = title_font.render("PVZ", True, BLACK)
        screen.blit(title, (SIDEBAR_WIDTH//2 - title.get_width()//2, 15))
        
        # Plant cards
        y_offset = 60
        plants_info = [
            ("sunflower", YELLOW_PENCIL, 50),
            ("peashooter", GREEN_PENCIL, 100),
            ("repeater", RED_PENCIL, 200),
            ("wallnut", BROWN_PENCIL, 50)
        ]
        
        for i, (plant_type, color, cost) in enumerate(plants_info):
            y = y_offset + i * 110
            
            # Card
            can_afford = self.sun_count >= cost
            
            if can_afford:
                # Draw background first
                pygame.draw.rect(screen, (255, 255, 250), (8, y, SIDEBAR_WIDTH - 16, 100))
                border_color = BLACK if self.selected_plant == i else (180, 180, 180)
                border_width = 3 if self.selected_plant == i else 2
                pygame.draw.rect(screen, border_color, (8, y, SIDEBAR_WIDTH - 16, 100), border_width)
                
                # Key hint - normal
                pygame.draw.circle(screen, BLACK, (SIDEBAR_WIDTH//2, y + 20), 10, 2)
                key_text = font.render(str(i + 1), True, BLACK)
                screen.blit(key_text, (SIDEBAR_WIDTH//2 - key_text.get_width()//2, y + 12))
                
                # Draw colored plant icon on top
                icon_y = y + 55
                self.draw_plant_icon(screen, plant_type, SIDEBAR_WIDTH//2, icon_y, size=0.5)
                
                # Plant name
                name_map = {"sunflower": "Sunflower", "peashooter": "Peashooter", "repeater": "Repeater", "wallnut": "Wall-nut"}
                plant_name = name_map.get(plant_type, plant_type.capitalize())
                name_surf = small_font.render(plant_name, True, BLACK)
                screen.blit(name_surf, (SIDEBAR_WIDTH//2 - name_surf.get_width()//2, y + 75))
                
                # Cost - gold color
                cost_surf = small_font.render(str(cost), True, (180, 140, 50))
                screen.blit(cost_surf, (SIDEBAR_WIDTH//2 - cost_surf.get_width()//2, y + 90))
            else:
                # Draw icon to a temporary surface first
                temp_surface = pygame.Surface((SIDEBAR_WIDTH - 16, 100), pygame.SRCALPHA)
                self.draw_plant_icon(temp_surface, plant_type, (SIDEBAR_WIDTH - 16)//2, 55, size=0.5)
                
                # Apply grayscale filter to the surface
                for x in range(temp_surface.get_width()):
                    for y_pos in range(temp_surface.get_height()):
                        pixel = temp_surface.get_at((x, y_pos))
                        if pixel[3] > 0:  # If not transparent
                            gray = int(pixel[0] * 0.299 + pixel[1] * 0.587 + pixel[2] * 0.114)
                            temp_surface.set_at((x, y_pos), (gray, gray, gray, pixel[3]))
                
                # Grayed out card background
                pygame.draw.rect(screen, (240, 240, 240), (8, y, SIDEBAR_WIDTH - 16, 100))
                
                # Blit the grayscale icon
                screen.blit(temp_surface, (8, y))
                pygame.draw.rect(screen, (160, 160, 160), (8, y, SIDEBAR_WIDTH - 16, 100), 2)
                
                # Key hint - gray
                pygame.draw.circle(screen, GRAY_PENCIL, (SIDEBAR_WIDTH//2, y + 20), 10, 2)
                key_text = font.render(str(i + 1), True, GRAY_PENCIL)
                screen.blit(key_text, (SIDEBAR_WIDTH//2 - key_text.get_width()//2, y + 12))
                
                # Plant name - gray
                name_map = {"sunflower": "Sunflower", "peashooter": "Peashooter", "repeater": "Repeater", "wallnut": "Wall-nut"}
                plant_name = name_map.get(plant_type, plant_type.capitalize())
                name_surf = small_font.render(plant_name, True, GRAY_PENCIL)
                screen.blit(name_surf, (SIDEBAR_WIDTH//2 - name_surf.get_width()//2, y + 75))
                
                # Cost - gray color
                cost_surf = small_font.render(str(cost), True, GRAY_PENCIL)
                screen.blit(cost_surf, (SIDEBAR_WIDTH//2 - cost_surf.get_width()//2, y + 90))

    def draw_grid(self):
        # Draw pre-generated grass textures
        texture_idx = 0
        for col in range(GRID_COLS):
            for row in range(GRID_ROWS):
                x = GRID_OFFSET_X + col * CELL_WIDTH
                y = GRID_OFFSET_Y + row * CELL_HEIGHT
                
                screen.blit(self.grass_textures[texture_idx], (x, y))
                texture_idx += 1

    def draw_ui(self):
        self.draw_top_bar()
        self.draw_sidebar()
        
        # Pause overlay
        if self.paused:
            pause_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pause_overlay.fill((255, 255, 255, 180))
            screen.blit(pause_overlay, (0, 0))
            
            pause_text = title_font.render("PAUSED", True, BLACK)
            resume_text = font.render("Press [P] to continue", True, GRAY_PENCIL)
            
            screen.blit(pause_text, (SCREEN_WIDTH//2 - pause_text.get_width()//2, SCREEN_HEIGHT//2 - 30))
            screen.blit(resume_text, (SCREEN_WIDTH//2 - resume_text.get_width()//2, SCREEN_HEIGHT//2 + 20))
        
        # AI Mode toggle button (top right corner)
        button_width = 100
        button_height = 28
        button_x = SCREEN_WIDTH - button_width - 10
        button_y = 8
        
        # Button background
        if self.ai_mode:
            button_color = (200, 255, 200)
            border_color = (0, 150, 0)
            text_color = (0, 100, 0)
        else:
            button_color = (250, 250, 250)
            border_color = (150, 150, 150)
            text_color = (100, 100, 100)
        
        pygame.draw.rect(screen, button_color, (button_x, button_y, button_width, button_height), border_radius=5)
        pygame.draw.rect(screen, border_color, (button_x, button_y, button_width, button_height), 2, border_radius=5)
        
        # Button text
        button_text = small_font.render("AI Mode", True, text_color)
        screen.blit(button_text, (button_x + button_width//2 - button_text.get_width()//2, button_y + 5))
        
        # Status indicator
        if self.ai_mode:
            # Green dot
            pygame.draw.circle(screen, (0, 200, 0), (button_x - 15, button_y + button_height//2), 6)
            pygame.draw.circle(screen, (0, 150, 0), (button_x - 15, button_y + button_height//2), 6, 1)
        
        # Store button rect for click detection
        self.ai_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        # AI Action Logs (bottom right corner)
        if self.ai_mode and self.ai_logs:
            log_width = 400
            log_height = 200
            log_x = SCREEN_WIDTH - log_width - 10
            log_y = SCREEN_HEIGHT - log_height - 10
            
            # Log background
            pygame.draw.rect(screen, (250, 250, 245), (log_x, log_y, log_width, log_height), border_radius=5)
            pygame.draw.rect(screen, BLACK, (log_x, log_y, log_width, log_height), 2, border_radius=5)
            
            # Title
            title = small_font.render("AI Action Log:", True, BLACK)
            screen.blit(title, (log_x + 10, log_y + 8))
            
            # Log entries
            log_start_y = log_y + 30
            line_height = 18
            
            max_logs = (log_height - 40) // line_height
            visible_logs = self.ai_logs[-max_logs:]
            
            for i, log in enumerate(visible_logs):
                # Truncate log if too long
                if len(log) > 55:
                    log = log[:52] + "..."
                log_text = small_font.render(log, True, (50, 50, 50))
                screen.blit(log_text, (log_x + 10, log_start_y + i * line_height))

    def ai_decide(self):
        """AI makes decisions about what to do"""
        current_time = time.time()
        
        # Only act at intervals
        if current_time - self.last_ai_action < self.ai_action_interval:
            return
        
        self.last_ai_action = current_time
        
        # Count plants by type and row
        sunflowers = sum(1 for p in self.plants if p.type == "sunflower")
        peashooters_by_row = [0] * GRID_ROWS
        wallnuts_by_row = [0] * GRID_ROWS
        
        for plant in self.plants:
            if plant.type == "peashooter":
                peashooters_by_row[plant.row] += 1
            elif plant.type == "wallnut":
                wallnuts_by_row[plant.row] += 1
        
        # Log current state
        active_zombies = len([z for z in self.zombies if not z.dying])
        self.ai_log(f"Wave {self.wave} | Sun: {self.sun_count} | Sunflowers: {sunflowers} | Zombies: {active_zombies}")
        
        # Priority 1: Collect ALL suns immediately
        for sun in self.suns[:]:
            if sun.active:
                self.sun_count += sun.value
                self.suns.remove(sun)
                self.ai_log(f"Collected sun (+{sun.value}) = {self.sun_count}")
                return  # One action per tick
        
        # Priority 2: Early defense - prepare before zombies arrive
        if self.wave == 1 and sunflowers < 2:
            # First wave: start with 2 sunflowers
            if self.sun_count >= 50:
                for col in range(2):
                    for row in range(GRID_ROWS):
                        if self.grid[col][row] is None:
                            self.place_plant(col, row, "sunflower")
                            self.ai_log(f"Placed sunflower at ({col},{row}) - Early economy")
                            return
        
        # Priority 3: Build defense in each row
        for row in range(GRID_ROWS):
            # Check if this row needs peashooter
            if peashooters_by_row[row] == 0 and self.sun_count >= 100:
                # Each row needs at least one peashooter
                for col in range(2, 4):
                    if self.grid[col][row] is None:
                        self.place_plant(col, row, "peashooter")
                        self.ai_log(f"Placed peashooter at ({col},{row}) - Row defense")
                        return
            
            # Add wallnut in front of peashooter
            if peashooters_by_row[row] > 0 and wallnuts_by_row[row] == 0:
                if self.sun_count >= 50:
                    for col in range(4, 6):
                        if self.grid[col][row] is None:
                            self.place_plant(col, row, "wallnut")
                            self.ai_log(f"Placed wallnut at ({col},{row}) - Row protection")
                            return
        
        # Priority 4: Build more sunflowers (aim for 5 total)
        if sunflowers < 5 and self.sun_count >= 50:
            # Place in leftmost columns
            for col in range(2):
                for row in range(GRID_ROWS):
                    if self.grid[col][row] is None:
                        self.place_plant(col, row, "sunflower")
                        self.ai_log(f"Placed sunflower at ({col},{row}) - Expanding economy")
                        return
        
        # Priority 5: Strengthen defense - second peashooter per row
        for row in range(GRID_ROWS):
            if peashooters_by_row[row] < 2 and self.sun_count >= 100:
                for col in range(3, 5):
                    if self.grid[col][row] is None:
                        self.place_plant(col, row, "peashooter")
                        self.ai_log(f"Placed peashooter at ({col},{row}) - Strengthening row {row}")
                        return
        
        # Priority 6: Extra wallnuts for tough waves
        if self.wave >= 3:
            for row in range(GRID_ROWS):
                if wallnuts_by_row[row] < 2 and self.sun_count >= 50:
                    for col in range(5, 7):
                        if self.grid[col][row] is None:
                            self.place_plant(col, row, "wallnut")
                            self.ai_log(f"Placed wallnut at ({col},{row}) - Extra protection wave {self.wave}")
                            return
        
        # Priority 7: Max out sunflowers late game
        if self.wave >= 5 and sunflowers < 8 and self.sun_count >= 50:
            for col in range(2):
                for row in range(GRID_ROWS):
                    if self.grid[col][row] is None:
                        self.place_plant(col, row, "sunflower")
                        self.ai_log(f"Placed sunflower at ({col},{row}) - Late game economy")
                        return
        
        # Log if waiting for resources
        if self.sun_count < 50:
            self.ai_log("Waiting for sun...")
    
    def place_plant(self, col, row, plant_type):
        """Place a plant at the specified grid position"""
        if self.grid[col][row] is None:
            costs = {"sunflower": 50, "peashooter": 100, "wallnut": 50}
            if self.sun_count >= costs[plant_type]:
                plant = Plant(col, row, plant_type)
                self.plants.append(plant)
                self.grid[col][row] = plant
                self.sun_count -= costs[plant_type]

    def spawn_zombie(self):
        if self.zombies_spawned < self.zombies_to_spawn:
            row = random.randint(0, GRID_ROWS - 1)
            
            # Determine zombie type based on wave
            # Wave 1-2: Only normal + cone
            # Wave 3+: Add football zombies
            if self.wave >= 3 and random.random() < 0.15:
                zombie_type = "football"
            else:
                # 30% chance to spawn conehead zombie (increases with waves)
                cone_chance = 0.2 + (self.wave * 0.05)
                if random.random() < min(cone_chance, 0.5):
                    zombie_type = "cone"
                else:
                    zombie_type = "normal"
            
            self.zombies.append(Zombie(row, zombie_type))
            self.zombies_spawned += 1

    def spawn_natural_sun(self):
        if time.time() - self.last_sun_spawn > 15:
            x = random.randint(GRID_OFFSET_X, GRID_OFFSET_X + GRID_COLS * CELL_WIDTH - 50)
            self.suns.append(Sun(x, -30))
            self.last_sun_spawn = time.time()

    def handle_click(self, pos):
        if self.game_over or self.paused:
            return
        
        x, y = pos
        
        # Check AI Mode toggle button
        if hasattr(self, 'ai_button_rect') and self.ai_button_rect.collidepoint(x, y):
            self.ai_mode = not self.ai_mode
            self.selected_plant = None  # Clear selection when toggling AI
            return
        
        if self.ai_mode:
            return  # Disable manual control in AI mode
        
        # Check plant cards in sidebar
        if x <= SIDEBAR_WIDTH:
            y_offset = 60
            for i in range(3):
                card_y = y_offset + i * 110
                if card_y <= y <= card_y + 100:
                    plant_types = ["sunflower", "peashooter", "wallnut"]
                    costs = [50, 100, 50]
                    if self.sun_count >= costs[i]:
                        self.selected_plant = i
                    return
        
        # Check suns
        for sun in self.suns[:]:
            if sun.active:
                distance = math.sqrt((x - sun.x)**2 + (y - sun.y)**2)
                if distance < sun.radius + 15:
                    self.sun_count += sun.value
                    self.suns.remove(sun)
                    return
        
        # Check grid
        if GRID_OFFSET_X <= x <= GRID_OFFSET_X + GRID_COLS * CELL_WIDTH:
            if GRID_OFFSET_Y <= y <= GRID_OFFSET_Y + GRID_ROWS * CELL_HEIGHT:
                col = (x - GRID_OFFSET_X) // CELL_WIDTH
                row = (y - GRID_OFFSET_Y) // CELL_HEIGHT
                
                if self.selected_plant is not None:
                    plant_types = ["sunflower", "peashooter", "wallnut"]
                    costs = [50, 100, 50]
                    
                    if self.sun_count >= costs[self.selected_plant]:
                        if self.grid[col][row] is None:
                            plant_type = plant_types[self.selected_plant]
                            plant = Plant(col, row, plant_type)
                            self.plants.append(plant)
                            self.grid[col][row] = plant
                            self.sun_count -= costs[self.selected_plant]
                            self.selected_plant = None

    def update(self):
        if self.game_over or self.paused:
            return
        
        # AI Mode: Let AI make decisions
        if self.ai_mode:
            self.ai_decide()
        
        current_time = time.time()
        
        # Spawn zombies
        if current_time - self.last_spawn > self.spawn_interval:
            self.spawn_zombie()
            self.last_spawn = current_time
        
        # Wave completion
        if self.zombies_spawned >= self.zombies_to_spawn and len(self.zombies) == 0:
            self.wave += 1
            self.zombies_spawned = 0
            self.zombies_to_spawn = 3 + self.wave
            self.spawn_interval = max(5, 12 - self.wave * 0.5)
        
        # Natural sun
        self.spawn_natural_sun()
        
        # Update plants
        for plant in self.plants[:]:
            if plant.type == "sunflower":
                if current_time - plant.last_sun > 15:
                    self.suns.append(Sun(plant.x, plant.y - 30, is_bright=True))
                    plant.last_sun = current_time
            
            elif plant.type == "peashooter":
                has_zombie = any(z.row == plant.row and z.x > plant.x for z in self.zombies)
                if has_zombie and current_time - plant.last_shot > 1.5:
                    self.peas.append(Pea(plant.x + 20, plant.y - 15, plant.row))
                    plant.last_shot = current_time
            
            elif plant.type == "repeater":
                has_zombie = any(z.row == plant.row and z.x > plant.x for z in self.zombies)
                if has_zombie and current_time - plant.last_shot > 1.5:
                    # Shoot two peas rapidly!
                    self.peas.append(Pea(plant.x + 20, plant.y - 18, plant.row))
                    # Second pea comes shortly after
                    self.peas.append(Pea(plant.x + 20, plant.y - 12, plant.row))
                    plant.last_shot = current_time
            
            if plant.hp <= 0:
                self.plants.remove(plant)
                self.grid[plant.col][plant.row] = None
        
        # Update zombies
        for zombie in self.zombies[:]:
            # Skip dying zombies for game logic
            if zombie.dying:
                zombie.move()
                # Remove death animation finished
                if zombie.death_timer >= zombie.death_duration:
                    self.zombies.remove(zombie)
                continue
            
            zombie.eating = False
            
            for plant in self.plants:
                if plant.row == zombie.row:
                    if abs(zombie.x - plant.x) < 30:
                        zombie.eating = True
                        if current_time - zombie.last_attack > zombie.attack_speed:
                            plant.hp -= zombie.damage
                            zombie.last_attack = current_time
                        break
            
            zombie.move()
            
            if zombie.hp <= 0 and not zombie.dying:
                # Trigger death animation instead of removing
                zombie.dying = True
                continue
            
            if zombie.x < GRID_OFFSET_X - 20:
                self.game_over = True
        
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

    def draw(self):
        # Plain paper background (no grid lines)
        screen.fill(PAPER_COLOR)
        
        self.draw_grid()
        
        # Draw entities
        for plant in self.plants:
            plant.draw(screen)
        
        for zombie in self.zombies:
            zombie.draw(screen)
        
        for pea in self.peas:
            pea.draw(screen)
        
        for sun in self.suns:
            sun.draw(screen)
        
        self.draw_ui()
        
        # Game over
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 220))
            screen.blit(overlay, (0, 0))
            
            game_over_text = title_font.render("GAME OVER", True, RED_PENCIL)
            wave_text = font.render(f"You survived {self.wave} waves", True, BLACK)
            restart_text = font.render("Press [R] to try again", True, GRAY_PENCIL)
            
            screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 60))
            screen.blit(wave_text, (SCREEN_WIDTH//2 - wave_text.get_width()//2, SCREEN_HEIGHT//2))
            screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 50))

def main():
    game = Game()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    game.handle_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    if not game.ai_mode and game.sun_count >= 50:
                        game.selected_plant = 0
                elif event.key == pygame.K_2:
                    if not game.ai_mode and game.sun_count >= 100:
                        game.selected_plant = 1
                elif event.key == pygame.K_3:
                    if not game.ai_mode and game.sun_count >= 50:
                        game.selected_plant = 2
                elif event.key == pygame.K_p:
                    game.paused = not game.paused
                elif event.key == pygame.K_r:
                    game = Game()
                elif event.key == pygame.K_a:
                    game.ai_mode = not game.ai_mode
                    game.selected_plant = None  # Clear selection when toggling AI
        
        game.update()
        game.draw()
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()
