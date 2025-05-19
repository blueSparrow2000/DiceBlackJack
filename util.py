"""

"""
from sys import deactivate_stack_trampoline

import pygame
import os, sys
import math

'''
image container
'''


class Image():
    def __init__(self, x, y, filename, folder="/images/", size=[100, 100]):  # color aqua
        self.IMAGE_FOLDER = os.path.dirname(os.path.realpath(sys.argv[0])) + folder
        self.x = x
        self.y = y
        self.size = size
        self.filename = filename
        self.image = None
        try:
            full_path = os.path.join(self.IMAGE_FOLDER, '%s.png' % self.filename)
            self.image = pygame.image.load(full_path).convert_alpha()
        except:
            print("Folder: %s" % self.IMAGE_FOLDER)
            raise Exception("UTIL ERROR: {} image failed to load!".format(self.filename))

        # self.image.set_alpha(200) # 0 transparent to 255 for opaque

        self.imageRect = self.image.get_rect()
        self.imageRect.center = (self.x, self.y)
        self.initialize()

    def get_rect(self):
        return self.imageRect # self.image.get_rect()

    def initialize(self):
        # resize
        self.resize_image(self.size)

        # # center_image
        image_height = self.size[0]
        image_width = self.size[1]
        self.imageRect = self.imageRect.move((image_width // 2, image_height // 2))

    def center_image(self, x, y):
        self.x, self.y = x, y
        self.imageRect.center = (x, y)

    def move_image(self, dx, dy):
        self.x += dx
        self.y += dy
        self.imageRect = self.imageRect.move((dx, dy))

    # in place
    def resize_image(self, size):
        self.size = [size[0], size[1]]  # copy

        self.image = pygame.transform.scale(self.image, self.size)
        self.imageRect = self.image.get_rect(center=self.imageRect.center)  # conserve previous center

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def rot_center(self, angle):
        rotated_image = pygame.transform.rotate(self.image, angle)
        self.image = rotated_image
        self.imageRect = rotated_image.get_rect(center=self.imageRect.center)  # conserve previous center


'''
basic text box
'''


class Text():
    def __init__(self, x, y, content, size=20, color='darkturquoise', frames=100, bold = True):  # color aqua
        self.x = int(x)
        self.y = int(y)
        self.frames = frames
        self.size = size
        self.color = color
        self.bold = bold

        self.content = content
        self.font = pygame.font.SysFont('arial', size, self.bold)
        self.text = self.font.render(self.content, True, self.color)
        # text.set_alpha(127)
        self.textRect = self.text.get_rect(center=(self.x, self.y))

        self.text_width = self.text.get_width()
        self.text_height = self.text.get_height()

    def get_size(self):
        return self.text_width, self.text_height

    def change_pos(self, x, y):
        self.x = int(x)
        self.y = int(y)
        self.textRect.center = (self.x, self.y)

    def get_content(self):
        return self.content

    def change_content(self, content,new_color=None):
        if not new_color:
            new_color = self.color

        self.content = content
        self.text = self.font.render(self.content, True, new_color)
        # self.textRect = self.text.get_rect(center=(self.x, self.y))
        self.textRect = self.text.get_rect()
        self.textRect.center = (self.x, self.y)

    def write(self, screen):
        screen.blit(self.text, self.textRect)

    def get_rect(self):
        return self.textRect

    def change_color(self, new_color):
        self.color = new_color
        self.change_content(self.get_content())

'''
write center-alligned multiple line text 
'''

class MultiText():
    def __init__(self, x, y, content, size=20, color='darkturquoise', frames=100, content_per_line=10,
                 text_gap=5):  # color aqua
        self.x = int(x)
        self.y = int(y)
        self.frames = frames
        self.size = size
        self.color = color
        self.text_gap = text_gap

        # string alligning process
        self.content_blocks = []

        total_length = len(content)
        current_start = 0
        cnt = 0
        while current_start + content_per_line < total_length:
            text_content = Text(self.x, self.y + cnt * (self.size + self.text_gap),
                                content[current_start:current_start + content_per_line], self.size, self.color,
                                self.frames)
            self.content_blocks.append(text_content)
            current_start += content_per_line
            cnt += 1
        last_content = Text(self.x, self.y + cnt * (self.size + self.text_gap), content[current_start:total_length],
                            self.size, self.color, self.frames)
        self.content_blocks.append(last_content)

    def write(self, screen):
        for text_box in self.content_blocks:
            text_box.write(screen)

    def change_pos(self, x, y):
        self.x = int(x)
        self.y = int(y)
        cnt = 0
        for text_box in self.content_blocks:
            text_box.change_pos(x, y + cnt * (self.size + self.text_gap))
            cnt += 1


class ScoreViewer():
    def __init__(self, x, y, size=15, color=(120,120,120),light_color=(160,160,160), frames=100):  # color aqua
        self.x = int(x)
        self.y = int(y)
        self.frames = frames
        self.size = size
        self.color = color
        self.light_color = light_color

        self.text_locations = [[self.x, self.y-40],[self.x, self.y-20],[self.x, self.y+20],[self.x, self.y+40]]
        self.player_text = Text(self.text_locations[0][0],self.text_locations[0][1], "player", self.size, self.color,
             self.frames,bold = True)
        self.player_score = Text(self.text_locations[1][0],self.text_locations[1][1], "0", self.size+5, self.color,
             self.frames,bold = True)
        self.dealer_score = Text(self.text_locations[2][0],self.text_locations[2][1], "0", self.size+5, self.color,
             self.frames,bold = True)
        self.dealer_text = Text(self.text_locations[3][0],self.text_locations[3][1], "dealer", self.size, self.color,
             self.frames,bold = True)

        self.viewer_background = pygame.Rect(0, 0, 50, 100)
        self.viewer_background.center = (self.x, self.y)
        self.background_color = (0,0,0)#(138, 134, 96) #

        # string alligning process
        self.content_blocks = [self.player_text,self.player_score,self.dealer_score,self.dealer_text]

    def get_rect(self):
        return [block.get_rect() for block in self.content_blocks] + [self.viewer_background]

    def write(self, screen):
        pygame.draw.rect(screen, self.background_color, self.viewer_background)
        for text_box in self.content_blocks:
            text_box.write(screen)

    def change_pos(self, x, y):
        self.x = int(x)
        self.y = int(y)
        self.text_locations = [[self.x, self.y-40],[self.x, self.y-20],[self.x, self.y+20],[self.x, self.y+40]]

        for i in range(len(self.content_blocks)):
            content = self.content_blocks[i]
            content.change_pos(self.text_locations[i][0],self.text_locations[i][1])

        self.viewer_background.center = (self.x, self.y)

    def update_score_viewer_color(self, current_turn=""):
        if current_turn == "player":  # change highlight color
            self.player_text.change_color(self.light_color)
            self.dealer_text.change_color(self.color)
        elif current_turn == "dealer":
            self.player_text.change_color(self.color)
            self.dealer_text.change_color(self.light_color)
        else: # reset color
            self.player_text.change_color(self.color)
            self.dealer_text.change_color(self.color)

    def update_score_viewer(self,observation, burst_check = False):
        player_score, dealer_score = observation
        if burst_check:
            player_score = player_score if player_score<=21 else 0 # burst check
            dealer_score = dealer_score if dealer_score<=21 else 0 # burst check

        self.player_score.change_content(str(player_score))
        self.dealer_score.change_content(str(dealer_score))








'''
music player
'''


class MusicBox():
    current_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
    MUSIC_FOLDER = current_dir + '/musics/'
    SOUND_EFFECT = current_dir + '/sound_effects/'

    def __init__(self):
        pygame.mixer.init()
        mixer_channel_num = 8  # default 로 8임
        # This is the sound channel
        self.sound_channel = pygame.mixer.Channel(5)

        self.sound_effect_list = self.read_all_sound_effect_names()  # ['confirm','fissure','glass_break','lazer','metal','railgun_reload','shruff','smash','sudden','swing_by','thmb','rotate gas','thrust']
        self.sound_effects = dict()
        for sound in self.sound_effect_list:
            self.sound_effects[sound] = pygame.mixer.Sound(MusicBox.SOUND_EFFECT + sound + '.mp3')

    def read_all_sound_effect_names(self):
        all_sound_names = list(os.listdir("sound_effects/"))
        # remove '.mp3' part
        all_sound_names = [sound_name[:-4] for sound_name in all_sound_names]
        return all_sound_names

    def music_Q(self, music_file,
                repeat=False):  # 현재 재생되고 있는 음악을 확인하고 음악을 틀거나 말거나 결정해야 할때 check_playing_sound = True 로 줘야 함
        try:
            full_path = os.path.join(MusicBox.MUSIC_FOLDER, '%s.mp3' % music_file)
            pygame.mixer.music.load(full_path)
        except:
            full_path = os.path.join(MusicBox.MUSIC_FOLDER, '%s.wav' % music_file)
            pygame.mixer.music.load(full_path)

        pygame.mixer.music.set_volume(1)  # 0.5
        if repeat:
            pygame.mixer.music.play(-1)
        else:
            pygame.mixer.music.play()

    def collision_sound_effect(self, type1, type2):  # for fun! you cant hear sound in space tho
        # print("collision between {} and {} type".format(type1, type2))
        if type1 == 'gas' or type2 == 'gas':  # if they contain at least one gas type
            self.play_sound_effect('shruff')
        else:  # no gas planets
            if type1 == 'icy' or type2 == 'icy':  # at least one ice type
                self.play_sound_effect('glass_break')
            else:  # rocky, metal
                if type1 == 'metal' or type2 == 'metal':
                    self.play_sound_effect('metal')
                else:
                    self.play_sound_effect('fissure')

    def play_sound_effect(self, name, check_busy=False):
        if check_busy:
            if not self.sound_channel.get_busy():  # check busy일때는 사운드가 있다면 실행 x
                self.sound_channel.play(self.sound_effects[name])
        else:
            self.sound_channel.play(self.sound_effects[name])
        # self.sound_effects[name].play()


soundPlayer = MusicBox()
