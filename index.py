import random, pymunk,pygame
import pymunk.pygame_util

width, height = 800,800



def main():
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()
    running = True


    space = pymunk.Space() 
    space.gravity = (0.0,0.0)

    player_body = pymunk.Body(10,100)
    player_body.position = 400,400
    
    player_shape = pymunk.Poly(player_body,[(10,0),(-10,-5),(-10,5)])
    player_shape.color = pygame.Color("white")

    booster_on = False

    # player_debug = pymunk.Circle(player_body,10)
    # player_debug.color = pygame.Color("blue")
    space.add(player_body,player_shape)

    pymunk.pygame_util.positive_y_is_up = True
    draw_options = pymunk.pygame_util.DrawOptions(screen)
 
    """
    BALANCE STUFF
    """
    player_rotation = -0.2
    player_accel = 0.1
    player_decel = 0.9997

    pygame.key.set_repeat(1,16)
    while running:
        for event in pygame.event.get():
            #handle quit
            if event.type == pygame.QUIT:
                running = False 
            if event.type == pygame.KEYDOWN and event.key in [pygame.K_ESCAPE,pygame.K_q]:
                running = False

            #rotation
            if event.type == pygame.KEYDOWN and event.key in [pygame.K_a,pygame.K_LEFT]:
                player_body.angle -= player_rotation
            if event.type == pygame.KEYDOWN and event.key in [pygame.K_d,pygame.K_RIGHT]:
                player_body.angle += player_rotation
            
            #thrust
            if event.type == pygame.KEYDOWN and event.key in [pygame.K_w,pygame.K_UP]:
                booster_on = True
            
        if not pygame.key.get_pressed()[pygame.K_w] and not pygame.key.get_pressed()[pygame.K_UP]:
            booster_on = False
        if booster_on:
            # print("boost")
            accel_vector = pymunk.Vec2d(player_accel,0).rotated_degrees(player_body.angle)
            player_body.apply_impulse_at_local_point(accel_vector)
        else:
            player_body.velocity *= player_decel
        
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
        screen.fill(pygame.Color("black"))
        space.debug_draw(draw_options)

        space.step(1.0/60)
        pygame.display.flip()


if __name__ == "__main__":
    main()