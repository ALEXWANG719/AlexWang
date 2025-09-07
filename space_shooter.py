import pygame
import random
import sys
import math
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)

class GameState(Enum):
    PLAYING = 1
    GAME_OVER = 2

class Star:
    """Star class for background starfield"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = random.uniform(0.5, 3.0)
        self.brightness = random.randint(100, 255)
        self.size = random.randint(1, 2)
        
    def update(self):
        """Update star position"""
        self.y += self.speed
        
    def draw(self, screen):
        """Draw the star"""
        color = (self.brightness, self.brightness, self.brightness)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)
    
    def is_off_screen(self):
        """Check if star is off screen"""
        return self.y > SCREEN_HEIGHT

class Player:
    """Player spaceship class"""
    def __init__(self, x, y, player_id=1):
        self.x = x
        self.y = y
        self.speed = 5
        self.player_id = player_id
        self.color = CYAN if player_id == 1 else GREEN  # Different colors for each player
        
        # Load player sprite
        try:
            self.sprite = pygame.image.load("Pasted Graphic-3.png")
            self.sprite = pygame.transform.scale(self.sprite, (40, 30))  # Resize to fit game
            self.width = self.sprite.get_width()
            self.height = self.sprite.get_height()
        except pygame.error:
            # Fallback to simple drawing if image fails to load
            self.sprite = None
            self.width = 40
            self.height = 30
        
    def move(self, dx, dy):
        """Move the player ship"""
        self.x += dx * self.speed
        self.y += dy * self.speed
        
        # Keep player within screen bounds
        self.x = max(0, min(SCREEN_WIDTH - self.width, self.x))
        self.y = max(0, min(SCREEN_HEIGHT - self.height, self.y))
    
    def draw(self, screen):
        """Draw the player spaceship"""
        if self.sprite:
            # Draw the loaded sprite with color tinting
            if self.player_id == 2:
                # Create a green-tinted version for player 2
                tinted_sprite = self.sprite.copy()
                tinted_sprite.fill((0, 255, 0, 128), special_flags=pygame.BLEND_MULT)
                screen.blit(tinted_sprite, (self.x, self.y))
            else:
                screen.blit(self.sprite, (self.x, self.y))
        else:
            # Fallback to simple pixel-style spaceship
            pygame.draw.polygon(screen, self.color, [
                (self.x + self.width // 2, self.y),  # Top point
                (self.x, self.y + self.height),      # Bottom left
                (self.x + self.width // 4, self.y + self.height * 0.7),  # Left wing
                (self.x + self.width * 3 // 4, self.y + self.height * 0.7),  # Right wing
                (self.x + self.width, self.y + self.height)  # Bottom right
            ])
            # Ship body
            body_color = BLUE if self.player_id == 1 else (0, 150, 0)
            pygame.draw.rect(screen, body_color, (self.x + self.width // 3, self.y + self.height // 3, 
                                                 self.width // 3, self.height // 2))
    
    def get_rect(self):
        """Get collision rectangle"""
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Bullet:
    """Bullet class for player shots"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 4
        self.height = 10
        self.speed = 7
        
    def update(self):
        """Update bullet position"""
        self.y -= self.speed
        
    def draw(self, screen):
        """Draw the bullet"""
        pygame.draw.rect(screen, YELLOW, (self.x, self.y, self.width, self.height))
    
    def is_off_screen(self):
        """Check if bullet is off screen"""
        return self.y < 0
    
    def get_rect(self):
        """Get collision rectangle"""
        return pygame.Rect(self.x, self.y, self.width, self.height)

