import pygame.locals
from settings import *
from player import Player
from enemy import *
from sprites import *
from groups import Groups
from pytmx.util_pygame import load_pygame

from random import choice

class Game:
    def __init__(self):
        # setup
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))
        pygame.display.set_caption('survivor')
        self.clock = pygame.time.Clock()
        self.runnig = True
        
        # groups 
        self.all_sprites = Groups()
        self.collision_sprites = pygame.sprite.Group()
        self.dangarea_sprites = pygame.sprite.Group()
        self.healtharea_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        
        # gun timer 
        self.can_shoot = True
        self.shoot_time = 0
        self.gun_cooldown = 150
        
        # enemy timer
        self.enemy_event = pygame.event.custom_type()
        pygame.time.set_timer(self.enemy_event, 5000)
        self.spawn_positions = []

        
        # audio
        self.shoot_sound = pygame.mixer.Sound(join('audio','shoot.wav'))
        self.shoot_sound.set_volume(0.4)
        self.impact_sound = pygame.mixer.Sound(join('audio','impact.ogg'))
        # self.music_sound = pygame.mixer.Sound(join('audio','music.wav'))
        # self.music_sound.set_volume(0.3)
        # self.music_sound.play(loops=-1)

        # player health setting
        self.damage_cooldown = 1200  # 1 second cooldown between damage
        self.last_damage_time = 0  # Track last damage time


        # setup
        self.load_images()
        self.setup()

    def load_images(self):
        self.bullet_surf = pygame.image.load(join('images','gun','bullet.png')).convert_alpha()
        
        folders = list(walk(join('images','enemies')))[0][1]
        self.enemy_frames = {}
        self.air_enemy_frames = {}
        for folder in folders:
            for folder_path, _, file_names in walk(join('images','enemies',folder)):
                if folder == 'bat':
                    self.air_enemy_frames[folder] = []
                    for file_name in sorted(file_names, key= lambda name: int(name.split('.')[0])):
                        full_path = join(folder_path,file_name)
                        surf = pygame.image.load(full_path).convert_alpha()
                        self.air_enemy_frames[folder].append(surf)
                else:
                    self.enemy_frames[folder] = []
                    for file_name in sorted(file_names, key= lambda name: int(name.split('.')[0])):
                        full_path = join(folder_path,file_name)
                        surf = pygame.image.load(full_path).convert_alpha()
                        self.enemy_frames[folder].append(surf)

    def input(self):
        if pygame.mouse.get_pressed()[0] and self.can_shoot:
            self.shoot_sound.play()
            pos = self.gun.rect.center + self.gun.player_direction * 50
            Bullet(self.bullet_surf, pos, self.gun.player_direction,(self.all_sprites,self.bullet_sprites))
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()
    
    def gun_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time >= self.gun_cooldown:
                self.can_shoot = True
    
    def create_grid_from_sprites(self):
        # Initialize an empty grid of 0s (all cells are passable initially)
        grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
        # Mark collision sprites as blocked (1) in the grid
        for sprite in self.collision_sprites:
            # Calculate the top-left and bottom-right corners in grid coordinates
            start_x = int(sprite.rect.left // TILE_SIZE)
            start_y = int(sprite.rect.top // TILE_SIZE)
            end_x = int(sprite.rect.right // TILE_SIZE)
            end_y = int(sprite.rect.bottom // TILE_SIZE)
            
            # Loop through each grid cell the sprite covers
            for x in range(start_x, end_x + 1):
                for y in range(start_y, end_y + 1):
                    if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                        grid[y][x] = 1  # Block the grid cell

        # Mark danger area sprites as danger (2) in the grid
        for sprite in self.dangarea_sprites:
            start_x = int(sprite.rect.left // TILE_SIZE)
            start_y = int(sprite.rect.top // TILE_SIZE)
            end_x = int(sprite.rect.right // TILE_SIZE)
            end_y = int(sprite.rect.bottom // TILE_SIZE)
            
            for x in range(start_x, end_x + 1):
                for y in range(start_y, end_y + 1):
                    if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT and grid[y][x] != 1:
                        grid[y][x] = 2  # Mark as a danger zone
        
        # print(grid)
        return grid


    
    def setup(self):
        # self.grid = self.create_grid_from_sprites(self.collision_sprites, self.dangarea_sprites, self.GRID_WIDTH, self.GRID_HEIGHT, self.cell_size)  # Game map grid
        
        map = load_pygame(join('data','maps','world.tmx'))
        for x,y,image in map.get_layer_by_name('Ground').tiles():
            Sprite((x*TILE_SIZE, y*TILE_SIZE), image, self.all_sprites)
        
        for obj in map.get_layer_by_name('Objects'):
            CollisionSprite((obj.x, obj.y), obj.image, (self.all_sprites,self.collision_sprites))
        
        for obj in map.get_layer_by_name('Collisions'):
            if obj.name == 'dangarea':
                CollisionSprite((obj.x, obj.y), pygame.Surface((obj.width,obj.height)), self.dangarea_sprites)
                # CollisionSprite((obj.x, obj.y), pygame.Surface((obj.width,obj.height)), (self.all_sprites,self.dangarea_sprites))
            else: 
                if obj.name == 'healtharea':
                    CollisionSprite((obj.x, obj.y), pygame.Surface((obj.width,obj.height)), self.healtharea_sprites)
                    # CollisionSprite((obj.x, obj.y), pygame.Surface((obj.width,obj.height)), (self.all_sprites,self.collision_sprites))
                else:
                    CollisionSprite((obj.x, obj.y), pygame.Surface((obj.width,obj.height)), self.collision_sprites)
                    
                
        for obj in map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player((obj.x,obj.y),self.all_sprites,self.collision_sprites)
                self.gun = Gun(self.player,self.all_sprites)
                self.hp_bar = HPBar(self.player,self.all_sprites)
            else:
                self.spawn_positions.append((obj.x, obj.y))
                
        self.grid = self.create_grid_from_sprites()  # Game map grid
            
    def bullet_collision(self):
        if self.bullet_sprites:
            for bullet in self.bullet_sprites:
                collision_sprites = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask)   
                if collision_sprites:
                    self.impact_sound.play()
                    for sprite in collision_sprites:
                        sprite.destroy() 
                    bullet.kill()
    
                
    def player_collision(self):
        if pygame.sprite.spritecollide(self.player, self.enemy_sprites, True, pygame.sprite.collide_mask):
            self.impact_sound.play()
            self.player.current_hp -= 20  # Example damage value
            
        if pygame.sprite.spritecollide(self.player, self.healtharea_sprites, False,pygame.sprite.collide_mask):
            self.player.current_hp = self.player.max_hp  # Example damage value

        # Check for dangerous area collision
        current_time = pygame.time.get_ticks()
        if pygame.sprite.spritecollide(self.player, self.dangarea_sprites, False,pygame.sprite.collide_mask):
            if current_time - self.last_damage_time > self.damage_cooldown:
                self.player.current_hp -= 10  # Reduce health by 10 (adjust as needed)
                self.last_damage_time = current_time  # Update the last damage time
                self.impact_sound.play()
                
        if self.player.current_hp <= 0:
            self.runnig = False  # End the game when health reaches         
    
    
    def run(self):
        while self.runnig:
            # dt
            dt = self.clock.tick() / 1000
            
            # event loop 
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.runnig = False
                if event.type == self.enemy_event:
                    choice((Enemy(
                        pos=choice(self.spawn_positions), 
                        frames= choice(list(self.enemy_frames.values())),  
                        groups=(self.all_sprites, self.enemy_sprites),  
                        player=self.player,  
                        collision_sprites=self.collision_sprites, 
                        grid=self.grid, 
                        inAir=False
                    ),
                    Enemy(
                        pos=choice(self.spawn_positions), 
                        frames= choice(list(self.air_enemy_frames.values())),  
                        groups=(self.all_sprites, self.enemy_sprites),  
                        player=self.player,  
                        collision_sprites=self.collision_sprites, 
                        grid=self.grid, 
                        inAir=True
                    )
                    ))
                    
                # Enemy(choice(self.spawn_positions),choice(list(self.enemy_frames.values())), (self.all_sprites, self.enemy_sprites), self.player, self.collision_sprites)
                    
            # update 
            self.gun_timer()
            self.input()
            self.all_sprites.update(dt)
            self.bullet_collision()
            self.player_collision()
            
            # draw
            self.display_surface.fill('black')
            self.all_sprites.draw(self.player.rect.center)
            # self.player.draw_health_bar(self.display_surface)  # Draw health bar
            pygame.display.flip()
            
        pygame.quit()
        
if __name__ == '__main__':
    game = Game()
    game.run()