import pygame, math, time, os
pygame.init()

class custom_surface(pygame.sprite.Sprite,pygame.surface.Surface):
    def __init__(self,master, x,y, width, height, color = '#000000',
                 has_scrollbar = False, scrollbar_mode = 'y'):
        pygame.sprite.Sprite.__init__(self)
        pygame.surface.Surface.__init__(self,(width, height))
        self.x = x
        self.y = y
        self.master = master
        self.content = content(self)
        self.rect = self.get_rect()
        self.color = color
        self.rect.topleft = (x,y)
        self.has_scrollbar = has_scrollbar
        if has_scrollbar:
            self.scrollbar = scrollbar(self, self.rect, scrollbar_mode)
            self.rect.width -= 10
            self.rect.height -= 10

    def draw_on_surface(self):
        self.content.custom_draw()
        if self.has_scrollbar:
            self.scrollbar.draw()

    def get_offset(self):
        x_offset = 0
        y_offset = 0
        try:
            x_offset += self.rect.topleft[0]
            y_offset += self.rect.topleft[1]
            master_offset = self.master.get_offset()
            x_offset += master_offset[0]
            y_offset += master_offset[1]
        except:
            pass
        return pygame.math.Vector2(x_offset, y_offset)

    def set_pos(self, x, y):
        self.rect.topleft = (x,y)
    def draw(self):
        self.fill(self.color)
        self.draw_on_surface()
        self.master.blit(self, self.rect)

class content(pygame.sprite.Group):
    def __init__(self,master):
        pygame.sprite.Group.__init__(self)
        self.rect = pygame.rect.Rect(0,0,0,0)
        self.offset = pygame.math.Vector2(0,0)
        self.master = master
    def custom_draw(self):
        max_width = 0
        max_height = 0
        for sprite in sorted(self.sprites(), key = lambda sprite: (sprite.x,sprite.y)):
            if sprite.x + sprite.rect.width > max_width:
                max_width = sprite.x + sprite.rect.width
            if sprite.y + sprite.rect.height > max_height:
                max_height = sprite.y + sprite.rect.height
            if self.master.has_scrollbar:
                sprite.rect.topleft = pygame.math.Vector2(sprite.x,sprite.y) + self.offset
            sprite.draw()
        self.rect.width = max_width
        self.rect.height = max_height
    def button_list(self):
        list = []
        for sprite in sorted(self.sprites(), key = lambda sprite: (sprite.x,sprite.y)):
            try:
                sprite.state
                list.append(sprite)
            except:
                pass
        return list