class EnemyBullet:
    """Enemy bullet class"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 4
        self.height = 8
        self.speed = 4
        
    def update(self):
        """Update bullet position"""
        self.y += self.speed
        
    def draw(self, screen):
        """Draw the enemy bullet"""
        pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))
    
    def is_off_screen(self):
        """Check if bullet is off screen"""
        return self.y > SCREEN_HEIGHT
    
    def get_rect(self):
        """Get collision rectangle"""
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Asteroid:
    """Asteroid obstacle class"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = random.randint(20, 40)
        self.height = random.randint(20, 40)
        self.speed = random.uniform(1, 2.5)
        self.rotation = 0
        self.rotation_speed = random.uniform(-3, 3)
        
    def update(self):
        """Update asteroid position and rotation"""
        self.y += self.speed
        self.rotation += self.rotation_speed
        
    def draw(self, screen):
        """Draw the asteroid"""
        # Create a rotated surface for the asteroid
        asteroid_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        # Draw a rough asteroid shape
        pygame.draw.polygon(asteroid_surface, (100, 100, 100), [
            (self.width // 2, 0),
            (self.width, self.height // 3),
            (self.width * 0.8, self.height * 0.7),
            (self.width * 0.6, self.height),
            (self.width * 0.3, self.height * 0.8),
            (0, self.height * 0.5),
            (self.width * 0.2, self.height * 0.2)
        ])
        
        # Rotate the asteroid
        rotated_asteroid = pygame.transform.rotate(asteroid_surface, self.rotation)
        # Center the rotated asteroid
        rect = rotated_asteroid.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        screen.blit(rotated_asteroid, rect)
    
    def is_off_screen(self):
        """Check if asteroid is off screen"""
        return self.y > SCREEN_HEIGHT
    
    def get_rect(self):
        """Get collision rectangle"""
        return pygame.Rect(self.x, self.y, self.width, self.height)

class ExplosionProjectile:
    """Explosion projectile shot by the grenade boss"""
    def __init__(self, x, y, target_x, target_y):
        self.x = x
        self.y = y
        self.width = 8
        self.height = 8
        self.speed = 4
        
        # Calculate direction to target
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx*dx + dy*dy)
        if distance > 0:
            self.dx = (dx / distance) * self.speed
            self.dy = (dy / distance) * self.speed
        else:
            self.dx = 0
            self.dy = self.speed
        
        self.explosion_radius = 30
        self.has_exploded = False
        self.explosion_timer = 0
        self.explosion_duration = 20
        
    def update(self):
        """Update projectile position"""
        if not self.has_exploded:
            self.x += self.dx
            self.y += self.dy
        else:
            self.explosion_timer += 1
    
    def draw(self, screen):
        """Draw the projectile or explosion"""
        if not self.has_exploded:
            # Draw projectile
            pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), 4)
        else:
            # Draw explosion
            if self.explosion_timer < self.explosion_duration:
                progress = self.explosion_timer / self.explosion_duration
                radius = int(self.explosion_radius * progress)
                # Draw explosion rings
                for i in range(3):
                    ring_radius = radius - (i * 8)
                    if ring_radius > 0:
                        color_intensity = int(255 * (1 - progress))
                        color = (255, color_intensity, 0)  # White to orange
                        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), ring_radius, 2)
    
    def explode(self):
        """Trigger explosion"""
        self.has_exploded = True
        self.explosion_timer = 0
    
    def is_off_screen(self):
        """Check if projectile is off screen"""
        return (self.x < -50 or self.x > SCREEN_WIDTH + 50 or 
                self.y < -50 or self.y > SCREEN_HEIGHT + 50)
    
    def is_explosion_finished(self):
        """Check if explosion effect is finished"""
        return self.has_exploded and self.explosion_timer >= self.explosion_duration
    
    def get_explosion_rect(self):
        """Get explosion collision rectangle"""
        if self.has_exploded and self.explosion_timer < self.explosion_duration:
            progress = self.explosion_timer / self.explosion_duration
            radius = int(self.explosion_radius * progress)
            return pygame.Rect(self.x - radius, self.y - radius, radius * 2, radius * 2)
        return None

class GrenadeBoss:
    """Big white grenade boss that shoots explosions"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 60
        self.height = 60
        self.speed = 1
        self.health = 10  # Boss takes multiple hits to destroy
        self.max_health = 10
        
        # Movement pattern
        self.movement_timer = 0
        self.movement_direction = 1  # 1 for right, -1 for left
        
        # Shooting
        self.shoot_timer = 0
        self.shoot_delay = 90  # Shoots every 1.5 seconds
        self.projectiles = []
        
        # Visual effects
        self.flash_timer = 0
        self.flash_duration = 10
        
    def update(self, player_x, player_y):
        """Update boss position and behavior"""
        # Movement - oscillate left and right
        self.movement_timer += 1
        if self.movement_timer > 60:  # Change direction every second
            self.movement_direction *= -1
            self.movement_timer = 0
        
        self.x += self.movement_direction * self.speed
        self.x = max(0, min(SCREEN_WIDTH - self.width, self.x))
        
        # Shooting
        self.shoot_timer += 1
        if self.shoot_timer >= self.shoot_delay:
            # Shoot explosion at player
            projectile = ExplosionProjectile(
                self.x + self.width // 2, 
                self.y + self.height,
                player_x + 20,  # Aim at player center
                player_y + 15
            )
            self.projectiles.append(projectile)
            self.shoot_timer = 0
        
        # Update projectiles
        for projectile in self.projectiles[:]:
            projectile.update()
            if projectile.is_off_screen() or projectile.is_explosion_finished():
                self.projectiles.remove(projectile)
            elif not projectile.has_exploded and projectile.y > SCREEN_HEIGHT * 0.7:
                # Explode when reaching lower part of screen
                projectile.explode()
        
        # Update flash timer
        if self.flash_timer > 0:
            self.flash_timer -= 1
    
    def draw(self, screen):
        """Draw the boss"""
        # Flash effect when hit
        if self.flash_timer > 0 and (self.flash_timer // 3) % 2 == 0:
            color = RED
        else:
            color = WHITE
        
        # Draw boss body (big white grenade)
        pygame.draw.ellipse(screen, color, (self.x, self.y, self.width, self.height))
        pygame.draw.ellipse(screen, (200, 200, 200), (self.x + 5, self.y + 5, self.width - 10, self.height - 10), 2)
        
        # Draw health bar
        bar_width = 60
        bar_height = 8
        bar_x = self.x + (self.width - bar_width) // 2
        bar_y = self.y - 15
        
        # Background
        pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
        # Health
        health_width = int(bar_width * (self.health / self.max_health))
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, health_width, bar_height))
        
        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(screen)
    
    def take_damage(self):
        """Take damage from player bullets"""
        self.health -= 1
        self.flash_timer = self.flash_duration
        return self.health <= 0
    
    def is_off_screen(self):
        """Check if boss is off screen"""
        return self.y > SCREEN_HEIGHT
    
    def get_rect(self):
        """Get collision rectangle"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def get_explosion_rects(self):
        """Get all active explosion collision rectangles"""
        explosion_rects = []
        for projectile in self.projectiles:
            rect = projectile.get_explosion_rect()
            if rect:
                explosion_rects.append(rect)
        return explosion_rects

