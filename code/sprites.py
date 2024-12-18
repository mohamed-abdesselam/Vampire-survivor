from settings import *
from math import atan2,degrees
import heapq

class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, serf, groups):
        super().__init__(groups)
        self.image = serf
        self.rect = self.image.get_frect(topleft = pos)
        self.ground = True   
        
class CollisionSprite(pygame.sprite.Sprite):
    def __init__(self, pos, serf, groups):
        super().__init__(groups)
        self.image = serf
        self.rect = self.image.get_frect(topleft = pos)
    
class HPBar(pygame.sprite.Sprite):
    def __init__(self, player, groups):
        super().__init__(groups)
        self.player = player  # Link to the player object
        
        # Health bar settings
        self.bar_width = 100
        self.bar_height = 10
        self.border_color = (255, 255, 255)  # White border
        self.background_color = (50, 50, 50)  # Dark gray background
        self.health_color = (255, 0, 0)  # Red for health
        
        # Create a surface for the health bar
        self.image = pygame.Surface((self.bar_width, self.bar_height))
        self.rect = self.image.get_rect()
    
    def update(self, _):
        # Update position below the player
        self.rect.centerx = self.player.rect.centerx
        self.rect.centery = self.player.rect.bottom + 15  # 15 pixels below the player
        
        # Calculate health ratio
        health_ratio = self.player.current_hp / self.player.max_hp
        
        # Clear the health bar surface
        self.image.fill(self.background_color)  # Fill with background color
        
        # Draw the health portion
        health_width = int(self.bar_width * health_ratio)
        pygame.draw.rect(self.image, self.health_color, (0, 0, health_width, self.bar_height))
        
        # Draw border
        pygame.draw.rect(self.image, self.border_color, (0, 0, self.bar_width, self.bar_height), 2)
          
class Gun(pygame.sprite.Sprite):
    def __init__(self,player,groups):
        # player connection
        self.player = player
        self.distance = 140
        self.player_direction = pygame.Vector2(1,0)
        
        # sprite setup
        super().__init__(groups)
        self.gun_surf = pygame.image.load(join('images','gun','gun.png')).convert_alpha()
        self.image = self.gun_surf
        self.rect = self.image.get_frect(center = self.player.rect.center + self.player_direction * self.distance)
        
    def get_directoin(self):
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        player_pos = pygame.Vector2(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        self.player_direction = (mouse_pos - player_pos).normalize()
        
    def rotate_gun(self):
        angle = degrees(atan2(self.player_direction.x, self.player_direction.y)) - 90
        if self.player_direction.x > 0:
            self.image = pygame.transform.rotozoom(self.gun_surf, angle, 1)
        else:
            self.image = pygame.transform.rotozoom(self.gun_surf, abs(angle), 1)
            self.image = pygame.transform.flip(self.image,False,True)
        
    def update(self , _):
        self.get_directoin()
        self.rotate_gun()
        self.rect.center = self.player.rect.center + self.player_direction * self.distance
        
class Bullet(pygame.sprite.Sprite):
    def __init__(self,surf,pos,direction,groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = pos)      
        self.spawm_time = pygame.time.get_ticks()
        self.lifetime = 1000
        
        self.direction = direction
        self.speed = 1200
        
    def update(self,dt):
        self.rect.center += self.direction * self.speed * dt    
        
        if pygame.time.get_ticks() - self.spawm_time >= self.lifetime:
            self.kill()
    
class Enemydsa(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, player, collision_sprites):
        super().__init__(groups)
        self.player = player 
        
        # image
        self.frames, self.frames_index = frames , 0
        self.image = self.frames[self.frames_index]  
        self.animation_spedd = 6 

        # rect 
        self.rect = self.image.get_frect(center = pos)
        self.hitbox_rect = self.rect.inflate(-20,-40)
        self.collision_sprites = collision_sprites
        self.direction = pygame.Vector2()
        self.spedd = 350
        
        # timer
        self.death_time = 0
        self.death_duration = 400        
        
    def animate(self,dt):
        self.frames_index += self.animation_spedd * dt
        self.image = self.frames[int(self.frames_index) % len(self.frames)]
        
    def move(self,dt):
        # get direction
        player_pos = pygame.Vector2(self.player.rect.center)
        enemy_pos = pygame.Vector2(self.rect.center)
        self.direction = (player_pos - enemy_pos).normalize()
        
        # update the rect postion + collision
        self.hitbox_rect.x += self.direction.x * self.spedd * dt
        self.collision('horizantal')
        self.hitbox_rect.y += self.direction.y * self.spedd * dt
        self.collision('vertical')
        self.rect.center = self.hitbox_rect.center
    
    def collision(self,direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if direction == 'horizantal':
                    if self.direction.x > 0 : self.hitbox_rect.right = sprite.rect.left
                    if self.direction.x < 0 : self.hitbox_rect.left = sprite.rect.right
                else:
                    if self.direction.y < 0 : self.hitbox_rect.top = sprite.rect.bottom
                    if self.direction.y > 0 : self.hitbox_rect.bottom = sprite.rect.top
    
    def destroy(self):
        # start timer
        self.death_time = pygame.time.get_ticks()
        
        # change image
        surf = pygame.mask.from_surface(self.frames[0]).to_surface()
        surf.set_colorkey('black')
        self.image = surf
        
    def death_timer(self):
        if pygame.time.get_ticks() - self.death_time >= self.death_duration:
            self.kill()
                
    def update(self,dt):
        if self.death_time == 0:
            self.move(dt)
            self.animate(dt)
        else:
            self.death_timer()  
            
            