class scrollbar():
    def __init__(self,master, screen_rect, mode):
        self.x_holding =  False
        self.y_holding = False
        self.master = master
        self.mode = mode
        self.conner_rect = pygame.rect.Rect(screen_rect.width - 10,screen_rect.height - 10, 10,10)
        if 'x' in self.mode:
            self.x_scrollbar = custom_surface(self.master,0, screen_rect.height - 10, screen_rect.width - 10, 10)
            self.x_scrollbar.set_colorkey('#000000')
            self.x_scrollbar.set_alpha(125)
            self.x_bar = custom_rect(self.x_scrollbar,0,0, screen_rect.width - 10, 10,'#EBEDEF', r_corners_int= 4)
            self.x_button = button(self.x_scrollbar, 0,0, screen_rect.width - 10, 10,['#B9770E','#B9770E','#B9770E'], r_corners_int= 4)
            self.x_button.add(self.x_scrollbar.content)
            self.pre_mouse_pos_x = 0.0
        
        if 'y' in self.mode:
            self.y_scrollbar = custom_surface(self.master,screen_rect.width - 10, 0, 10, screen_rect.height)
            self.y_scrollbar.set_colorkey('#000000')
            self.y_scrollbar.set_alpha(125)
            self.y_bar = custom_rect(self.y_scrollbar,0, 0, 10, screen_rect.height,'#EBEDEF', r_corners_int= 4)
            self.y_button = button(self.y_scrollbar, 0, 0, 10, screen_rect.height,['#B9770E','#B9770E','#B9770E'], r_corners_int= 4)
            self.y_button.add(self.y_scrollbar.content)
            self.pre_mouse_pos_y = 0.0

    def x_update(self,screen,mouse_pos):
        #resize button
        if screen.content.rect.width > screen.rect.width:
            diff = self.x_bar.width/screen.content.rect.width
            new_width = diff*self.x_bar.width
            self.x_button.width = new_width
            #getting offset
            dis_diff = self.x_button.rect.topleft[0]/ self.x_bar.width
            screen.content.offset.x = -(dis_diff*screen.content.rect.width)
        else:
            self.x_button.width = self.x_bar.width

        if self.x_button.rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed(3)[0]:
            self.x_holding = True
        if mouse_pos[0]<0 or mouse_pos[0]>screen.rect.width:
            self.x_holding = False
        if mouse_pos[0] >= self.x_button.rect.x and mouse_pos[0] <= self.x_button.rect.bottomright[0] and self.x_holding:
            new_x = self.x_button.rect.x + mouse_pos[0] - self.pre_mouse_pos_x
            if new_x <= self.x_bar.rect.topleft[0]:
                new_x = self.x_bar.rect.topleft[0]
            if new_x + self.x_button.width >= self.x_bar.rect.bottomright[0]:
                new_x = self.x_bar.rect.bottomright[0] - self.x_button.width
            self.x_button.rect.x = new_x
        if not pygame.mouse.get_pressed(3)[0]:
            self.x_holding = False
        

    def y_update(self,screen,mouse_pos):
        #resize button
        if screen.content.rect.height > screen.rect.height:
            diff = self.y_bar.height/screen.content.rect.height
            new_height = diff*self.y_bar.height
            self.y_button.height = new_height
            #getting offset
            dis_diff = self.y_button.rect.topleft[1]/ self.y_bar.height
            screen.content.offset.y = -(dis_diff*screen.content.rect.height)
        else:
            self.y_button.height = self.y_bar.height

        if self.y_button.rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed(3)[0]:
            self.y_holding = True
        if mouse_pos[1]<0 or mouse_pos[1]>screen.rect.height:
            self.y_holding = False
        if mouse_pos[1] >= self.y_button.rect.y and mouse_pos[1] <= self.y_button.rect.bottomright[1] and self.y_holding:
            new_y = self.y_button.rect.y + mouse_pos[1] - self.pre_mouse_pos_y  
            if new_y <= self.y_bar.rect.topright[1]:
                new_y = self.y_bar.rect.topright[1]
            if new_y + self.y_button.height >= self.y_bar.rect.bottomright[1]:
                new_y = self.y_bar.rect.bottomright[1] - self.y_button.height  
            self.y_button.rect.y = new_y
        if not pygame.mouse.get_pressed(3)[0]:
            self.y_holding = False
        

    def draw(self):
        if self.master.content.rect.width > self.master.rect.width:
            if 'x' in self.mode:
                mouse_pos = pygame.mouse.get_pos() - self.x_scrollbar.get_offset()
                self.x_update(self.master,mouse_pos)
                self.x_scrollbar.draw()
                self.pre_mouse_pos_x = mouse_pos[0]
        if self.master.content.rect.height > self.master.rect.height:
            if 'y' in self.mode:
                mouse_pos = pygame.mouse.get_pos() - self.y_scrollbar.get_offset()
                self.y_update(self.master,mouse_pos)
                self.y_scrollbar.draw()
                self.pre_mouse_pos_y = mouse_pos[1]

class custom_rect(pygame.sprite.Sprite):
    def __init__(self, master, x, y, width, height, color, bodder_int=0, r_corners_int=0):
        super().__init__()
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.rect = pygame.Rect(x, y, width, height)
        self.master = master
        self.content = content(self)
        self.color = color
        self.bodder_int = bodder_int
        self.r_corners_int = r_corners_int
    def draw(self):
        pygame.draw.rect(self.master,self.color,self.rect,self.bodder_int, self.r_corners_int)

