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

    player_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
    player_body.position = 400,400
    
    player_shape = pymunk.Poly(player_body,[(10,0),(-10,-10),(-10,10)])
    player_shape.color = pygame.Color("white")

    # player_debug = pymunk.Circle(player_body,10)
    # player_debug.color = pygame.Color("blue")

    

    space.add(player_body,player_shape)

    pymunk.pygame_util.positive_y_is_up = True
    draw_options = pymunk.pygame_util.DrawOptions(screen)


    

    while running:
        for event in pygame.event.get():

            #handle quit
            if event.type == pygame.QUIT:
                running = False 
            elif event.type == pygame.KEYDOWN and event.key in [pygame.K_ESCAPE,pygame.K_q]:
                running = False

            
            

        screen.fill(pygame.Color("black"))
        space.debug_draw(draw_options)

        space.step(1.0/60)
        pygame.display.flip()


if __name__ == "__main__":
    main()