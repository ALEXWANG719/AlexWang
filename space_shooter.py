import pygame
import random
import sys
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
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 5
        
        # Load player sprite
        try:
            self.sprite = pygame.image.load("Pasted Graphic-1.png")
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
            # Draw the loaded sprite
            screen.blit(self.sprite, (self.x, self.y))
        else:
            # Fallback to simple pixel-style spaceship
            pygame.draw.polygon(screen, CYAN, [
                (self.x + self.width // 2, self.y),  # Top point
                (self.x, self.y + self.height),      # Bottom left
                (self.x + self.width // 4, self.y + self.height * 0.7),  # Left wing
                (self.x + self.width * 3 // 4, self.y + self.height * 0.7),  # Right wing
                (self.x + self.width, self.y + self.height)  # Bottom right
            ])
            # Ship body
            pygame.draw.rect(screen, BLUE, (self.x + self.width // 3, self.y + self.height // 3, 
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

class Enemy:
    """Enemy spaceship class"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = random.uniform(1, 3)
        self.shoot_timer = 0
        self.shoot_delay = random.randint(60, 120)  # Random shooting delay
        
        # Load enemy sprite
        try:
            self.sprite = pygame.image.load("Pasted Graphic 2.png")
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
        
        # Game objects
        self.player = Player(SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT - 50)
        self.bullets = []
        self.enemies = []
        self.enemy_bullets = []
        self.asteroids = []
        self.stars = []
        
        # Spawning timers
        self.enemy_spawn_timer = 0
        self.enemy_spawn_delay = 60  # frames
        self.asteroid_spawn_timer = 0
        self.asteroid_spawn_delay = 120  # frames
        self.star_spawn_timer = 0
        self.star_spawn_delay = 2  # frames (spawn stars frequently)
        
        # Initialize starfield
        self.initialize_starfield()
    
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
                if event.key == pygame.K_SPACE and self.state == GameState.PLAYING:
                    # Shoot bullet
                    bullet = Bullet(self.player.x + self.player.width // 2 - 2, self.player.y)
                    self.bullets.append(bullet)
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
            enemy = Enemy(random.randint(0, SCREEN_WIDTH - 30), -25)
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
    
    def lose_life(self):
        """Handle player losing a life"""
        self.lives -= 1
        if self.lives <= 0:
            self.state = GameState.GAME_OVER
        else:
            # Respawn player
            self.player = Player(SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT - 50)
            self.invulnerable_timer = self.invulnerable_duration
            # Clear all bullets and enemies for a fresh start (keep stars)
            self.bullets = []
            self.enemy_bullets = []
            self.enemies = []
            self.asteroids = []
    
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
            
            # Draw score and lives
            score_text = self.font.render(f"Score: {self.score}", True, WHITE)
            lives_text = self.font.render(f"Lives: {self.lives}", True, WHITE)
            self.screen.blit(score_text, (10, 10))
            self.screen.blit(lives_text, (10, 50))
            
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
        self.player = Player(SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT - 50)
        self.bullets = []
        self.enemies = []
        self.enemy_bullets = []
        self.asteroids = []
        self.stars = []
        self.enemy_spawn_timer = 0
        self.asteroid_spawn_timer = 0
        self.star_spawn_timer = 0
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
