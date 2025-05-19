'''
Buttons and GUI design here

move_ratio = [ratio_x, ratio_y]
현재 맵에서 어느 위치에 지정되었느냐에 따라 화면 크기가 변할때 얼마나 움직여야 하는지가 다르다
오른쪽 모서리에 고정된 버튼은 y 움직임 없어야 하므로 [1,0]
가운데 위치한 버튼은 (self.y//2 같이 /2 operation이 붙을시 y 길이 증가함에 따라 반만 증가) [0.5,0.5]
어중간하게 중간이면 이런식 [0.5,1]
'''
from util import *
import random


class Button():
    def __init__(self, master, function_to_call, x,y, name, text_size=20,text_color = 'black', button_length=120, button_height=30, color = (150,150,150), hover_color = (80,80,80), move_ratio = [0.5,1]):
        self.master = master # 버튼이 부를 함수가 정의되어있는 주인 클래스 (여기 안에서만 이 버튼이 정의되며 존재함)
        self.function_to_call = function_to_call # given by string
        self.x = x
        self.y = y
        self.move_ratio = move_ratio
        self.name = name
        self.text_size = text_size
        self.text_color = text_color
        self.button_length = button_length
        self.button_height = button_height
        self.hover_color = hover_color
        self.original_color = color
        self.color = color
        self.hover = False

        self.text = Text(self.x, self.y, self.name,size = self.text_size,color=self.text_color)
        self.rect = pygame.Rect((self.x -button_length//2 ,self.y-button_height//2),(button_length,button_height))

    def check_inside_button(self,mousepos):
        if abs(mousepos[0] - self.x) < self.button_length//2 and abs(
                mousepos[1] - self.y) < self.button_height//2:
            return True
        else:
            return False

    def on_click(self,mousepos):
        if self.check_inside_button(mousepos):
            return getattr(self.master, self.function_to_call)() # 리턴값이 있다면 여기서 리턴해준다

    def hover_check(self,mousepos): # mousemotion일때 불러줘야함
        inside = self.check_inside_button(mousepos)
        if (not self.hover) and inside: # 호버 아니었는데 버튼 위에 올라옴 => 호버시작
            self.color = self.hover_color
            self.hover = True
        elif self.hover and not inside: # 호버링이었는데 벗어남 => 호버 끝
            self.color = self.original_color
            self.hover = False

    def draw_button(self,screen):
        pygame.draw.rect(screen, self.color,
                         [self.x - self.button_length // 2, self.y - self.button_height // 2, self.button_length,self.button_height])
        self.text.write(screen)

    def initialize(self):
        pass

    def get_all_rect(self):
        return [self.rect]

    def move_to(self, dx,dy):
        # change my coord
        self.x += dx*self.move_ratio[0]
        self.y += dy*self.move_ratio[1]
        # change text pos
        self.text.change_pos(self.x,self.y)
        # change rect pos
        self.rect.x = self.x - self.button_length // 2
        self.rect.y = self.y - self.button_height // 2

class ToggleButton(Button):
    def __init__(self, master, function_to_call, x, y, name, text_size=20,text_color = 'black', button_length=120, button_height=30,
                 color=(150, 150, 150), hover_color=(80, 80, 80),move_ratio = [1,0], toggle_text_dict = None, toggle_variable = None, max_toggle_count = 2):
        super().__init__(master, function_to_call, x, y, name, text_size,text_color, button_length, button_height,color, hover_color,move_ratio)
        self.toggle_text_dict = toggle_text_dict
        self.toggle_count = 0
        self.max_toggle_count = max_toggle_count
        self.toggle_variable = toggle_variable # for synchronization
        self.toggle_tracker = toggle_variable[0]

        # self.text = Text(self.x, self.y, "{}: {}".format(self.toggle_text_dict[self.toggle_count],self.toggle_variable[0]), size=self.text_size, color='black')
        self.text = Text(self.x, self.y, "{}: {}".format(self.name,self.toggle_variable[0]), size=self.text_size, color='black')

        self.text_explanation_rect = None

        if self.toggle_text_dict:
            self.explain_text_offset = [0 , self.text_size*3//2]
            self.text_explanation = Text(self.x+self.explain_text_offset[0], self.y + self.explain_text_offset[1], self.get_explanation(), size=17, color='gray')
            self.text_explanation_rect = pygame.Rect((self.x -button_length//2 + self.explain_text_offset[0],self.y-button_height//2 + self.explain_text_offset[1]),(button_length,button_height))


    def get_all_rect(self):
        if not self.toggle_text_dict:
            return super().get_all_rect()
        return [self.rect, self.text_explanation_rect]

    def get_explanation(self):
        return self.toggle_text_dict[self.toggle_tracker]

    def update_explanation(self):
        if self.toggle_text_dict:
            self.text_explanation.change_content(self.get_explanation())

    def on_click(self,mousepos):
        if self.check_inside_button(mousepos): # 반드시 토글변수가 바뀜
            do_toggle = getattr(self.master, self.function_to_call)()
            # self.update_toggle_count()
            # print(self.name,self.toggle_variable[0])
            self.synch()
            return do_toggle# 리턴값이 있다면 여기서 리턴해준다

    def synch(self):
        if self.toggle_variable[0] != self.toggle_tracker:
            self.update_toggle_tracker(self.toggle_variable[0])
            self.text.change_content("{}: {}".format(self.name,self.toggle_variable[0]))
            self.update_explanation()

    def initialize(self):
        self.synch()

    def update_toggle_tracker(self, togglevar):
        self.toggle_tracker = togglevar

    # not used
    def update_toggle_count(self):
        self.toggle_count += 1
        if self.toggle_count == self.max_toggle_count: # reset
            self.toggle_count = 0

    def draw_button(self,screen):
        super().draw_button(screen)
        # draw explanation if needed
        if self.hover and self.toggle_text_dict:
            pygame.draw.rect(screen, 'black',
                             [self.x - self.button_length // 2 + self.explain_text_offset[0], self.y - self.button_height // 2 + self.explain_text_offset[1], self.button_length,
                              self.button_height])
            self.text_explanation.write(screen)

    def move_to(self, dx,dy):
        super().move_to(dx,dy)
        # change explanation rect pos
        if self.toggle_text_dict:
            # change explanation text pos
            self.text_explanation.change_pos(self.x+self.explain_text_offset[0], self.y+self.explain_text_offset[1])
            self.text_explanation_rect.x = self.x - self.button_length // 2 + self.explain_text_offset[0]
            self.text_explanation_rect.y = self.y - self.button_height // 2 + self.explain_text_offset[1]



class Selector():
    def __init__(self, x, y, name, choices, text_sizes=[15,17,23,17,15],
                 colors=[(90, 90, 90),(130, 130, 130),(150, 150, 150),(130, 130, 130),(90, 90, 90)], move_ratio = [0.5,0.5]):
        self.x = x # center coordinate
        self.y = y # center coordinate
        self.move_ratio = move_ratio
        self.name = name
        self.text_sizes = text_sizes
        self.colors = colors

        self.select_pointer = 2 # having second entity pointing as default
        self.choices = choices
        self.choice = self.choices[self.select_pointer]

        self.choice_texts = []
        self.initialize_text()
        self.rect = None # includes text rect(should be made manually) and button rect -> if you are going to used selector in update screen

        self.name_text = Text(self.x, self.y - 120, self.name,size = 23,color=self.colors[2])

        self.buttons = [Button(self, 'up', self.x, self.y - 75, 'Λ',move_ratio = self.move_ratio,text_size=20,text_color=(100,100,100), button_length=30, button_height=30,
                 color=(0, 0, 0), hover_color=(10, 10, 10)),
                        Button(self, 'down', self.x, self.y + 75 , 'V',move_ratio = self.move_ratio,text_size=20,text_color=(100,100,100), button_length=30, button_height=30,
                 color=(0, 0, 0), hover_color=(10, 10, 10))]

    def scroll_up(self, mousepos):
        if self.check_inside_selector(mousepos):
            return self.up()

    def scroll_down(self, mousepos):
        if self.check_inside_selector(mousepos):
            return self.down()

    def check_inside_selector(self, mousepos):
        if abs(mousepos[0] - self.x) < 70 and abs(
                mousepos[1] - self.y) < 75:
            return True
        else:
            return False

    # 이거 main에서 클릭할때 불러줘야함 - 스크롤시엔 각 경우마다 up/down을 직접 불러야함
    def buttons_on_click(self, mousepos):
        ret = False
        for button in self.buttons:
            temp = button.on_click(mousepos)
            if temp: # if some output exists
                ret = temp
        return ret

    def up(self):
        return self.update_pointer(-1)

    def down(self):
        return self.update_pointer(1)

    def initialize_text(self):
        self.choice_texts = []
        for i in range(len(self.text_sizes)): # assert len(self.text_sizes) == len(self.colors) == len(self.choices)
            choice_text = Text(self.x, self.y + (i-2)*(29 - abs(i-2)*3), self.choices[i],size = self.text_sizes[i],color=self.colors[i])
            self.choice_texts.append(choice_text)

    def get_current_choice(self):
        # print("Selected system: {}".format(self.choice))
        return self.choice

    def check_bound(self):
        if self.select_pointer < 0: # unchanged
            self.select_pointer = 0
        elif self.select_pointer > len(self.choices) - 1:
            self.select_pointer = len(self.choices) - 1
        else:
            return True # changed
        return False # unchanged

    # pointer NOT periodic
    # if pointer value is changed, return True, else False
    def update_pointer(self, amt):
        self.select_pointer += amt
        changed_flag = self.check_bound()
        if changed_flag:
            self.choice = self.choices[self.select_pointer] # change choice
            self.update_texts() # update text contents too
        return changed_flag

    # if pointer changed, update text contents
    def update_texts(self):
        for i in range(len(self.text_sizes)):  # assert len(self.text_sizes) == len(self.colors) == len(self.choices)
            content = ""
            index_to_grab = self.select_pointer + (i-2)
            if  0 <= index_to_grab <= len(self.choices) - 1: # proper content exist
                content = self.choices[index_to_grab]
            self.choice_texts[i].change_content(content)

    # move ratio 0.5 is when assumed to be in the middle of the screen
    def move_to(self, dx,dy):
        # change my coord
        self.x += dx*self.move_ratio[0]
        self.y += dy*self.move_ratio[1]
        # change text pos
        for i in range(len(self.text_sizes)): # assert len(self.text_sizes) == len(self.colors) == len(self.choices)
            selection_text = self.choice_texts[i]
            selection_text.change_pos(self.x, self.y + (i-2)*(29 - abs(i-2)*3))
        self.name_text.change_pos(self.x,self.y- 120)
        # change button pos
        for button in self.buttons:
            button.move_to(dx,dy)
        # change rect pos

    def draw(self, screen):
        # Write name
        self.name_text.write(screen)
        # write selection text
        for selection_text in self.choice_texts:
            selection_text.write(screen)

        # draw buttons
        for button in self.buttons:
            getattr(button, 'draw_button')(screen)





class DiceContainer():
    def __init__(self, x, y, name, dice_types=['',''],owner = '', image_size = [62,62] ,move_ratio = [0.5,0.5]):
        self.x = x  # center coordinate
        self.y = y  # center coordinate
        self.image_size = image_size # fixed
        self.move_ratio = move_ratio
        self.name = name
        self.owner = owner
        self.interaction_dict = {'Break':False, 'Freeze':False}

        self.dice_list = []
        self.change_type(dice_types)

    def reset_dice(self,env):
        self.interaction_dict = {'Break':False, 'Freeze':False}
        for dice in self.dice_list:
            dice.reset_var(env)

    def get_dice(self):
        return self.dice_list

    def call(self, function_name, *args):
        result = []
        for dice in self.dice_list:
            if args:
                if len(args)==1:
                    result.append(getattr(dice, function_name)(args[0]))
                elif len(args)==2:
                    result.append(getattr(dice, function_name)(args[0],args[1]))
                else:
                    print("Arguement passed more than 3!")
            else:
                result.append(getattr(dice, function_name)())
        return result

    def change_type(self, new_type_list):
        self.dice_list = []
        cnt=0
        for dice_type in new_type_list:
            dice = None
            if dice_type=='ice':
                dice = IceDice(self.x, self.y, dice_type,owner = self.owner,dice_index=cnt, image_size = self.image_size ,move_ratio = self.move_ratio)
            elif dice_type=='wood':
                dice = WoodDice(self.x, self.y, dice_type,owner = self.owner,dice_index=cnt, image_size = self.image_size ,move_ratio = self.move_ratio)
            elif dice_type=='dark':
                dice = DarkDice(self.x, self.y, dice_type, owner = self.owner,dice_index=cnt, image_size=self.image_size,
                                move_ratio=self.move_ratio)
            elif dice_type == 'aqua':
                dice = AquaDice(self.x, self.y, dice_type, owner = self.owner,dice_index=cnt, image_size=self.image_size,
                                move_ratio=self.move_ratio)
            elif dice_type == 'royal':
                dice = RoyalDice(self.x, self.y, dice_type, owner = self.owner,dice_index=cnt, image_size=self.image_size,
                                move_ratio=self.move_ratio)
            else:
                dice = Dice(self.x, self.y, dice_type,owner = self.owner,dice_index=cnt, image_size = self.image_size ,move_ratio = self.move_ratio)
            self.dice_list.append(dice)
            cnt+=1

    def change_content(self,roll):
        cnt=0
        for d_num in roll:
            self.dice_list[cnt].change_content(d_num)
            cnt+=1

    def interact_dice(self,point,env):
        ability_used = False
        for dice in self.dice_list:
            if dice.interact(point,env,self.interaction_dict):
                ability_used = True

        if ability_used:
            for dice in self.dice_list:
                dice.ability_used = True

    def move_to(self,dx,dy):
        # change my coord
        dx_motion = dx * self.move_ratio[0]
        dy_motion = dy * self.move_ratio[1]
        self.x += dx_motion
        self.y += dy_motion
        for dice in self.dice_list:
            dice.move_to(dx,dy)

    def end_random_roll(self):
        for dice in self.dice_list:
            dice.end_random_roll()

class Dice():
    def __init__(self, x, y, name, dice_index = 0, owner = '',image_size = [50,50] ,move_ratio = [0.5,0.5]):
        self.x = x  # center coordinate
        self.y = y  # center coordinate
        self.image_size = image_size # fixed
        self.move_ratio = move_ratio
        self.name = name
        self.image_folder = '/images/dice/'
        self.image_names = list()
        self.image_dict = dict()
        self.dice_image = None # current images to draw
        self.all_images = []
        self.highlight_img = None
        self.highlight_text = None
        self.dice_index = dice_index

        self.dice_type = name
        self.initialize()

        self.ability_used = False

        self.owner = owner

    def reset_var(self,env):
        self.ability_used = False

    # initially download images
    def initialize(self,dice_num=1):
        self.image_names = self.read_all_image_names()

        for img_name in self.image_names: # save one dice
            img = Image(self.x,self.y, "%s"%img_name ,folder = self.image_folder,size = self.image_size)
            if self.dice_index==0:
                img.rot_center(-45)
                img.move_image(-100,-20)
            elif self.dice_index==1:
                img.rot_center(10)
                img.move_image(20, 0)
            else:
                print("ERROR: Invalid dice index!")
            self.image_dict[img_name] = img
            self.all_images.append(img)

        # highlights
        h = Image(self.x, self.y, "highlight", folder=self.image_folder, size=self.image_size)
        if self.dice_index == 0:
            h.rot_center(-45)
            h.move_image(-100, -20)
        elif self.dice_index == 1:
            h.rot_center(10)
            h.move_image(20, 0)
        else:
            print("ERROR: Invalid dice index!")
        self.highlight_img = h

        self.change_content(dice_num)

    def read_all_image_names(self):
        image_names = list(os.listdir(self.image_folder[1:]))
        # remove '.png' part
        image_names = [system_name[:-4] for system_name in image_names]
        # only numbers from 0, 1 to 6 are remained
        image_names = list(filter(lambda x:x in [self.dice_type+str(i) for i in range(7)], image_names))

        # print(image_names)
        return image_names

    # draw if current content is not None
    def draw(self,screen):
        if self.dice_image:
            self.dice_image.draw(screen)

    def draw_random_dice(self,screen):
        random_dice = random.choice(self.all_images)
        random_dice.draw(screen)

    def move_to(self,dx, dy):
        # change my coord
        dx_motion = dx * self.move_ratio[0]
        dy_motion = dy * self.move_ratio[1]
        self.x += dx_motion
        self.y += dy_motion
        for img_name in self.image_names:
            img_to_move = self.image_dict[img_name]
            if img_to_move:
                img_to_move.move_image(dx_motion,dy_motion)

        self.highlight_img.move_image(dx_motion,dy_motion)

    # if it is in jacket name list, use it. Otherwise, leave as None
    def change_content(self,dice_num):
        self.dice_image = None
        dice_num = str(dice_num)
        dice_name = self.dice_type + dice_num
        if dice_name in self.image_names:
            self.dice_image = self.image_dict[dice_name]

    def check_point_inside(self,point):
        collision = self.dice_image.get_rect().collidepoint(point)
        return collision

    def get_rect(self):
        if self.dice_image:
            return self.dice_image.get_rect()

    def get_dice_num(self):
        if self.dice_image:
            return int(self.dice_image.filename[-1])

    def highlight(self,mousepos, screen ):
        h = self.highlight_img.get_rect()
        if h.collidepoint(mousepos):
            self.highlight_img.draw(screen)
            if self.highlight_text and not self.ability_used:
                self.highlight_text.change_pos(mousepos[0]+30,mousepos[1]-20)
                self.highlight_text.write(screen)

    def break_sound(self):
        soundPlayer.play_sound_effect('break_wood')

    def roll_sound(self):
        soundPlayer.play_sound_effect('dice_roll')

    def interact(self,point,env, interaction_list):
        return False

    def end_random_roll(self):
        pass

class DarkDice(Dice):
    def __init__(self, x, y, name, dice_index = 0,owner = '', image_size = [50,50] ,move_ratio = [0.5,0.5]):
        super().__init__(x, y, name,dice_index = dice_index ,owner=owner, image_size = image_size ,move_ratio = move_ratio)

class WoodDice(Dice):
    def __init__(self, x, y, name, dice_index = 0,owner = '', image_size = [50,50] ,move_ratio = [0.5,0.5]):
        super().__init__(x, y, name,dice_index = dice_index ,owner=owner, image_size = image_size ,move_ratio = move_ratio)
        self.highlight_text = Text(self.x,self.y, "Break", size=20, color=(138, 134, 96))

    def break_sound(self):
        soundPlayer.play_sound_effect('break_wood')

    def roll_sound(self):
        soundPlayer.play_sound_effect('wood_sticks')

    def interact(self,point,env,interaction_list):
        if self.check_point_inside(point) and not interaction_list['Break']:#
            self.break_sound()
            if self.owner == 'Player':
                env.add_player_hand( -self.get_dice_num())
            else:
                env.add_dealer_hand(-self.get_dice_num())
            self.change_content(0) # break number to 0
            interaction_list['Break'] = True
            return True

class AquaDice(Dice):
    def __init__(self, x, y, name, dice_index = 0,owner = '', image_size = [50,50] ,move_ratio = [0.5,0.5]):
        super().__init__(x, y, name,dice_index = dice_index ,owner=owner, image_size = image_size ,move_ratio = move_ratio)
    def break_sound(self):
        soundPlayer.play_sound_effect('water')

    def roll_sound(self):
        soundPlayer.play_sound_effect('snow_break')

class RoyalDice(Dice):
    def __init__(self, x, y, name, dice_index = 0,owner = '', image_size = [50,50] ,move_ratio = [0.5,0.5]):
        super().__init__(x, y, name,dice_index = dice_index ,owner=owner, image_size = image_size ,move_ratio = move_ratio)
    def break_sound(self):
        soundPlayer.play_sound_effect('ball_throw')

    def roll_sound(self):
        soundPlayer.play_sound_effect('dice_roll')

    def reset_var(self,env):
        self.ability_used = False
        if self.owner == 'Player':
            env.set_player_protection()
        # no protection for the dealer!


class IceDice(Dice):
    def __init__(self, x, y, name, dice_index=0,owner = '', image_size=[50, 50], move_ratio=[0.5, 0.5]):
        super().__init__(x, y, name, dice_index=dice_index,owner=owner, image_size=image_size, move_ratio=move_ratio)
        self.frozen = False
        self.highlight_text = Text(self.x, self.y, "Freeze", size=20, color=(138, 134, 96))

    def break_sound(self):
        soundPlayer.play_sound_effect('tit')

    def freeze_sound(self):
        soundPlayer.play_sound_effect('freezing')

    def roll_sound(self):
        soundPlayer.play_sound_effect('dice_roll_plastic')

    def interact(self,point,env,interaction_list):
        if self.check_point_inside(point) and not interaction_list['Freeze']:#
            self.freeze_sound()
            interaction_list['Freeze'] = True
            env.set_freeze(self.dice_index)
            self.frozen = True
            return True

    def draw_random_dice(self,screen):
        if self.frozen:
            self.draw(screen)
            return
        random_dice = random.choice(self.all_images)
        random_dice.draw(screen)

    # draw if current content is not None
    def draw(self,screen):
        if self.dice_image:
            self.dice_image.draw(screen)

    def end_random_roll(self):
        self.frozen = False
