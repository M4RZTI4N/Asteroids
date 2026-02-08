#i based most of the gameplay mechanics off of the version of asteroids found at https://freeasteroids.org/
import random, pymunk,pygame, math
from itertools import chain
import pymunk.pygame_util

width, height = 800,800

collision_type = {
    "player":0,
    "bullet":1,
    "bad":2,
}

score = 0

def create_bullet():
    bullet_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
    bullet_shape = pymunk.Circle(bullet_body,3)
    bullet_shape.collision_type = collision_type["bullet"]
    bullet_shape.color = pygame.Color("white")
    bullet_shape.sensor = True


    return bullet_body,bullet_shape

def create_asteroid(size):
    asteroid_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
    asteroid_body.angular_velocity = 0.05
    asteroid_shape = pymunk.Circle(asteroid_body,size)
    asteroid_shape.collision_type = collision_type["bad"]
    asteroid_shape.color = pygame.Color("red")
    asteroid_shape.sensor = True

    return asteroid_body,asteroid_shape

def create_saucer(size):
    saucer_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
    saucer_shape = pymunk.Circle(saucer_body,size)
    saucer_shape.collision_type = collision_type["bad"]
    saucer_shape.color = pygame.Color("pink")
    saucer_shape.sensor = True

    return saucer_body,saucer_shape

def create_saucer_bullet():
    bullet_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
    bullet_shape = pymunk.Circle(bullet_body,3)
    bullet_shape.collision_type = collision_type["bad"]
    bullet_shape.color = pygame.Color("white") 
    bullet_shape.sensor = True


    return bullet_body,bullet_shape