class SpaceHole:
    """Space hole that allows passage through laser barrier"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 20
        self.rotation = 0
        self.rotation_speed = 2
        
    def update(self):
        """Update hole rotation"""
        self.rotation += self.rotation_speed
        
    def draw(self, screen):
        """Draw the space hole"""
        # Create a rotating hole effect
        hole_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Draw the hole (black circle with rotating effect)
        center_x, center_y = self.width // 2, self.height // 2
        pygame.draw.circle(hole_surface, BLACK, (center_x, center_y), 15)
        
        # Add rotating lines for effect
        for i in range(4):
            angle = self.rotation + i * 90
            start_x = center_x + 8 * math.cos(math.radians(angle))
            start_y = center_y + 8 * math.sin(math.radians(angle))
            end_x = center_x + 18 * math.cos(math.radians(angle))
            end_y = center_y + 18 * math.sin(math.radians(angle))
            pygame.draw.line(hole_surface, CYAN, (start_x, start_y), (end_x, end_y), 2)
        
        # Rotate the surface
        rotated_hole = pygame.transform.rotate(hole_surface, self.rotation)
        rect = rotated_hole.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        screen.blit(rotated_hole, rect)
    
    def get_rect(self):
        """Get collision rectangle"""
        return pygame.Rect(self.x, self.y, self.width, self.height)

class SpaceLaser:
    """Space laser barrier that blocks movement"""
    def __init__(self, y_position):
        self.y = y_position
        self.height = 8
        self.width = SCREEN_WIDTH
        self.active = True
        self.space_hole = None
        self.hole_timer = 0
        self.hole_duration = 300  # Hole stays open for 5 seconds
        self.laser_timer = 0
        self.laser_duration = 1800  # Laser stays active for 30 seconds
        
    def update(self):
        """Update laser and hole states"""
        self.laser_timer += 1
        
        if self.space_hole:
            self.hole_timer += 1
            self.space_hole.update()
            
            # Close hole after duration
            if self.hole_timer >= self.hole_duration:
                self.space_hole = None
                self.hole_timer = 0
        
        # Deactivate laser after duration
        if self.laser_timer >= self.laser_duration:
            self.active = False
    
    def create_space_hole(self):
        """Create a space hole in the laser"""
        if not self.space_hole:
            # Create hole at random x position
            hole_x = random.randint(50, SCREEN_WIDTH - 90)
            self.space_hole = SpaceHole(hole_x, self.y - 10)
            self.hole_timer = 0
    
    def draw(self, screen):
        """Draw the laser barrier"""
        if not self.active:
            return
            
        # Draw laser beam
        laser_color = (255, 0, 255)  # Magenta laser
        pygame.draw.rect(screen, laser_color, (0, self.y, self.width, self.height))
        
        # Add laser glow effect
        for i in range(3):
            glow_color = (255, 0, 255, 50 - i * 15)
            glow_rect = pygame.Rect(-i, self.y - i, self.width + i * 2, self.height + i * 2)
            pygame.draw.rect(screen, laser_color, glow_rect, 1)
        
        # Draw space hole if active
        if self.space_hole:
            self.space_hole.draw(screen)
    
    def can_pass_through(self, player_rect):
        """Check if player can pass through the laser"""
        if not self.active:
            return True
            
        # Check if player is in the space hole
        if self.space_hole and player_rect.colliderect(self.space_hole.get_rect()):
            return True
            
        return False
    
    def get_rect(self):
        """Get laser collision rectangle"""
        return pygame.Rect(0, self.y, self.width, self.height)

class ExplosiveSeed:
    """Explosive seed projectile shot by robotic bird boss"""
    def __init__(self, x, y, target_x, target_y):
        self.x = x
        self.y = y
        self.width = 6
        self.height = 6
        self.speed = 3
        
        # Calculate direction to target
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx*dx + dy*dy)
        if distance > 0:
            self.dx = (dx / distance) * self.speed
            self.dy = (dy / distance) * self.speed
        else:
            self.dx = 0
            self.dy = self.speed
        
        self.explosion_radius = 25
        self.has_exploded = False
        self.explosion_timer = 0
        self.explosion_duration = 15
        self.proximity_trigger_distance = 40  # Explode when close to player
        
    def update(self, player_x, player_y):
        """Update seed position and check for proximity explosion"""
        if not self.has_exploded:
            self.x += self.dx
            self.y += self.dy
            
            # Check if close to player
            distance_to_player = math.sqrt((self.x - player_x)**2 + (self.y - player_y)**2)
            if distance_to_player <= self.proximity_trigger_distance:
                self.explode()
        else:
            self.explosion_timer += 1
    
    def draw(self, screen):
        """Draw the seed or explosion"""
        if not self.has_exploded:
            # Draw seed (brown/beige color)
            pygame.draw.circle(screen, (139, 69, 19), (int(self.x), int(self.y)), 3)
            # Add small highlight
            pygame.draw.circle(screen, (160, 82, 45), (int(self.x - 1), int(self.y - 1)), 1)
        else:
            # Draw explosion
            if self.explosion_timer < self.explosion_duration:
                progress = self.explosion_timer / self.explosion_duration
                radius = int(self.explosion_radius * progress)
                # Draw explosion rings
                for i in range(3):
                    ring_radius = radius - (i * 6)
                    if ring_radius > 0:
                        color_intensity = int(255 * (1 - progress))
                        color = (255, color_intensity // 2, 0)  # Orange to red
                        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), ring_radius, 2)
    
    def explode(self):
        """Trigger explosion"""
        self.has_exploded = True
        self.explosion_timer = 0
    
    def is_off_screen(self):
        """Check if seed is off screen"""
        return (self.x < -50 or self.x > SCREEN_WIDTH + 50 or 
                self.y < -50 or self.y > SCREEN_HEIGHT + 50)
    
    def is_explosion_finished(self):
        """Check if explosion effect is finished"""
        return self.has_exploded and self.explosion_timer >= self.explosion_duration
    
    def get_explosion_rect(self):
        """Get explosion collision rectangle"""
        if self.has_exploded and self.explosion_timer < self.explosion_duration:
            progress = self.explosion_timer / self.explosion_duration
            radius = int(self.explosion_radius * progress)
            return pygame.Rect(self.x - radius, self.y - radius, radius * 2, radius * 2)
        return None

class RoboticBirdBoss:
    """Big robotic bird boss that shoots explosive seeds"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 80
        self.height = 60
        self.speed = 2
        self.health = 15  # More health than grenade boss
        self.max_health = 15
        
        # Movement pattern - bird-like swooping
        self.movement_timer = 0
        self.movement_phase = 0  # 0: flying right, 1: swooping down, 2: flying left, 3: swooping up
        self.phase_timer = 0
        self.phase_duration = 120  # 2 seconds per phase
        
        # Shooting
        self.shoot_timer = 0
        self.shoot_delay = 60  # Shoots every second
        self.seeds = []
        
        # Visual effects
        self.flash_timer = 0
        self.flash_duration = 10
        self.wing_flap_timer = 0
        self.wing_flap_speed = 8
        
    def update(self, player_x, player_y):
        """Update bird position and behavior"""
        # Bird-like movement pattern
        self.movement_timer += 1
        self.phase_timer += 1
        
        if self.phase_timer >= self.phase_duration:
            self.movement_phase = (self.movement_phase + 1) % 4
            self.phase_timer = 0
        
        # Movement based on phase
        if self.movement_phase == 0:  # Flying right
            self.x += self.speed
        elif self.movement_phase == 1:  # Swooping down
            self.x += self.speed * 0.5
            self.y += self.speed
        elif self.movement_phase == 2:  # Flying left
            self.x -= self.speed
        elif self.movement_phase == 3:  # Swooping up
            self.x -= self.speed * 0.5
            self.y -= self.speed
        
        # Keep bird within screen bounds
        self.x = max(0, min(SCREEN_WIDTH - self.width, self.x))
        self.y = max(50, min(SCREEN_HEIGHT - 100, self.y))
        
        # Shooting
        self.shoot_timer += 1
        if self.shoot_timer >= self.shoot_delay:
            # Shoot multiple seeds in spread pattern
            for i in range(3):
                angle_offset = (i - 1) * 0.3  # Spread seeds
                target_x = player_x + 20 + math.cos(angle_offset) * 30
                target_y = player_y + 15 + math.sin(angle_offset) * 30
                
                seed = ExplosiveSeed(
                    self.x + self.width // 2, 
                    self.y + self.height,
                    target_x, target_y
                )
                self.seeds.append(seed)
            self.shoot_timer = 0
        
        # Update seeds
        for seed in self.seeds[:]:
            seed.update(player_x, player_y)
            if seed.is_off_screen() or seed.is_explosion_finished():
                self.seeds.remove(seed)
        
        # Update visual effects
        if self.flash_timer > 0:
            self.flash_timer -= 1
        self.wing_flap_timer += 1
    
    def draw(self, screen):
        """Draw the robotic bird boss"""
        # Flash effect when hit
        if self.flash_timer > 0 and (self.flash_timer // 3) % 2 == 0:
            body_color = RED
            wing_color = (200, 0, 0)
        else:
            body_color = (100, 100, 100)  # Gray metallic
            wing_color = (80, 80, 80)
        
        # Wing flapping animation
        wing_offset = int(5 * math.sin(self.wing_flap_timer * self.wing_flap_speed * 0.1))
        
        # Draw bird body (oval)
        pygame.draw.ellipse(screen, body_color, (self.x + 20, self.y + 15, 40, 30))
        
        # Draw wings (flapping)
        pygame.draw.ellipse(screen, wing_color, (self.x + 5, self.y + 10 + wing_offset, 25, 20))
        pygame.draw.ellipse(screen, wing_color, (self.x + 50, self.y + 10 - wing_offset, 25, 20))
        
        # Draw head
        pygame.draw.circle(screen, body_color, (int(self.x + 45), int(self.y + 20)), 12)
        
        # Draw robotic eye
        pygame.draw.circle(screen, RED, (int(self.x + 48), int(self.y + 18)), 4)
        pygame.draw.circle(screen, WHITE, (int(self.x + 49), int(self.y + 17)), 2)
        
        # Draw beak
        pygame.draw.polygon(screen, (200, 200, 0), [
            (self.x + 55, self.y + 20),
            (self.x + 65, self.y + 18),
            (self.x + 65, self.y + 22)
        ])
        
        # Draw legs
        pygame.draw.line(screen, (150, 150, 150), (self.x + 30, self.y + 45), (self.x + 30, self.y + 55), 3)
        pygame.draw.line(screen, (150, 150, 150), (self.x + 50, self.y + 45), (self.x + 50, self.y + 55), 3)
        
        # Draw health bar
        bar_width = 80
        bar_height = 8
        bar_x = self.x + (self.width - bar_width) // 2
        bar_y = self.y - 15
        
        # Background
        pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
        # Health
        health_width = int(bar_width * (self.health / self.max_health))
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, health_width, bar_height))
        
        # Draw seeds
        for seed in self.seeds:
            seed.draw(screen)
    
    def take_damage(self):
        """Take damage from player bullets"""
        self.health -= 1
        self.flash_timer = self.flash_duration
        return self.health <= 0
    
    def is_off_screen(self):
        """Check if bird is off screen"""
        return self.y > SCREEN_HEIGHT
    
    def get_rect(self):
        """Get collision rectangle"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def get_explosion_rects(self):
        """Get all active seed explosion collision rectangles"""
        explosion_rects = []
        for seed in self.seeds:
            rect = seed.get_explosion_rect()
            if rect:
                explosion_rects.append(rect)
        return explosion_rects

class Enemy:
    """Enemy spaceship class"""
    def __init__(self, x, y, difficulty_level=1):
        self.x = x
        self.y = y
        self.base_speed = random.uniform(1, 3)
        self.speed = self.base_speed * (1 + difficulty_level * 0.3)  # Speed increases with difficulty
        self.shoot_timer = 0
        self.shoot_delay = max(30, random.randint(60, 120) - difficulty_level * 10)  # Faster shooting with difficulty
        
        # Swinging movement parameters
        self.swing_amplitude = 20 + difficulty_level * 10  # How wide the swing is
        self.swing_frequency = 0.05 + difficulty_level * 0.02  # How fast the swing is
        self.swing_phase = random.uniform(0, 2 * 3.14159)  # Random starting phase
        self.original_x = x  # Store original x position for swinging
        
        # Load enemy sprite
        try:
            self.sprite = pygame.image.load("Pasted Graphic-4.png")
            self.sprite = pygame.transform.scale(self.sprite, (30, 25))  # Resize to fit game
            self.width = self.sprite.get_width()
            self.height = self.sprite.get_height()
        except pygame.error:
            # Fallback to simple drawing if image fails to load
            self.sprite = None
            self.width = 30
            self.height = 25
        
    def update(self):
        """Update enemy position and shooting timer"""
        self.y += self.speed
        self.shoot_timer += 1
        
        # Add swinging movement
        self.swing_phase += self.swing_frequency
        swing_offset = self.swing_amplitude * math.sin(self.swing_phase)
        self.x = self.original_x + swing_offset
        
        # Keep enemy within screen bounds
        self.x = max(0, min(SCREEN_WIDTH - self.width, self.x))
    
    def can_shoot(self):
        """Check if enemy can shoot"""
        return self.shoot_timer >= self.shoot_delay
    
    def shoot(self):
        """Create an enemy bullet"""
        self.shoot_timer = 0
        self.shoot_delay = random.randint(60, 120)  # Reset delay
        return EnemyBullet(self.x + self.width // 2 - 2, self.y + self.height)
        
    def draw(self, screen):
        """Draw the enemy spaceship"""
        if self.sprite:
            # Draw the loaded sprite
            screen.blit(self.sprite, (self.x, self.y))
        else:
            # Fallback to simple pixel-style enemy ship
            pygame.draw.polygon(screen, RED, [
                (self.x + self.width // 2, self.y + self.height),  # Bottom point
                (self.x, self.y),                                   # Top left
                (self.x + self.width // 4, self.y + self.height * 0.3),  # Left wing
                (self.x + self.width * 3 // 4, self.y + self.height * 0.3),  # Right wing
                (self.x + self.width, self.y)  # Top right
            ])
            # Enemy body
            pygame.draw.rect(screen, (200, 0, 0), (self.x + self.width // 4, self.y + self.height // 3, 
                                                  self.width // 2, self.height // 2))
    
    def is_off_screen(self):
        """Check if enemy is off screen"""
        return self.y > SCREEN_HEIGHT
    
    def get_rect(self):
        """Get collision rectangle"""
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Game:
    """Main game class"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Shooter")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        
        # Game state
        self.state = GameState.PLAYING
        self.score = 0
        self.lives = 3
        self.invulnerable_timer = 0
        self.invulnerable_duration = 120  # 2 seconds of invulnerability after respawn
        self.has_bomb = True  # Player starts with one bomb per round
        self.bomb_explosion_timer = 0
        self.bomb_explosion_duration = 30  # Explosion effect duration
        
        # Difficulty system
        self.difficulty_level = 1
        self.base_enemy_spawn_delay = 60
        
        # Game objects - Single player
        self.player = Player(SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT - 50, 1)
        self.bullets = []
        self.enemies = []
        self.enemy_bullets = []
        self.asteroids = []
        self.stars = []
        self.boss = None
        self.boss_type = "grenade"  # Track which boss type to spawn next
        self.space_laser = None
        
        # Spawning timers
        self.enemy_spawn_timer = 0
        self.enemy_spawn_delay = self.base_enemy_spawn_delay
        self.asteroid_spawn_timer = 0
        self.asteroid_spawn_delay = 120  # frames
        self.star_spawn_timer = 0
        self.star_spawn_delay = 2  # frames (spawn stars frequently)
        self.boss_spawn_timer = 0
        self.boss_spawn_delay = 1800  # Spawn boss every 30 seconds
        self.laser_spawn_timer = 0
        self.laser_spawn_delay = 1200  # Spawn laser every 20 seconds
        self.boss_warning_timer = 0
        self.boss_warning_duration = 180  # Warning shows for 3 seconds
        
        # Initialize starfield
        self.initialize_starfield()
    
    def update_difficulty(self):
        """Update difficulty level based on score"""
        # Increase difficulty every 100 points
        new_difficulty = min(10, 1 + self.score // 100)  # Cap at level 10
        
        if new_difficulty != self.difficulty_level:
            self.difficulty_level = new_difficulty
            # Update enemy spawn delay (faster spawning with higher difficulty)
            self.enemy_spawn_delay = max(20, self.base_enemy_spawn_delay - self.difficulty_level * 5)
    
    def initialize_starfield(self):
        """Initialize the background starfield"""
        # Create initial stars across the screen
        for _ in range(50):  # Start with 50 stars
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            self.stars.append(Star(x, y))
        
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if self.state == GameState.PLAYING:
                    if event.key == pygame.K_SPACE:
                        # Shoot bullet
                        bullet = Bullet(self.player.x + self.player.width // 2 - 2, self.player.y)
                        self.bullets.append(bullet)
                    elif event.key == pygame.K_b and self.has_bomb:
                        # Activate atomic bomb
                        self.activate_bomb()
                    elif event.key == pygame.K_h and self.space_laser and self.space_laser.active:
                        # Create space hole in laser (H key)
                        self.space_laser.create_space_hole()
                elif event.key == pygame.K_r and self.state == GameState.GAME_OVER:
                    # Restart game
                    self.restart_game()
        return True
    
    def update(self):
        """Update game logic"""
        if self.state != GameState.PLAYING:
            return
            
        # Handle player movement
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = 1
            
        self.player.move(dx, dy)
        
        # Update difficulty based on score
        self.update_difficulty()
        
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.is_off_screen():
                self.bullets.remove(bullet)
        
        # Update enemy bullets
        for bullet in self.enemy_bullets[:]:
            bullet.update()
            if bullet.is_off_screen():
                self.enemy_bullets.remove(bullet)
        
        # Spawn enemies
        self.enemy_spawn_timer += 1
        if self.enemy_spawn_timer >= self.enemy_spawn_delay:
            enemy = Enemy(random.randint(0, SCREEN_WIDTH - 30), -25, self.difficulty_level)
            self.enemies.append(enemy)
            self.enemy_spawn_timer = 0
        
        # Update enemies and handle shooting
        for enemy in self.enemies[:]:
            enemy.update()
            if enemy.is_off_screen():
                self.enemies.remove(enemy)
            elif enemy.can_shoot():
                enemy_bullet = enemy.shoot()
                self.enemy_bullets.append(enemy_bullet)
        
        # Spawn asteroids
        self.asteroid_spawn_timer += 1
        if self.asteroid_spawn_timer >= self.asteroid_spawn_delay:
            asteroid = Asteroid(random.randint(0, SCREEN_WIDTH - 40), -40)
            self.asteroids.append(asteroid)
            self.asteroid_spawn_timer = 0
        
        # Update asteroids
        for asteroid in self.asteroids[:]:
            asteroid.update()
            if asteroid.is_off_screen():
                self.asteroids.remove(asteroid)
        
        # Update stars
        for star in self.stars[:]:
            star.update()
            if star.is_off_screen():
                self.stars.remove(star)
        
        # Spawn new stars
        self.star_spawn_timer += 1
        if self.star_spawn_timer >= self.star_spawn_delay:
            # Spawn new star at top of screen
            new_star = Star(random.randint(0, SCREEN_WIDTH), -5)
            self.stars.append(new_star)
            self.star_spawn_timer = 0
        
        # Spawn laser barrier
        self.laser_spawn_timer += 1
        if self.laser_spawn_timer >= self.laser_spawn_delay and self.space_laser is None:
            # Spawn laser at middle of screen
            self.space_laser = SpaceLaser(SCREEN_HEIGHT // 2)
            self.laser_spawn_timer = 0
        
        # Update laser
        if self.space_laser:
            self.space_laser.update()
            if not self.space_laser.active:
                self.space_laser = None
        
        # Spawn boss with warning
        self.boss_spawn_timer += 1
        if self.boss_spawn_timer >= self.boss_spawn_delay and self.boss is None:
            # Show boss warning first
            self.boss_warning_timer = self.boss_warning_duration
            self.boss_spawn_timer = 0
        
        # Handle boss warning timer
        if self.boss_warning_timer > 0:
            self.boss_warning_timer -= 1
            if self.boss_warning_timer == 0:
                # Spawn boss after warning (alternate between types)
                if self.boss_type == "grenade":
                    self.boss = GrenadeBoss(SCREEN_WIDTH // 2 - 30, -60)
                    self.boss_type = "bird"  # Next time spawn bird
                else:
                    self.boss = RoboticBirdBoss(SCREEN_WIDTH // 2 - 40, -80)
                    self.boss_type = "grenade"  # Next time spawn grenade
        
        # Update boss
        if self.boss:
            self.boss.update(self.player.x, self.player.y)
            if self.boss.is_off_screen():
                self.boss = None
        
        # Check collisions
        self.check_collisions()
    
    def check_collisions(self):
        """Check for collisions between game objects"""
        # Bullet vs Enemy collisions
        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                if bullet.get_rect().colliderect(enemy.get_rect()):
                    self.bullets.remove(bullet)
                    self.enemies.remove(enemy)
                    self.score += 10
                    break
        
        # Bullet vs Boss collisions
        if self.boss:
            for bullet in self.bullets[:]:
                if bullet.get_rect().colliderect(self.boss.get_rect()):
                    self.bullets.remove(bullet)
                    if self.boss.take_damage():
                        # Boss destroyed
                        self.score += 100  # Big score bonus for boss
                        self.boss = None
                    break
        
        # Update bomb explosion timer
        if self.bomb_explosion_timer > 0:
            self.bomb_explosion_timer -= 1
        
        # Check if player is invulnerable
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= 1
            return  # Skip collision checks if invulnerable
        
        # Player vs Enemy collisions
        for enemy in self.enemies:
            if self.player.get_rect().colliderect(enemy.get_rect()):
                self.lose_life()
                return
        
        # Player vs Enemy Bullet collisions
        for bullet in self.enemy_bullets[:]:
            if self.player.get_rect().colliderect(bullet.get_rect()):
                self.enemy_bullets.remove(bullet)  # Remove the bullet that hit
                self.lose_life()
                return
        
        # Player vs Asteroid collisions
        for asteroid in self.asteroids:
            if self.player.get_rect().colliderect(asteroid.get_rect()):
                self.lose_life()
                return
        
        # Player vs Boss collisions
        if self.boss and self.player.get_rect().colliderect(self.boss.get_rect()):
            self.lose_life()
            return
        
        # Player vs Boss explosion collisions
        if self.boss:
            for explosion_rect in self.boss.get_explosion_rects():
                if self.player.get_rect().colliderect(explosion_rect):
                    self.lose_life()
                    return
        
        # Player vs Laser barrier collisions
        if self.space_laser and self.space_laser.active:
            if self.player.get_rect().colliderect(self.space_laser.get_rect()):
                # Check if player can pass through (in space hole)
                if not self.space_laser.can_pass_through(self.player.get_rect()):
                    self.lose_life()
                    return
    
    def lose_life(self):
        """Handle player losing a life"""
        self.lives -= 1
        if self.lives <= 0:
            self.state = GameState.GAME_OVER
        else:
            # Respawn player
            self.player = Player(SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT - 50, 1)
            self.invulnerable_timer = self.invulnerable_duration
            # Reset bomb for new round
            self.has_bomb = True
            self.bomb_explosion_timer = 0
            # Reset difficulty for new round
            self.difficulty_level = 1
            self.enemy_spawn_delay = self.base_enemy_spawn_delay
            # Clear all bullets and enemies for a fresh start (keep stars)
            self.bullets = []
            self.enemy_bullets = []
            self.enemies = []
            self.asteroids = []
            self.boss = None  # Remove boss on respawn
            self.space_laser = None  # Remove laser on respawn
            self.boss_warning_timer = 0  # Reset warning timer
    
    def activate_bomb(self):
        """Activate atomic bomb to destroy all enemies"""
        if not self.has_bomb:
            return
        
        # Destroy all enemies and enemy bullets
        enemies_destroyed = len(self.enemies)
        self.enemies.clear()
        self.enemy_bullets.clear()
        
        # Award points for destroyed enemies
        self.score += enemies_destroyed * 10
        
        # Start explosion effect
        self.bomb_explosion_timer = self.bomb_explosion_duration
        
        # Player no longer has bomb
        self.has_bomb = False
    
    def draw_bomb_explosion(self):
        """Draw the atomic bomb explosion effect"""
        # Calculate explosion radius based on timer
        progress = 1.0 - (self.bomb_explosion_timer / self.bomb_explosion_duration)
        max_radius = min(SCREEN_WIDTH, SCREEN_HEIGHT) // 2
        current_radius = int(max_radius * progress)
        
        # Draw multiple explosion rings
        for i in range(3):
            ring_radius = current_radius - (i * 20)
            if ring_radius > 0:
                # Create explosion colors (white to yellow to red)
                if i == 0:
                    color = (255, 255, 255)  # White center
                elif i == 1:
                    color = (255, 255, 0)    # Yellow middle
                else:
                    color = (255, 100, 0)    # Orange outer
                
                # Draw explosion ring
                pygame.draw.circle(self.screen, color, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), ring_radius, 3)
    
    def draw_boss_warning(self):
        """Draw boss incoming warning"""
        # Create pulsing effect
        pulse = int(50 * math.sin(self.boss_warning_timer * 0.3))
        
        # Determine boss type for warning
        if self.boss_type == "grenade":
            boss_name = "GRENADE BOSS"
            warning_color = RED
        else:
            boss_name = "ROBOTIC BIRD BOSS"
            warning_color = CYAN
        
        # Draw warning text
        warning_text = self.big_font.render(f"{boss_name} INCOMING!", True, warning_color)
        warning_rect = warning_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - pulse))
        
        # Add background
        bg_rect = warning_rect.inflate(20, 10)
        pygame.draw.rect(self.screen, BLACK, bg_rect)
        pygame.draw.rect(self.screen, warning_color, bg_rect, 3)
        
        self.screen.blit(warning_text, warning_rect)
        
        # Draw countdown
        countdown = (self.boss_warning_timer // 60) + 1
        countdown_text = self.font.render(f"Appearing in {countdown}...", True, YELLOW)
        countdown_rect = countdown_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(countdown_text, countdown_rect)
    
    def draw(self):
        """Draw everything on screen"""
        self.screen.fill(BLACK)
        
        # Draw stars first (background)
        for star in self.stars:
            star.draw(self.screen)
        
        if self.state == GameState.PLAYING:
            # Draw game objects
            # Draw player with invulnerability effect
            if self.invulnerable_timer > 0 and (self.invulnerable_timer // 10) % 2 == 0:
                # Flash effect during invulnerability
                pass  # Don't draw player when flashing
            else:
                self.player.draw(self.screen)
            
            for bullet in self.bullets:
                bullet.draw(self.screen)
            for bullet in self.enemy_bullets:
                bullet.draw(self.screen)
            for enemy in self.enemies:
                enemy.draw(self.screen)
            for asteroid in self.asteroids:
                asteroid.draw(self.screen)
            
            # Draw laser barrier
            if self.space_laser:
                self.space_laser.draw(self.screen)
            
            # Draw boss
            if self.boss:
                self.boss.draw(self.screen)
            
            # Draw boss warning
            if self.boss_warning_timer > 0:
                self.draw_boss_warning()
            
            # Draw bomb explosion effect
            if self.bomb_explosion_timer > 0:
                self.draw_bomb_explosion()
            
            # Draw score, lives, bomb status, and difficulty
            score_text = self.font.render(f"Score: {self.score}", True, WHITE)
            lives_text = self.font.render(f"Lives: {self.lives}", True, WHITE)
            bomb_text = self.font.render(f"Bomb: {'READY' if self.has_bomb else 'USED'}", True, YELLOW if self.has_bomb else RED)
            difficulty_text = self.font.render(f"Level: {self.difficulty_level}", True, CYAN)
            controls_text = self.font.render("Space: Shoot | B: Bomb | H: Hole", True, WHITE)
            self.screen.blit(score_text, (10, 10))
            self.screen.blit(lives_text, (10, 50))
            self.screen.blit(bomb_text, (10, 90))
            self.screen.blit(difficulty_text, (10, 130))
            self.screen.blit(controls_text, (10, 170))
            
        elif self.state == GameState.GAME_OVER:
            # Draw game over screen
            game_over_text = self.big_font.render("GAME OVER", True, RED)
            score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
            lives_text = self.font.render(f"Lives Lost: {3 - self.lives}", True, WHITE)
            restart_text = self.font.render("Press R to Restart", True, WHITE)
            
            # Center the text
            game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
            lives_rect = lives_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
            
            self.screen.blit(game_over_text, game_over_rect)
            self.screen.blit(score_text, score_rect)
            self.screen.blit(lives_text, lives_rect)
            self.screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()
    
    def restart_game(self):
        """Restart the game"""
        self.state = GameState.PLAYING
        self.score = 0
        self.lives = 3
        self.invulnerable_timer = 0
        self.has_bomb = True
        self.bomb_explosion_timer = 0
        self.difficulty_level = 1
        self.enemy_spawn_delay = self.base_enemy_spawn_delay
        self.player = Player(SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT - 50, 1)
        self.bullets = []
        self.enemies = []
        self.enemy_bullets = []
        self.asteroids = []
        self.stars = []
        self.boss = None
        self.boss_type = "grenade"
        self.space_laser = None
        self.enemy_spawn_timer = 0
        self.asteroid_spawn_timer = 0
        self.star_spawn_timer = 0
        self.boss_spawn_timer = 0
        self.laser_spawn_timer = 0
        self.boss_warning_timer = 0
        # Reinitialize starfield
        self.initialize_starfield()
    
    def run(self):
        """Main game loop"""
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
