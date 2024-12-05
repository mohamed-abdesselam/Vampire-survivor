import heapq
from settings import *

# Define a heuristic function (Manhattan distance)
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])  # Manhattan distance

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, player, collision_sprites, grid, inAir=False):
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
        self.inAir = inAir
        self.death_time = 0
        self.death_duration = 400

    def animate(self, dt):
        self.frames_index += self.animation_speed * dt
        self.image = self.frames[int(self.frames_index) % len(self.frames)]

    def move(self, dt):
        # get direction
        player_pos = pygame.Vector2(self.player.rect.center)
        enemy_pos = pygame.Vector2(self.rect.center)
        self.direction = (player_pos - enemy_pos).normalize()

        # update the rect position + collision
        self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.collision('horizantal')
        self.hitbox_rect.y += self.direction.y * self.speed * dt
        self.collision('vertical')
        self.rect.center = self.hitbox_rect.center

    def collision(self, direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if direction == 'horizantal':
                    if self.direction.x > 0: self.hitbox_rect.right = sprite.rect.left
                    if self.direction.x < 0: self.hitbox_rect.left = sprite.rect.right
                else:
                    if self.direction.y < 0: self.hitbox_rect.top = sprite.rect.bottom
                    if self.direction.y > 0: self.hitbox_rect.bottom = sprite.rect.top

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
        neighbors = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # 4 possible directions: up, down, left, right
        
        for dx, dy in directions:
            x, y = node[0] + dx, node[1] + dy
            if 0 <= x < len(self.grid[0]) and 0 <= y < len(self.grid):
                if self.inAir:  # In air, can pass through danger areas
                    if self.grid[y][x] != 1:  # 1 means obstacle
                        neighbors.append((x, y))
                else:  # Can't move through danger areas
                    if self.grid[y][x] != 1 and self.grid[y][x] != 2:  # 2 means danger
                        neighbors.append((x, y))
        return neighbors

    def a_star(self, start, goal):
        open_set = []
        heapq.heappush(open_set, (0, start))  # Push the start node with priority 0
        g_score = {start: 0}  # Cost from start to current node
        f_score = {start: heuristic(start, goal)}  # Estimated total cost from start to goal
        previous_nodes = {start: None}  # Store the path

        while open_set:
            _, current = heapq.heappop(open_set)  # Get the node with the lowest f_score

            if current == goal:  # If the goal is reached, reconstruct the path
                break

            for neighbor in self.get_neighbors(current):
                tentative_g_score = g_score[current] + 1  # All edges have equal cost (1)

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
                    previous_nodes[neighbor] = current

        # Reconstruct path from goal to start
        path = []
        node = goal
        while node is not None:
            path.append(node)
            node = previous_nodes.get(node)
        self.path = path[::-1]  # Reverse the path to go from start to goal

    def move_along_path(self, dt):
        if self.path:
            next_cell = self.path[0]
            target_pos = pygame.Vector2((next_cell[0]) * self.cell_size, (next_cell[1]) * self.cell_size)
            current_pos = pygame.Vector2(self.rect.center)

            self.direction = (target_pos - current_pos)
            if self.direction:
                self.direction = (target_pos - current_pos).normalize()

            distance = self.direction * self.speed * dt
            self.hitbox_rect.center += distance

            # If close to the next node, move to the next path step
            if current_pos.distance_to(target_pos) < self.speed * dt:
                self.path = self.path[1:]  # Remove the first element of the path

            self.rect.center = self.hitbox_rect.center

    def update(self, dt):
        player_cell = (self.player.rect.centerx // self.cell_size, self.player.rect.centery // self.cell_size)
        enemy_cell = (self.rect.centerx // self.cell_size, self.rect.centery // self.cell_size)

        # Update the path only when the enemy or player moves to a new cell
        if self.player_cell != player_cell or self.enemy_cell != enemy_cell:
            self.player_cell = player_cell
            self.enemy_cell = enemy_cell
            if self.inAir:
                self.a_star(enemy_cell, player_cell)  # Use A* for in-air enemies
            else:
                self.a_star(enemy_cell, player_cell)  # For non-in-air enemies (same behavior)

        if self.death_time == 0:
            self.move_along_path(dt)
            self.animate(dt)
        else:
            self.death_timer()