def main():
    global score
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    font = pygame.font.SysFont(None,24)
    big_font = pygame.font.SysFont(None,48)
    # clock = pygame.time.Clock()
    running = True
    won =False

    player_img = pygame.image.load("asteroids0.png").convert_alpha()
    player_img = pygame.transform.smoothscale(player_img,(20,20))
    bullet_img = pygame.image.load("asteroids1.png").convert_alpha()
    asteroid_img = pygame.image.load("asteroids2.png").convert_alpha()
    saucer_img = pygame.image.load("saucer.png").convert_alpha()
    big_saucer_img = pygame.image.load("bigsaucer.png").convert_alpha()
    saucer_bullet_img = pygame.image.load("saucer_bullet.png").convert_alpha()

    fire_sound = pygame.mixer.Sound("fire.wav")
    asteroid_sound = pygame.mixer.Sound("asteroid.wav")
    ship_explosion = pygame.mixer.Sound("ship_explosion.wav")
    saucer_explosion = pygame.mixer.Sound("saucer_explo.wav")
    saucer_fire = pygame.mixer.Sound("saucer_fire.wav")

    boom_sprites = []
    for i in range(9):
        boom_sprites.append(pygame.image.load("boom/boom_"+str(i)+".png"))

    space = pymunk.Space() 
    space.gravity = (0.0,0.0)

    player_body = pymunk.Body(10,100)
    player_body.position = 400,400
    
    player_shape = pymunk.Poly(player_body,[(10,0),(-10,-5),(-10,5)])
    player_shape.color = pygame.Color("white")
    player_shape.collision_type = collision_type["player"]

    player_state = "active"
    death_frame = 0
    frame_spacing = 100
    last_frame_start = 0
    booster_on = False
    spawn_immune = True
    spawn_immune_start = pygame.time.get_ticks()
    lives = 3

    # player_debug = pymunk.Circle(player_body,10)
    # player_debug.color = pygame.Color("blue")
    space.add(player_body,player_shape)

    # pymunk.pygame_util.positive_y_is_up = True
    draw_options = pymunk.pygame_util.DrawOptions(screen)
 
    """
    BALANCE STUFF
    """
    player_rotation = 0.1
    player_accel = 0.1
    player_decel = 0.9997
    bullet_vel = 15
    start_asteroid_count = 4
    start_asteroid_size = 40
    min_asteroid_size = 5
    asteroid_vel = 4
    spawn_buffer = 200
    """"""

    active_bullets = []
    bullet_spawns = {}
    can_shoot = True

    active_asteroids = []
    #safe spawn zone
    x_range = list(chain(range(0,width//2 - spawn_buffer),range(width//2 + spawn_buffer,width)))
    y_range = list(chain(range(0,width//2 - spawn_buffer),range(width//2 + spawn_buffer,width)))
    for a in range(start_asteroid_count):
        a_body,a_shape = create_asteroid(start_asteroid_size)
        a_body.position = pymunk.Vec2d(random.choice(x_range),random.choice(y_range))
        a_vel = pymunk.Vec2d(asteroid_vel,0).rotated_degrees(random.randint(0,360))
        a_body.velocity = a_vel
        space.add(a_body,a_shape)
        active_asteroids.append(a_body)

    small_saucers = []
    big_saucers = []
    saucer_bullets = []
    saucer_bullet_spawns = {}
    
    last_saucer_spawn = pygame.time.get_ticks()
    last_saucer_shot = pygame.time.get_ticks()
    saucer_shot_delay = 2000

    """
    INPUT HANDLING
    """
    pygame.key.set_repeat(1,16)
    while running:
        for event in pygame.event.get():
            #handle quit
            if event.type == pygame.QUIT:
                running = False 
            if event.type == pygame.KEYDOWN and event.key in [pygame.K_ESCAPE,pygame.K_q]:
                running = False
            if player_state == "active":
                #rotation
                if event.type == pygame.KEYDOWN and event.key in [pygame.K_a,pygame.K_LEFT]:
                    player_body.angle -= player_rotation
                if event.type == pygame.KEYDOWN and event.key in [pygame.K_d,pygame.K_RIGHT]:
                    player_body.angle += player_rotation
                
                #thrust
                if event.type == pygame.KEYDOWN and event.key in [pygame.K_w,pygame.K_UP]:
                    booster_on = True

                #fire
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    if can_shoot:
                        new_body,new_shape = create_bullet()
                        new_body.position = player_body.position + pymunk.Vec2d(16,0).rotated(player_body.angle)
                        b_vel = pymunk.Vec2d(bullet_vel,0).rotated(player_body.angle)
                        new_body.velocity = b_vel
                        active_bullets.append(new_body)
                        space.add(new_body,new_shape)
                        can_shoot =False
                        bullet_spawns[new_body.id] = pygame.time.get_ticks()
                        pygame.mixer.Sound.play(fire_sound)
                if event.type == pygame.KEYUP and event.key == pygame.K_SPACE: 
                    can_shoot = True  

        if player_state == "active":    
            if not pygame.key.get_pressed()[pygame.K_w] and not pygame.key.get_pressed()[pygame.K_UP]:
                booster_on = False
            if booster_on:
                # print("boost")
                accel_vector = pymunk.Vec2d(player_accel,0).rotated_degrees(player_body.angle)
                player_body.apply_impulse_at_local_point(accel_vector)
            else:
                player_body.velocity *= player_decel
                if player_body.velocity.length < 1:
                    player_body.velocity = pymunk.Vec2d(0,0)
            
            if player_body.velocity.length > 10:
                player_body.velocity = player_body.velocity.scale_to_length(10)

            if player_body.position.x < 0:
                player_body.position = width, player_body.position.y
            if player_body.position.x > width:
                player_body.position = 0, player_body.position.y
            if player_body.position.y < 0:
                player_body.position = player_body.position.x, height
            if player_body.position.y > height:
                player_body.position  = player_body.position.x, 0

        """
        SAUCER SPAWNS N MECHANICS
        """
        if pygame.time.get_ticks() > last_saucer_spawn + 10000:
            if random.random() > 0.5:
                small_body,small_shape = create_saucer(10)
                small_body.position = pymunk.Vec2d(random.randint(0,width),random.randint(0,height))
                small_body.velocity = pymunk.Vec2d(4,0).rotated_degrees(random.randint(0,360))
                print(small_body.velocity)
                space.add(small_body,small_shape)
                small_saucers.append(small_body)
                last_saucer_spawn = pygame.time.get_ticks()
            else:
                big_body,big_shape = create_saucer(20)
                big_body.position = pymunk.Vec2d(random.randint(0,width),random.randint(0,height))
                big_body.velocity = pymunk.Vec2d(2,0).rotated_degrees(random.randint(0,360))
                space.add(big_body,big_shape)
                big_saucers.append(big_body)
                last_saucer_spawn = pygame.time.get_ticks()

        if pygame.time.get_ticks() > last_saucer_shot + saucer_shot_delay:
            last_saucer_shot = pygame.time.get_ticks()
            noise = False
            for small in small_saucers:
                bullet_body,bullet_shape = create_saucer_bullet()
                bullet_body.position = small.position
                bullet_body.velocity = pymunk.Vec2d(bullet_vel,0).rotated((player_body.position-small.position).angle)
                saucer_bullets.append(bullet_body)
                space.add(bullet_body,bullet_shape)
                saucer_bullet_spawns[bullet_body.id] = pygame.time.get_ticks()
                noise = True
            for big in big_saucers:
                bullet_body,bullet_shape = create_saucer_bullet()
                bullet_body.position = big.position
                bullet_body.velocity = pymunk.Vec2d(bullet_vel,0).rotated_degrees(random.randint(0,360))
                saucer_bullets.append(bullet_body)
                space.add(bullet_body,bullet_shape)
                saucer_bullet_spawns[bullet_body.id] = pygame.time.get_ticks()
                noise = True
            
            if noise:
                pygame.mixer.Sound.play(saucer_fire)
        """
        COLLISION
        """
        def shoot_asteroid(arbiter,space,data):
            global score
            nonlocal active_asteroids,small_saucers,big_saucers
            bullet_shape = arbiter.shapes[0]
            collided_shape = arbiter.shapes[1]
            try:
                active_bullets.remove(bullet_shape.body)
            except:
                pass
            space.remove(bullet_shape,bullet_shape.body)
            
            if collided_shape.body in active_asteroids:
                score += (200//collided_shape.radius)
                if collided_shape.radius//2 > min_asteroid_size:
                    for i in range(2):
                        a_body,a_shape = create_asteroid(collided_shape.radius//2)
                        a_body.position = collided_shape.body.position
                        a_vel = collided_shape.body.velocity.rotated_degrees(random.randint(0,360))*1.1
                        a_body.velocity = a_vel
                        space.add(a_body,a_shape)
                        active_asteroids.append(a_body)
                active_asteroids.remove(collided_shape.body)
                space.remove(collided_shape,collided_shape.body)
                pygame.mixer.Sound.play(asteroid_sound)
            if collided_shape.body in small_saucers:
                score += 600
                small_saucers.remove(collided_shape.body)
                space.remove(collided_shape,collided_shape.body)
                pygame.mixer.Sound.play(saucer_explosion)
            if collided_shape.body in big_saucers:
                score += 400
                big_saucers.remove(collided_shape.body)
                space.remove(collided_shape,collided_shape.body)
                pygame.mixer.Sound.play(saucer_explosion)
                

        
        space.on_collision(collision_type["bullet"],collision_type["bad"],begin=shoot_asteroid)

        def hit_player(arbiter,space,data):
            global score
            nonlocal lives, spawn_immune,spawn_immune_start, player_state, death_frame,last_frame_start
            player_shape = arbiter.shapes[0]
            if spawn_immune:
                return
            else:
                player_shape.body.velocity = pymunk.Vec2d(0,0)
                lives -= 1
                player_state = "dead"
                death_frame = 0
                last_frame_start = pygame.time.get_ticks()
                pygame.mixer.Sound.play(ship_explosion)
                
                
                

        space.on_collision(collision_type["player"],collision_type["bad"],begin=hit_player)

        """
        RENDERING
        """
        screen.fill(pygame.Color("black"))

        if player_state == "active":
            rotated_player = pygame.transform.rotate(player_img,-math.degrees(player_body.angle))
        else:
            death_img = boom_sprites[death_frame]
            rotated_player = pygame.transform.rotate(death_img,-math.degrees(player_body.angle))
            if pygame.time.get_ticks() - frame_spacing > last_frame_start:
                death_frame += 1
                last_frame_start = pygame.time.get_ticks()
                if death_frame >= len(boom_sprites):
                    player_state = "active"
                    spawn_immune = True
                    spawn_immune_start = pygame.time.get_ticks()
                    player_shape.body.position = width//2,height//2
                    player_shape.body.velocity = pymunk.Vec2d(0,0)
            
            
        
        player_rect = rotated_player.get_rect()
        player_rect.center = player_body.position
        screen.blit(rotated_player,player_rect)

        if spawn_immune:
            pygame.draw.circle(screen,pygame.Color("white"),player_rect.center,20,1)

        if pygame.time.get_ticks() - spawn_immune_start > 1000:
            spawn_immune = False

        current_time = pygame.time.get_ticks()
        for bullet in active_bullets:
            if current_time - bullet_spawns[bullet.id] > 1000:
                active_bullets.remove(bullet)
                [b_shape] = bullet.shapes
                space.remove(b_shape,bullet)
                continue

            if bullet.position.x < 0:
                bullet.position = width, bullet.position.y
            if bullet.position.x > width:
                bullet.position = 0, bullet.position.y
            if bullet.position.y < 0:
                bullet.position = bullet.position.x, height
            if bullet.position.y > height:
                bullet.position  = bullet.position.x, 0

            rotated_bullet = pygame.transform.rotate(bullet_img,-math.degrees(bullet.angle))
        
            bullet_rect = rotated_bullet.get_rect()
            bullet_rect.center = bullet.position
            screen.blit(rotated_bullet,bullet_rect)

        for bullet in saucer_bullets:
            if current_time - saucer_bullet_spawns[bullet.id] > 1000:
                saucer_bullets.remove(bullet)
                [b_shape] = bullet.shapes
                space.remove(b_shape,bullet)
                continue

            if bullet.position.x < 0:
                bullet.position = width, bullet.position.y
            if bullet.position.x > width:
                bullet.position = 0, bullet.position.y
            if bullet.position.y < 0:
                bullet.position = bullet.position.x, height
            if bullet.position.y > height:
                bullet.position  = bullet.position.x, 0

            rotated_bullet = pygame.transform.rotate(saucer_bullet_img,-math.degrees(bullet.angle))
        
            bullet_rect = rotated_bullet.get_rect()
            bullet_rect.center = bullet.position
            screen.blit(rotated_bullet,bullet_rect)

        for asteroid in active_asteroids:
            if asteroid.position.x < 0:
                asteroid.position = width, asteroid.position.y
            if asteroid.position.x > width:
                asteroid.position = 0, asteroid.position.y
            if asteroid.position.y < 0:
                asteroid.position = asteroid.position.x, height
            if asteroid.position.y > height:
                asteroid.position  = asteroid.position.x, 0

            [a_shape] = asteroid.shapes
            scaled_asteroid = pygame.transform.smoothscale(asteroid_img,(a_shape.radius*2,a_shape.radius*2))
            rotated_asteroid = pygame.transform.rotate(scaled_asteroid,-math.degrees(asteroid.angle))
        
            asteroid_rect = rotated_asteroid.get_rect()
            asteroid_rect.center = asteroid.position
            screen.blit(rotated_asteroid,asteroid_rect)

        for saucer in small_saucers:
            if saucer.position.x < 0:
                saucer.position = width,saucer.position.y
            if saucer.position.x > width:
                saucer.position = 0,saucer.position.y
            if saucer.position.y < 0:
                saucer.position = saucer.position.x,height
            if saucer.position.x > height:
                saucer.position = saucer.position.x,0

            [saucer_shape] = saucer.shapes
            scaled_saucer = pygame.transform.smoothscale(saucer_img,(saucer_shape.radius*2,saucer_shape.radius*2))

            saucer_rect = scaled_saucer.get_rect()
            saucer_rect.center = saucer.position
            screen.blit(scaled_saucer,saucer_rect)

        for saucer in big_saucers:
            if saucer.position.x < 0:
                saucer.position = width,saucer.position.y
            if saucer.position.x > width:
                saucer.position = 0,saucer.position.y
            if saucer.position.y < 0:
                saucer.position = saucer.position.x,height
            if saucer.position.x > height:
                saucer.position = saucer.position.x,0

            [saucer_shape] = saucer.shapes
            scaled_saucer = pygame.transform.smoothscale(big_saucer_img,(saucer_shape.radius*2,saucer_shape.radius*2))

            saucer_rect = scaled_saucer.get_rect()
            saucer_rect.center = saucer.position
            screen.blit(scaled_saucer,saucer_rect)

        text = font.render(f'score: {int(score)}',True, (255,255,255))
        text_rect = text.get_rect()
        text_rect.center = (80,20)
        screen.blit(text,text_rect)

        l_text = font.render(f'lives: ' + "#"*lives,True, (255,255,255))
        l_text_rect = l_text.get_rect()
        l_text_rect.center = (80,50)
        screen.blit(l_text,l_text_rect)

        space.step(1.0/60)
        pygame.display.flip()

        if lives < 0:
            running = False
            won = False
        if len(active_asteroids) <= 0 and len(small_saucers) <= 0 and len(big_saucers) <= 0:
            running = False
            won = True
    """
    game over
    """
    quit_end = False

    while not quit_end:

        screen.fill(pygame.Color("black"))

        title_text = big_font.render("GAME OVER",True,(255,255,255))
        title_text_rect = title_text.get_rect()
        title_text_rect.center = (width/2,height//3)
        screen.blit(title_text,title_text_rect)

        score_text = font.render(f'score: {int(score)}',True,(255,255,255))
        score_text_rect = score_text.get_rect()
        score_text_rect.center = (width/2,height//3+40)
        screen.blit(score_text,score_text_rect)

        if won:
            win_text = font.render('YOU WON!!!!!!!!',True,(0,127,0))
            win_text_rect = win_text.get_rect()
            win_text_rect.center = (width/2,2*(height//3))
            screen.blit(win_text,win_text_rect)

        quit_text = font.render("esc or q to quit",True,(180,180,180))
        quit_text_rect = quit_text.get_rect()
        quit_text_rect.center = (width//2,2*(height//3)+40)
        screen.blit(quit_text,quit_text_rect)
        
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_end = True
            if event.type == pygame.KEYDOWN and event.key in [pygame.K_ESCAPE,pygame.K_q]:
                quit_end = True

if __name__ == "__main__":
    main()