class text_label(pygame.sprite.Sprite):
    def __init__(self,master, x, y, text, size = 16, font = None, color = '#000000', placement = None, placement_offset = [0,0]):
        super().__init__()
        self.x = x
        self.y = y
        self.master = master
        self.color = color
        self.size = size
        self.font = font
        self.placement = placement
        self.placement_offset = pygame.math.Vector2(placement_offset)
        if font != None:
            self.r_font = pygame.font.SysFont(font, self.size)
        else:
            self.r_font = pygame.font.SysFont(None, self.size)
        self.text = text
        self.sprite = self.r_font.render(self.text,True,self.color)
        self.rect = self.sprite.get_rect()
        if self.placement == None:
            self.rect.x = x
            self.rect.y = y
        else:
            self.set_placement()

    def set_placement(self):
        if self.placement == 1:
            self.rect.topleft = self.master.rect.topleft + self.placement_offset - self.master.rect.topleft
        elif self.placement == 2:
            self.rect.midtop = self.master.rect.midtop + self.placement_offset - self.master.rect.topleft
        elif self.placement == 3:
            self.rect.topright = self.master.rect.topright + self.placement_offset - self.master.rect.topleft
        elif self.placement == 4:
            self.rect.midleft = self.master.rect.midleft + self.placement_offset - self.master.rect.topleft
        elif self.placement == 5:
            self.rect.center = self.master.rect.center + self.placement_offset - self.master.rect.topleft
        elif self.placement == 6:
            self.rect.midright = self.master.rect.midright + self.placement_offset - self.master.rect.topleft
        elif self.placement == 7:
            self.rect.bottomleft = self.master.rect.bottomleft + self.placement_offset - self.master.rect.topleft
        elif self.placement == 8:
            self.rect.midbottom = self.master.rect.midbottom + self.placement_offset - self.master.rect.topleft
        elif self.placement == 9:
            self.rect.bottomright = self.master.rect.bottomright + self.placement_offset - self.master.rect.topleft

    def update(self):
        self.sprite = self.r_font.render(self.text,True,self.color)
        if self.placement == None:
            old_rect_topleft = self.rect.topleft
            self.rect = self.sprite.get_rect(topleft = old_rect_topleft)
        else:
            self.rect = self.sprite.get_rect()
            self.set_placement()


    def change_text(self,new_text):
        self.text = new_text
        self.update()

    def change_placement(self, new_placement, new_placement_offset):
        self.placement = new_placement
        self.placement_offset = new_placement_offset
        if self.placement != None:
            self.rect.x = self.x
            self.rect.y = self.y
        else:
            self.set_placement()

    def change_font(self,new_font):
        self.r_font = pygame.font.SysFont(new_font, self.size)
        self.update()

    def change_size(self,new_size):
        self.size = new_size
        if self.font != None:
            self.r_font = pygame.font.SysFont(self.font, self.size)
        else:
            self.r_font = pygame.font.SysFont(None, self.size)
        self.update()

    def draw(self):
        self.master.blit(self.sprite,self.rect)

class image_label(pygame.sprite.Sprite):
    def __init__(self,master, x, y, dir, placement = None, placement_offset = [0,0]):
        super().__init__()
        self.x = x
        self.y = y
        self.master = master
        self.dir = dir
        self.og_sprite = pygame.image.load(dir)
        self.sprite = self.og_sprite
        self.sprite = self.sprite.convert_alpha()
        self.rect = self.sprite.get_rect()
        self.placement = placement
        self.placement_offset =  pygame.math.Vector2(placement_offset)
        if self.placement == None:
            self.rect.x = x
            self.rect.y = y
        else:
            self.set_placement()
        self.sprite.set_colorkey('#000000')

    def rescale(self, width, height):
        self.sprite = pygame.transform.smoothscale(self.og_sprite, (width, height))
        if self.placement == None:
            old_rect_topleft = self.rect.topleft
            self.rect = self.sprite.get_rect(topleft = old_rect_topleft)
        else:
            self.rect = self.sprite.get_rect()
            self.set_placement()

    def change_placement(self, new_placement, new_placement_offset):
        self.placement = new_placement
        self.placement_offset = new_placement_offset
        if self.placement != None:
            self.rect.x = self.x
            self.rect.y = self.y
        else:
            self.set_placement()

    def set_placement(self):
        if self.placement == 1:
            self.rect.topleft = self.master.rect.topleft + self.placement_offset - self.master.rect.topleft
        elif self.placement == 2:
            self.rect.midtop = self.master.rect.midtop + self.placement_offset - self.master.rect.topleft
        elif self.placement == 3:
            self.rect.topright = self.master.rect.topright + self.placement_offset - self.master.rect.topleft
        elif self.placement == 4:
            self.rect.midleft = self.master.rect.midleft + self.placement_offset - self.master.rect.topleft
        elif self.placement == 5:
            self.rect.center = self.master.rect.center + self.placement_offset - self.master.rect.topleft
        elif self.placement == 6:
            self.rect.midright = self.master.rect.midright + self.placement_offset - self.master.rect.topleft
        elif self.placement == 7:
            self.rect.bottomleft = self.master.rect.bottomleft + self.placement_offset - self.master.rect.topleft
        elif self.placement == 8:
            self.rect.midbottom = self.master.rect.midbottom + self.placement_offset - self.master.rect.topleft
        elif self.placement == 9:
            self.rect.bottomright = self.master.rect.bottomright + self.placement_offset - self.master.rect.topleft
    def draw(self):
        self.master.blit(self.sprite, self.rect)

