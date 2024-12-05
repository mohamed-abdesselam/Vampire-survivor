from settings import *
import heapq

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, player, collision_sprites, grid):
        super().__init__(groups)
        self.player = player
        self.player_cell = pygame.Vector2()
        self.frames, self.frames_index = frames, 0
        self.image = self.frames[self.frames_index]
        self.animation_speed = 6
        self.rect = self.image.get_rect(center=pos)
        self.hitbox_rect = self.rect.inflate(-20, -40)
        self.collision_sprites = collision_sprites
        self.direction = pygame.Vector2()
        self.speed = 350
        self.grid = grid  # Game map grid
        self.cell_size = TILE_SIZE  # Size of each grid cell
        self.path = []  # Store the path to follow
        
#         # Death timer
        self.death_time = 0
        self.death_duration = 400
        
                
    def animate(self,dt):
        self.frames_index += self.animation_speed * dt
        self.image = self.frames[int(self.frames_index) % len(self.frames)]
        
    def move(self,dt):
        # get direction
        player_pos = pygame.Vector2(self.player.rect.center)
        enemy_pos = pygame.Vector2(self.rect.center)
        self.direction = (player_pos - enemy_pos).normalize()
        
        # update the rect postion + collision
        self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.collision('horizantal')
        self.hitbox_rect.y += self.direction.y * self.speed * dt
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

    def get_neighbors(self, node):
        # Example of getting neighbors in 4 directions (up, down, left, right)
        neighbors = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for dx, dy in directions:
            x, y = node[0] + dx, node[1] + dy
            if 0 <= x < len(self.grid[0]) and 0 <= y < len(self.grid) and self.grid[y][x] != 1:  # Assuming 1 is obstacle
                neighbors.append((x, y))
        return neighbors

    def dijkstra(self, start, goal):
        queue = [(0, start)]
        distances = {start: 0}
        previous_nodes = {start: None}
        visited = set()

        while queue:
            current_distance, current_node = heapq.heappop(queue)
            if current_node in visited:
                continue
            visited.add(current_node)

            if current_node == goal:
                break

            for neighbor in self.get_neighbors(current_node):
                new_distance = current_distance + 1
                if neighbor not in distances or new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    previous_nodes[neighbor] = current_node
                    heapq.heappush(queue, (new_distance, neighbor))

        # Reconstruct path
        path = []
        node = goal
        while node is not None:
            path.append(node)
            node = previous_nodes.get(node)
        self.path = path[::-1]  # Reverse path

    def move_along_path(self, dt):
        # print(self.path)
        if self.path:
            next_cell = self.path[0]
            target_pos = pygame.Vector2((next_cell[0]) * self.cell_size, (next_cell[1]) * self.cell_size)
            current_pos = pygame.Vector2(self.rect.center)

            self.direction = (target_pos - current_pos)
            if self.direction:
                self.direction = self.direction.normalize()
                
            distance = self.direction * self.speed * dt
            self.hitbox_rect.center += distance

            # If close to the next node, move to the next path step
            if current_pos.distance_to(target_pos) < self.speed * dt:
                self.path = self.path[1:]  # Slices the list to remove the first element
                
            self.rect.center = self.hitbox_rect.center

    def update(self, dt):
        player_cell = (self.player.rect.centerx // self.cell_size, self.player.rect.centery // self.cell_size)
        enemy_cell = (self.rect.centerx // self.cell_size, self.rect.centery // self.cell_size)

        if self.player_cell != player_cell:
            self.player_cell = player_cell
            self.dijkstra(enemy_cell, player_cell)  # Calculate path
        
        if self.death_time == 0:
            self.move_along_path(dt)
            # self.move(dt)
            self.animate(dt)
        else:
            self.death_timer()







# class GridNode:
#     def __init__(self, x, y, width, height, walkable):
#         self.rect = pygame.Rect(x, y, width, height) 
#         self.center = self.rect.center
#         self.walkable = walkable
#         self.row = 0
#         self.col = 0

#     def __lt__(self, other):  # For heapq comparison
#         return self.center < other.center

# class Enemy(pygame.sprite.Sprite):
#     def __init__(self, pos, frames, groups, player, collision_sprites):
#         super().__init__(groups)
#         self.player = player
#         self.frames, self.frames_index = frames, 0
#         self.image = self.frames[self.frames_index]
#         self.animation_speed = 6

#         # Rect and collision
#         self.rect = self.image.get_rect(center=pos)
#         self.hitbox_rect = self.rect.inflate(-20, -40)
#         self.collision_sprites = collision_sprites
#         self.direction = pygame.Vector2()
#         self.speed = 350

#         # Dijkstra related variables
#         self.grid_width = GRID_WIDTH
#         self.grid_height = GRID_HEIGHT
#         self.tile_size = TILE_SIZE
#         self.map_grid = self.create_grid()
#         # print(self.map_grid)
#         self.path = []
#         self.current_node = None
#         self.target_node = None

#         # Death timer
#         self.death_time = 0
#         self.death_duration = 400

#     def animate(self, dt):
#         self.frames_index += self.animation_speed * dt
#         self.image = self.frames[int(self.frames_index) % len(self.frames)]

#     def create_grid(self):
#         # Initialize an empty grid of 0s (all cells are passable initially)
#         grid = [[0 for _ in range(self.grid_width)] for _ in range(self.grid_height)]

#         # Mark collision sprites as blocked (1) in the grid
#         for sprite in self.collision_sprites:
#             grid_x = round(sprite.rect.centerx // self.tile_size)
#             grid_y = round(sprite.rect.centery // self.tile_size)
#             if 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height:
#                 # Mark the center grid cell as blocked
#                 grid[grid_y][grid_x] = 1

#                 # Optionally, mark surrounding cells as partially blocked (e.g., 0.5)
#                 # for dx in range(-1, 2):
#                 #     for dy in range(-1, 2):
#                 #         nx = grid_x + dx
#                 #         ny = grid_y + dy
#                 #         if 0 <= nx < self.grid_width and 0 <= ny < self.grid_height:
#                 #             grid[ny][nx] = 0.5 

#         # Create GridNode objects from the grid data
#         map_grid = []
#         for y in range(self.grid_height):
#             row = []
#             for x in range(self.grid_width):
#                 walkable = True if grid[y][x] == 0 else False
#                 node = GridNode(x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size, walkable) 
#                 node.row, node.col = y, x
#                 row.append(node)
#             map_grid.append(row)

#         return map_grid

#     def find_path(self):
#         start_node = self.get_grid_node(self.rect.center)
#         end_node = self.get_grid_node(self.player.rect.center)

#         if start_node is None or end_node is None:
#             return

#         open_set = []
#         heapq.heappush(open_set, (0, start_node))
#         came_from = {}
#         g_score = {node: float('inf') for row in self.map_grid for node in row}
#         g_score[start_node] = 0

#         while open_set:
#             current = heapq.heappop(open_set)[1]

#             if current == end_node:
#                 path = []
#                 while current in came_from:
#                     path.insert(0, current)
#                     current = came_from[current]
#                 self.path = path
#                 return

#             for neighbor in self.get_neighbors(current):
#                 tentative_g_score = g_score[current] + 1  # Cost per grid cell

#                 if tentative_g_score < g_score[neighbor]:
#                     came_from[neighbor] = current
#                     g_score[neighbor] = tentative_g_score
#                     heapq.heappush(open_set, (g_score[neighbor], neighbor))

#     def get_grid_node(self, position):
#         # grid_x = int(position[0] // self.map_grid[0][0].width)
#         # grid_y = int(position[1] // self.map_grid[0][0].height)
#         grid_x = int(position[0] // self.tile_size)
#         grid_y = int(position[1] // self.tile_size)
#         try:
#             return self.map_grid[grid_y][grid_x]
#         except IndexError:
#             return None

#     def get_neighbors(self, node):
#         neighbors = []
#         row, col = node.row, node.col
#         for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  # Check up, right, down, left
#             new_row, new_col = row + dr, col + dc
#             if 0 <= new_row < len(self.map_grid) and 0 <= new_col < len(self.map_grid[0]):
#                 neighbor = self.map_grid[new_row][new_col]
#                 if neighbor.walkable:
#                     neighbors.append(neighbor)
#         return neighbors

#     def move(self, dt):
#         if self.path:
#             self.current_node = self.path[0]
#             target_pos = self.current_node.center
#             self.direction = (pygame.Vector2(target_pos) - pygame.Vector2(self.rect.center)).
#             # self.direction = (pygame.Vector2(target_pos) - pygame.Vector2(self.rect.center)).normalize()

#             self.hitbox_rect.x += self.direction.x * self.speed * dt
#             self.collision('horizontal')
#             self.hitbox_rect.y += self.direction.y * self.speed * dt
#             self.collision('vertical')

#             if self.rect.centerx == target_pos[0] and self.rect.centery == target_pos[1]:
#                 self.path.pop(0)
#         else:
#             self.find_path()

#         self.rect.center = self.hitbox_rect.center

#     def collision(self, direction):
#         for sprite in self.collision_sprites:
#             if sprite.rect.colliderect(self.hitbox_rect):
#                 if direction == 'horizontal':
#                     if self.direction.x > 0: self.hitbox_rect.right = sprite.rect.left
#                     if self.direction.x < 0: self.hitbox_rect.left = sprite.rect.right
#                 else:
#                     if self.direction.y < 0: self.hitbox_rect.top = sprite.rect.bottom
#                     if self.direction.y > 0: self.hitbox_rect.bottom = sprite.rect.top

#     def destroy(self):
#         self.death_time = pygame.time.get_ticks()
#         surf = pygame.mask.from_surface(self.frames[0]).to_surface()
#         surf.set_colorkey('black')
#         self.image = surf

#     def death_timer(self):
#         if pygame.time.get_ticks() - self.death_time >= self.death_duration:
#             self.kill()

#     def update(self, dt):
#         if self.death_time == 0:
#             self.move(dt)
#             self.animate(dt)
#         else:
#             self.death_timer()