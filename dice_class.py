from gui import *

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

    def get_new_die(self,cnt,dice_type, x_loc = None, y_loc = None, owner = None):
        x_loc = self.x if not x_loc else x_loc
        y_loc = self.y if not y_loc else y_loc
        owner = self.owner if not owner else owner

        dice = None
        if dice_type == 'ice':
            dice = IceDice(x_loc, y_loc, dice_type, owner=owner, dice_index=cnt, image_size=self.image_size,
                           move_ratio=self.move_ratio)
        elif dice_type == 'wood':
            dice = WoodDice(x_loc, y_loc, dice_type, owner=owner, dice_index=cnt, image_size=self.image_size,
                            move_ratio=self.move_ratio)
        elif dice_type == 'dark':
            dice = DarkDice(x_loc, y_loc, dice_type, owner=owner, dice_index=cnt, image_size=self.image_size,
                            move_ratio=self.move_ratio)
        elif dice_type == 'aqua':
            dice = AquaDice(x_loc, y_loc, dice_type, owner=owner, dice_index=cnt, image_size=self.image_size,
                            move_ratio=self.move_ratio)
        elif dice_type == 'royal':
            dice = RoyalDice(x_loc, y_loc, dice_type, owner=owner, dice_index=cnt, image_size=self.image_size,
                             move_ratio=self.move_ratio)
        else:
            dice = Dice(x_loc, y_loc, dice_type, owner=owner, dice_index=cnt, image_size=self.image_size,
                        move_ratio=self.move_ratio)

        return dice

    def change_type(self, new_type_list):
        self.dice_list = []
        cnt=0
        for dice_type in new_type_list:
            dice = self.get_new_die(cnt,dice_type)
            self.dice_list.append(dice)
            cnt+=1

    def change_die_type(self, die_index, new_type):
        self.dice_list[die_index] = self.get_new_die(die_index, new_type)

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
    ability_dict = {'Normal':'Normal dice blackjack',
                      'Break':"Can break 'one' die in a roll, once per game except the last round",
                      'Freeze':"Can freeze a die to get guaranteed number next turn, once per game",
                      'Guard':"Your dice protects you against busting, for once" }
    def __init__(self, x, y, name, ability = '',dice_index = 0, owner = '',image_size = [50,50] ,move_ratio = [0.5,0.5]):
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
        self.explanation = None
        self.ability = ability

        if ability:
            self.highlight_text = Text(self.x,self.y, self.ability, size=20, color=(138, 134, 96))
            self.explanation = Text(self.x,self.y+100, Dice.ability_dict[self.ability] , size=17, color=(138, 134, 96))

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
        if self.ability:
            self.explanation.change_pos(self.x, self.y+100)

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
                self.explanation.write(screen)

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
        super().__init__(x, y, name,ability = 'Break',dice_index = dice_index ,owner=owner, image_size = image_size ,move_ratio = move_ratio)


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
        super().__init__(x, y, name,ability = 'Guard',dice_index = dice_index ,owner=owner, image_size = image_size ,move_ratio = move_ratio)
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
        super().__init__(x, y, name, ability = 'Freeze',dice_index=dice_index,owner=owner, image_size=image_size, move_ratio=move_ratio)
        self.frozen = False

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