class animated_label(pygame.sprite.Sprite):
    def __init__(self,master, x, y , dir, speed, start_frame):
        super().__init__()
        self.x = x
        self.y = y
        self.master = master
        self.animation_library =  {}
        self.animations = os.listdir(dir)
        for animation in self.animations:
            path = []
            action = os.listdir(f'{dir}\\{animation}')
            for frame in action:
                path.append(pygame.image.load(f'{dir}\\{animation}\\{frame}').convert_alpha())
            self.animation_library.update({animation:path})
        self.cur_action = start_frame
        self.cur_frame = 0
        self.sprite = None
        self.rect = None
        self.animaiton_speed = speed

    def update(self,dt):
        self.cur_frame += self.animaiton_speed*dt
        if self.cur_frame > len(self.animation_library[self.cur_action]):
            self.cur_frame = 0
        self.sprite = self.animation_library[self.cur_action][int(self.cur_frame)-1]
        self.rect = self.sprite.get_rect()

    def draw(self,dt):
        self.update(dt)
        self.master.blit(self.sprite, self.rect)

class button(pygame.sprite.Sprite,pygame.surface.Surface):
    def __init__(self,master, x, y, width, height, color = ['#000000','#000000','#000000'], bodder_int=0, r_corners_int=0, elevation=0, bg_color = '#000000'):
        pygame.sprite.Sprite.__init__(self)
        pygame.surface.Surface.__init__(self,(width,height+elevation),pygame.SRCALPHA)
        self.x = x
        self.y = y
        self.master = master
        self.content = content(self)
        self.width = width
        self.height = height
        self.color = {'idle': color[0], 'hover': color[1], 'holding': color[2]}
        self.state = 'idle'
        self.bodder_int = bodder_int
        self.elevation = elevation
        self.r_corners = r_corners_int
        self.button_rect = custom_surface(self,0,0,width,height,color = self.color['idle'])
        self.foudation_rect = pygame.Rect(0,elevation, width, height)
        self.rect = self.get_rect()
        self.bg_color = bg_color
        self.has_scrollbar = False
        self.rect.x = x
        self.rect.y = y
        self.selected = False
    
    def get_sound(self,dir):
        if dir != None:
            self.sound = pygame.mixer.Sound(self.dir)
            self.sound.set_volume(0.05)
    def set_sound_vol(self,vol):
        self.sound.set_volume(vol)
    
    def setcolorkey(self, colorkey):
        self.set_colorkey(colorkey)
        
    def get_offset(self):
        x_offset = 0
        y_offset = 0
        try:
            x_offset += self.rect.topleft[0]
            y_offset += self.rect.topleft[1]
            master_offset = self.master.get_offset()
            x_offset += master_offset[0]
            y_offset += master_offset[1]
        except:
            pass
        
        return pygame.math.Vector2(x_offset, y_offset)

    def press(self):
        mouse_pos = pygame.mouse.get_pos() - self.get_offset()
        if self.button_rect.rect.collidepoint(mouse_pos):
            if self.state == 'idle':
                self.state = 'hover'
            if pygame.mouse.get_pressed(3)[0]:
                self.state = 'holding'            
            if self.state == 'holding' and not pygame.mouse.get_pressed(3)[0]:
                self.state = 'idle'
                try:
                    self.sound.play()
                except:
                    pass
                self.selected = True
                return 'clicked'
        else:
            if self.state == 'hover':
                self.state = 'idle'
            if pygame.mouse.get_pressed(3)[0]:
                self.selected = False
    
    def update(self):
        if self.elevation > 0:
            self.foudation_rect.x = 0
            self.foudation_rect.y = self.elevation

    def draw(self):
        if self.state == 'idle' or self.state == 'hover':
            self.button_rect.rect.y = 0
        elif self.state == 'holding':
            self.button_rect.rect.y = self.elevation

        
        self.fill(self.bg_color)

        self.button_rect.color = self.color[self.state]

        if self.elevation > 0:
            pygame.draw.rect(self, '#475F77', self.foudation_rect, self.bodder_int, self.r_corners)
        self.button_rect.draw()

        self.content.custom_draw()

        self.update()
        self.master.blit(self,self.rect)

