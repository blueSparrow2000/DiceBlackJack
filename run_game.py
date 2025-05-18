from variables import *
import pygame
from gui import *
from util import *
from diceblackjack import DBJ
from time import sleep
import random

# pygame stuff
pygame.init()
font = pygame.font.SysFont('arial', 25)
# pygame stuff

class Simulator():
    def __init__(self,w=400,h=400):
        self.env = DBJ() # get the environment!
        self.env.set_verbose()

        self.w = w
        self.h = h

        self.display = pygame.display.set_mode((self.w, self.h),
                                               pygame.RESIZABLE | pygame.SRCALPHA)  # pygame.display.set_mode((self.w, self.h), pygame.SRCALPHA)
        pygame.display.set_caption('Dice BlackJack')

        self.mode_idx = 0
        self.mode_dict = {'Normal':'Normal dice blackjack', 'Break':"Can break 'one' dice in a roll, once per game except the last round"}# 'Freeze':"Can freeze a dice, which is assured number next turn, once per game"
        self.modes = list(self.mode_dict.keys())
        self.current_mode = [self.modes[self.mode_idx]]
        self.broke_dice = False
        self.froze_dice = False

        # trace option
        self.transparent_screen = pygame.Surface((self.w, self.h))
        self.transparent_screen.fill((40, 40, 40))
        self.transparent_screen.set_alpha(100)  # 0: transparent / 255: opaque

        self.dice_painter = DicePainter(self.w // 2, self.h // 2, 'Dice', initiial_dice=[4,3])
        self.dice_painter.draw(self.display)
        self.score_viewer = ScoreViewer(7*self.w // 8, self.h // 2)

        self.clock = pygame.time.Clock()

        ########## buttons ###########
        self.game_click_buttons = [Button(self, 'hit', self.w//4, 7*self.h//8, 'hit', button_length=100,color = (60,60,60), hover_color = (100,100,100)),Button(self, 'stand', 3*self.w//4, 7*self.h//8, 'stand', button_length=100,color = (60,60,60), hover_color = (100,100,100))]
        self.game_toggle_buttons = []

        self.end_click_buttons = [Button(self, 'yes', self.w//4, 7*self.h//8, 'yes', button_length=100,color = (80,80,80), hover_color = (120,120,120)),Button(self, 'no', 3*self.w//4, 7*self.h//8, 'no', button_length=100,color = (80,80,80), hover_color = (120,120,120))]
        self.end_toggle_buttons = []

        self.main_click_buttons = [Button(self, 'quit', self.w//2, 7*self.h//8, 'quit', button_length=100,color = (60,60,60), hover_color = (100,100,100)),Button(self, 'game_screen', self.w//2, 3*self.h//4, 'play', button_length=100,color = (60,60,60), hover_color = (100,100,100))]
        self.main_toggle_buttons = [ToggleButton(self, 'toggle_mode', self.w//2, self.h//2 + 50, 'Mode',toggle_variable = self.current_mode, toggle_text_dict = self.mode_dict,button_length=100, text_size=17,color = (60,60,60), hover_color = (100,100,100),move_ratio=[0.5,0.5])]

        self.main_buttons = self.main_click_buttons + self.main_toggle_buttons
        self.game_buttons = self.game_click_buttons + self.game_toggle_buttons
        self.end_buttons = self.end_click_buttons + self.end_toggle_buttons
        self.all_buttons = self.main_buttons + self.game_buttons + self.end_buttons

        ########## game variables ##########
        self.game_end = False
        self.win = False

        # main text
        self.game_name =  Text(self.w // 2, min(self.h // 8, 100), "Dice Black Jack", size=40, color=(160, 160, 160))

        # in game text
        self.turn_names = ["Your turn", "Dealer's turn"]
        self.turn_text = Text(self.w // 2, min(self.h // 8, 100), self.turn_names[0], size=40, color=(160, 160, 160))
        self.roll_sum_viewer = Text(self.w // 2, self.h//2, "0", size=80, color="darkgoldenrod")

        # end game text
        self.game_result_text = Text(self.w // 2, min(self.h // 8, 100), "You won", size=40, color=(180, 180, 180))
        self.replay_text = Text(self.w // 2, 3*self.h // 4, "Replay?", size=28, color=(150, 150, 150))

        # put all pause screen rects here! this includes interactable things like buttons! -> extract rects!
        self.end_screen_rects = [self.game_result_text.get_rect(),self.replay_text.get_rect()] # this is used to efficiently draw on pause screen
        for end_button in self.end_buttons+self.end_toggle_buttons:
            for item in end_button.get_all_rect():
                self.end_screen_rects.insert(0, item)

    def toggle_mode(self):
        self.mode_idx += 1
        if self.mode_idx == len(self.modes):
            self.mode_idx = 0
        self.current_mode[0] = self.modes[self.mode_idx]

    def initialize_game(self):
        self.env.reset()
        self.update_draw_dice(self.env.player_hand)
        self.score_viewer.update_score_viewer(self.env.get_hand_sums())
        self.game_end = False
        self.win = False
        self.broke_dice = False
        self.froze_dice = False

        #self.dice_painter

    def resize_window_updates(self):
        old_w, old_h = self.w, self.h
        self.w, self.h = self.display.get_width(), self.display.get_height()
        dx, dy = self.w - old_w, (self.h - old_h)

        # 투명 막 이동
        self.transparent_screen = pygame.Surface((self.w, self.h))
        self.transparent_screen.fill((40, 40, 40))
        self.transparent_screen.set_alpha(100)  # 0: transparent / 255: opaque

        # 모든 버튼의 위치 변경
        for buttons in self.all_buttons:
            buttons.move_to(dx, dy)

        # 주사위 그림 이동
        self.dice_painter.move_to(dx, dy)

        # score viewer 이동
        self.score_viewer.change_pos(7 * self.w // 8, self.h // 2)

        # 모든 텍스트 상자 이동
        self.turn_text.change_pos(self.w // 2, min(self.h // 8, 100))
        self.game_result_text.change_pos(self.w // 2, min(self.h // 8, 100))
        self.replay_text.change_pos(self.w // 2, 3 * self.h // 4)
        self.game_name.change_pos(self.w // 2, min(self.h // 8, 100))
        self.roll_sum_viewer.change_pos(self.w // 2, self.h//2)

    def button_function(self, button_list, function_name, *args):
        flag = None # false가 아닌 값이 하나라도 있다면 그 값을 리턴(무작위라 보면 됨. 버튼 순서에 따라 달라져서. 마지막 버튼의 리턴이 우선 - 근데 버튼은 안겹쳐 한번에 하나만 선택가능임)
        if len(args)==0: # no input
            for button in button_list:
                ret = getattr(button,function_name)()
                if ret:
                    flag = ret
        elif len(args)==1: # one input -> given as tuples
            for button in button_list:
                ret = getattr(button,function_name)(args[0])
                if ret:
                    flag = ret
        else: # multi inputs
            for button in button_list:
                ret = getattr(button,function_name)(args)
                if ret:
                    flag = ret
        return flag

    # button functions
    def hit(self):
        #action = 1
        roll, done = self.env.player_step(1)
        self.game_end_check(done)
        self.animate_roll(roll)
        self.score_viewer.update_score_viewer(self.env.get_hand_sums())

    def stand(self):
        #action = 0
        roll, done = self.env.player_step(0)
        self.game_end_check(done)
        self.score_viewer.update_score_viewer(self.env.get_hand_sums())

    def update_draw_dice(self, roll):
        self.dice_painter.change_content(roll)
        self.dice_painter.draw(self.display)
        pygame.display.update(self.dice_painter.get_rect())

    def animate_roll(self,roll):
        self.dice_painter.roll_sound()
        # animate only dice part (blit) : need to get rec to update blits
        frames = 10
        while frames>0:
            frames-=1
            self.dice_painter.draw_random_dice(self.display)
            pygame.display.update(self.dice_painter.get_rect())
            self.clock.tick(ANIMFPS)

        # assign text shower to show what number appeared
        self.update_draw_dice(roll)
        self.roll_sum_viewer.change_content(str(sum(roll)))
        self.roll_sum_viewer.write(self.display)
        pygame.display.update(self.dice_painter.get_rect()+[self.roll_sum_viewer.get_rect()])
        # short time sleep
        self.safe_sleep(0.7)

    def safe_sleep(self, amount):
        pygame.event.set_blocked(pygame.MOUSEBUTTONDOWN)
        sleep(amount)
        pygame.event.set_allowed(pygame.MOUSEBUTTONDOWN)

    def game_end_check(self,done):
        if done:
            self.game_end = True

    def yes(self):
        return True

    def no(self):
        return False

    def quit(self):
        pygame.quit()
        return False  # force quit

    def check_broke_dice(self):
        return self.broke_dice

    def check_froze_dice(self):
        return self.froze_dice

    def interact_dice(self, mousepos):
        if self.current_mode[0] == 'Break' and not self.check_broke_dice():
            collision = self.dice_painter.check_point_inside(mousepos)
            dice_nums = self.dice_painter.get_dice_nums()
            for i in range(2):
                if collision[i]:
                    self.dice_painter.break_sound()

                    self.broke_dice = True # now you cant break more dice

                    # revert the value of player hand
                    # print(self.env.player_hand)
                    self.env.modify_player_hand(i, dice_nums[i])

                    # print(self.env.player_hand)
                    # update score viewer
                    self.score_viewer.update_score_viewer(self.env.get_hand_sums())
                    # update dice painter
                    self.dice_painter.change_content([dice_nums[x]*int(not collision[x]) for x in range(2)])
                    # print(self.dice_painter.dice_images[0].filename)
                    # print(self.dice_painter.dice_images[1].filename)

        elif self.current_mode[0] == 'Freeze' and not self.check_froze_dice():
            pass



    def game_screen(self): # 2
        self.dice_painter.roll_sound()
        meta_run = True
        while meta_run:
            self.button_function(self.game_toggle_buttons, 'initialize')
            self.initialize_game()

            normal_game_end = True
            # player turn
            self.turn_text.change_content(self.turn_names[0])
            while not self.game_end:
                quit = self.animate_frame()
                if quit:
                    normal_game_end = False
                    meta_run = False
                    break

            if normal_game_end:
                # self.turn_text.change_content("")
                # self.animate_frame(click_available = False) # redraw
                if not self.env.player_burst():# dealer turn -> if not player burst
                    # draw initial dealer's dice
                    self.turn_text.change_content(self.turn_names[1])
                    self.update_draw_dice(self.env.dealer_initial_roll)
                    self.animate_frame(click_available = False)
                    self.safe_sleep(1.4)
                    # dealer step
                    done = False
                    while not done:
                        self.animate_frame(click_available = False)
                        roll, done = self.env.dealer_step()
                        self.game_end_check(done)
                        if roll:
                            self.animate_roll(roll)
                        self.score_viewer.update_score_viewer(self.env.get_hand_sums())

                # after game end
                pygame.mixer.pause()
                self.turn_text.change_content("")
                self.animate_frame(click_available = False) # redraw
                meta_run = self.game_end_screen()  # true여야 계속 게임 진행
                pygame.mixer.unpause()

        return True

    def animate_frame(self, click_available = True):
        # 1. collect user input
        mousepos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.WINDOWRESIZED:
                self.resize_window_updates()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # esc 키를 누르면 메인 화면으로
                    return True
            if event.type == pygame.MOUSEMOTION:
                mousepos = pygame.mouse.get_pos()
                self.button_function(self.game_buttons, 'hover_check', mousepos)

            if event.type == pygame.MOUSEBUTTONUP and click_available:  # 마우스를 뗼떼 실행됨
                mousepos = pygame.mouse.get_pos()
                self.interact_dice(mousepos)
                if self.button_function(self.game_click_buttons, 'check_inside_button', mousepos):
                    return self.button_function(self.game_click_buttons, 'on_click', mousepos) # 아무것도 리턴하지 않아야 함

        self.display.fill(BLACK)

        if (self.current_mode[0] == 'Break' and not self.check_broke_dice()) or (self.current_mode[0] == 'Freeze' and not self.check_froze_dice()) :
            # print(self.check_broke_dice())
            self.dice_painter.highlight(mousepos, self.display)

        self.turn_text.write(self.display)

        self.dice_painter.draw(self.display)
        self.button_function(self.game_buttons, 'draw_button', self.display)

        self.score_viewer.write(self.display)

        pygame.display.flip()
        self.clock.tick(FPS)

    def game_end_screen(self): #4 show commands and how to use this simulator
        # draw transparent screen - stop increasing time, only clock tick for interaction, but still can click buttons, update display for buttons
        # increase FPS -> 토글로 할지 슬라이더로 조작할지 버튼으로 올릴지 나중에 선택 / toggle v,t -> button text 바뀜 / toggle simulation method / trail length
        self.display.blit(self.transparent_screen, (0, 0))
        pygame.display.flip()
        self.button_function(self.end_toggle_buttons, 'initialize')

        # verify winner
        if self.env.get_reward() > 0:
            # player win
            self.game_result_text.change_content("You won")
            soundPlayer.play_sound_effect('confirm')
        elif self.env.get_reward() == 0:
            # tie
            self.game_result_text.change_content("Tie")
            soundPlayer.play_sound_effect('shruff')
        else:
            # player lost
            self.game_result_text.change_content("You lost")
            soundPlayer.play_sound_effect('thmb')

        while 1:
            # collect user input
            events = pygame.event.get()
            keys = pygame.key.get_pressed()  # 꾹 누르고 있으면 계속 실행되는 것들 # SHOULD BE CALLED AFTER pygame.event.get()!
            # handle events
            for event in events:
                if event.type == pygame.QUIT:  # 윈도우를 닫으면 main으로
                    # pygame.quit()
                    return False  # main
                if event.type == pygame.WINDOWRESIZED:
                    self.resize_window_updates()
                    self.display.blit(self.transparent_screen, (0, 0))
                    pygame.display.flip() # if resize is done, redraw everything
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                        return False  # main
                if event.type == pygame.MOUSEMOTION:
                    mousepos = pygame.mouse.get_pos()
                    self.button_function(self.end_buttons, 'hover_check', mousepos)
                if event.type == pygame.MOUSEBUTTONUP:  # 마우스를 뗼떼 실행됨
                    mousepos = pygame.mouse.get_pos()
                    self.button_function(self.end_toggle_buttons, 'on_click', mousepos) # toggle은 리턴값을 안씀
                    if self.button_function(self.end_click_buttons, 'check_inside_button', mousepos):
                        return self.button_function(self.end_click_buttons, 'on_click', mousepos) # False: main / True: Play again

            self.button_function(self.end_buttons, 'draw_button', self.display)
            self.game_result_text.write(self.display)
            self.replay_text.write(self.display)
            pygame.display.update(self.end_screen_rects)
            # pygame.event.pump() # in case update does not work properly
            self.clock.tick(SLOWFPS)


    def main_screen(self): # 1 -> pause screen과 유사 토글로 맵 종류 바꾸기
        self.button_function(self.main_toggle_buttons, 'initialize')

        while 1:

            # collect user input
            events = pygame.event.get()
            keys = pygame.key.get_pressed()  # 꾹 누르고 있으면 계속 실행되는 것들 # SHOULD BE CALLED AFTER pygame.event.get()!
            # handle events
            for event in events:
                if event.type == pygame.QUIT:  # 종료
                    pygame.quit()
                    return False  # force quit
                if event.type == pygame.WINDOWRESIZED:
                    self.resize_window_updates()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:  # 종료
                        pygame.quit()
                        return False  # quit
                if event.type == pygame.MOUSEMOTION:
                    mousepos = pygame.mouse.get_pos()
                    self.button_function(self.main_buttons, 'hover_check', mousepos)
                if event.type == pygame.MOUSEBUTTONUP:  # 마우스를 뗄때 실행됨
                    mousepos = pygame.mouse.get_pos()
                    self.button_function(self.main_toggle_buttons, 'on_click', mousepos) # toggle은 리턴값을 안씀
                    if self.button_function(self.main_click_buttons, 'check_inside_button', mousepos):
                        pygame.mixer.music.stop()
                        return self.button_function(self.main_click_buttons, 'on_click', mousepos) # False: main / True: Play again

            self.display.fill(BLACK)

            self.button_function(self.main_buttons, 'draw_button', self.display)
            self.game_name.write(self.display)
            pygame.display.flip()
            self.clock.tick(SLOWFPS)


if __name__=="__main__":
    sim = Simulator()

    run = True
    while run:
        soundPlayer.music_Q('Chill', True)
        run = sim.main_screen()