class round_button(button):
    def __init__(self,x, y, width, height, color = ['#000000','#000000','#000000'], bodder_int=0, elevation=0):
        super().__init__(x, y, width, height, color, bodder_int, elevation = elevation)
        self.between_rect = pygame.rect.Rect(self.rect.midleft,(self.width, self.elevation))
        pygame.draw.ellipse(self, '#475F77', self.button_rect)
        self.mask = pygame.mask.from_surface(self)
        self.set_colorkey('#000000')
    
    def press(self,screen_rect):
        mouse_pos = pygame.mouse.get_pos() - pygame.math.Vector2(screen_rect.topleft)
        if self.button_rect.collidepoint(mouse_pos):
            if self.mask.get_at(mouse_pos) == 1:
                if self.state == 'idle':
                    self.state = 'hover'
                    
                if pygame.mouse.get_pressed(3)[0]:
                    self.state = 'holding'
                    
                if self.state == 'holding' and not pygame.mouse.get_pressed(3)[0]:
                    self.state = 'idle'
                    try:
                        self.sound.play()
                    except:
                        pass
                    return 'clicked'
            else:
                if self.state == 'hover':
                    self.state = 'idle'
                    

    def update(self):
        self.between_rect = pygame.rect.Rect(self.rect.midleft,(self.width,self.foudation_rect.midleft[1]-self.rect.midleft[1]))

    def draw(self, screen):
        if self.state == 'idle' or self.state == 'hover':
            self.button_rect.y = 0
        elif self.state == 'holding':
            self.button_rect.y = self.foudation_rect.y 


        self.fill('#000000')

        if self.elevation > 0:
            pygame.draw.ellipse(self, '#475F77', self.foudation_rect)
            pygame.draw.rect(self, '#475F77', self.between_rect)
        pygame.draw.ellipse(self, self.color, self.button_rect, self.bodder_int)
        
        try:
            self.set_placement_t()
            self.text.draw(self)
        except:
            pass
        try:
            self.set_placement_i()
            self.image.draw(self)
        except:
            pass

        self.update()
        
        screen.blit(self,self.rect)

class textbox(button):
    def __init__(self, master, x, y, width, height, color = ['#000000','#000000','#000000'], bodder_int=0, r_corners_int=0, bg_color = '#000000'):
        button.__init__(self, master, x, y, width, height, color , bodder_int, r_corners_int,0, bg_color)
        self.the_text = text_label(self, 0,0, '', placement = 5)
        self.content.add(self.the_text)
        

    def typing(self,events):
        self.press()
        if self.selected:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        self.the_text.text = self.the_text.text[:-1]
                        self.the_text.update()
                    else:
                        self.the_text.text += event.unicode
                        self.the_text.update()

class combo_box(button):
    def __init__(self, master, x, y, width, height, color = ['#000000','#000000','#000000'], bodder_int=0, r_corners_int=0, bg_color = '#000000'):
        button.__init__(self, master, x, y, width, height, color , bodder_int, r_corners_int,0, bg_color)
        self.the_text = text_label(self, 0,0, '', placement = 5)
        self.content.add(self.the_text)

    def get_the_combo(self,dic,text_size,):
        self.combo = dic
        self.combo_buttons = []
        self.the_combo_surface = custom_surface(self.master, self.x,self.y+self.height,self.width,self.height*len(self.combo),'#FFFFFF')
        index = 0
        for item in self.combo:
            t_button = button(self.the_combo_surface,0,self.height*index,self.width,self.height,color= ['#FFFFFF','#FFFFFF','#FFFFFF'])
            t_text = text_label(t_button,0,0,item,text_size,placement=5)
            t_button.content.add(t_text)
            self.the_combo_surface.content.add(t_button)
            self.combo_buttons.append([t_button, t_text])
            index += 1

    def check(self):
        if self.selected:
            for button in self.combo_buttons:
                if button[0].press() == 'clicked':
                    self.the_text.text = button[1].text
                    self.the_text.update()
                    self.selected = False

    def press(self):
        mouse_pos = pygame.mouse.get_pos() - self.get_offset()
        if self.button_rect.collidepoint(mouse_pos):
            if self.state == 'idle':
                self.state = 'hover'
            if pygame.mouse.get_pressed(3)[0]:
                self.state = 'holding'            
            if self.state == 'holding' and not pygame.mouse.get_pressed(3)[0]:
                self.state = 'idle'
                try:
                    self.sound.play()
                except:
                    pass
                self.selected = True
                return 'clicked'
        else:
            if self.state == 'hover':
                self.state = 'idle'


    def draw(self):
        self.press()
        self.fill(self.bg_color)
        pygame.draw.rect(self, self.color[self.state], self.button_rect, self.bodder_int, self.r_corners)
        self.content.custom_draw()
        self.update()
        if self.selected:
            self.check()
            self.the_combo_surface.draw()
        self.master.blit(self,self.rect)