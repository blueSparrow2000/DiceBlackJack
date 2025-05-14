import random
from variables import *
import pygame


class DBJ():
    burst_num = 21
    def __init__(self,w=700,h=700):
        self.actions = [0,1] # 0,1
        self.states = [i for i in range(2,22)]# 2~21 valid states
        self.dice = [i+1 for i in range(6)]

        self.player_hand=self.roll()
        self.dealer_hand=self.roll()

        self.verbose = False
        self.animate = False

        self.w = w
        self.h = h
        # init display
        if self.animate:
            self.display = pygame.display.set_mode((self.w, self.h),
                                                   pygame.RESIZABLE | pygame.SRCALPHA)  # pygame.display.set_mode((self.w, self.h), pygame.SRCALPHA)
            pygame.display.set_caption('Dice BlackJack')

        self.clock = pygame.time.Clock()
        # self.display.fill((0, 0, 0))

        self.click_button = []
        self.toggle_button = []

        self.all_buttons = self.click_button + self.toggle_button

    def set_verbose(self):
        self.verbose = True

    def animate(self):
        self.animate = True

    def resize_window_updates(self):
        old_w, old_h = self.w, self.h
        self.w, self.h = self.display.get_width(), self.display.get_height()
        dx, dy = self.w - old_w, (self.h - old_h)

        self.transparent_screen = pygame.Surface((self.w, self.h))
        self.transparent_screen.fill((40, 40, 40))
        self.transparent_screen.set_alpha(100) # 0: transparent / 255: opaque

        # 모든 버튼의 위치 변경
        for buttons in self.all_buttons:
            buttons.move_to(dx, dy)

    def compare(self,a,b):
        return float(a>b)-float(a<b)

    def roll(self):
        return [int(random.choice(self.dice)) for i in range(2)]

    def sum_hand(self,h):
        return sum(h)

    def is_burst(self,h):
        return self.sum_hand(h) > DBJ.burst_num

    def hand_score(self,h):
        return 0 if self.is_burst(h) else self.sum_hand(h)

    def get_player_hand(self):
        return self.sum_hand(self.player_hand)

    def get_dealer_hand(self):
        return self.sum_hand(self.dealer_hand)

    def get_observation(self):
        return self.hand_score(self.player_hand)

    def reset(self):
        self.player_hand=self.roll() # roll initially
        self.dealer_hand=self.roll()
        if self.verbose:
            print("Reset")
            print("Dealer: {:2d} | Player: {:2d}".format(self.sum_hand(self.dealer_hand),
                                                               self.sum_hand(self.player_hand)))

        # 3. update ui and clock
        if self.animate:
            self._update_ui()
            self.clock.tick(SPEED)

        return self.get_observation()

    '''
    action is expected to be 1 (hit) or 0 (stand)
    '''
    def step(self,action):
        # 1. collect user input
        if self.animate:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if self.animate and event.type == pygame.WINDOWRESIZED:
                    self.resize_window_updates()
                # if event.type == pygame.KEYDOWN:
                #     if event.key == pygame.K_ESCAPE:  # esc 키를 누르면 메인 화면으로
                #         return False  # goto main
                # if event.type == pygame.MOUSEMOTION:
                #     mousepos = pygame.mouse.get_pos()
                #     self.button_function(min_display_buttons, 'hover_check', mousepos)
                # if event.type == pygame.MOUSEBUTTONUP:  # 마우스를 뗼떼 실행됨
                #     mousepos = pygame.mouse.get_pos()
                #     if self.button_function(min_display_buttons, 'check_inside_button', mousepos):
                #         return self.button_function(min_display_buttons, 'on_click', mousepos) # 이게 에러를 냄. 바로 pygame quit시 none을 리턴

        # 2. simulate step
        obs, reward, done = self.animated_train_step(action)

        # 3. update ui and clock
        if self.animate:
            self._update_ui()
            self.clock.tick(SPEED)

        # 4. print current step info
        if self.verbose:
            print("Dealer: {:2d} | Player: {:2d} |Reward: {:.1f}".format(self.get_dealer_hand(), self.get_player_hand(), reward))
            if done:
                print("END episode\n")

        return self.get_observation(), reward, done

    '''
    light weight function that plays only an essential step
    used for training NN model 
    '''
    def train_step(self, action):
        reward=0
        done=False
        if action: # hit
            self.player_hand += self.roll()
            if self.is_burst(self.player_hand):
                done=True
                reward=-1
        else: # stand
            done=True
            stop_dealer_hit_threshold = self.sum_hand(self.player_hand)
            while self.sum_hand(self.dealer_hand) < stop_dealer_hit_threshold:  # hit
                self.dealer_hand += self.roll()
            reward = self.compare(self.hand_score(self.player_hand), self.hand_score(self.dealer_hand))

        # print current step info
        if self.verbose:
            print("Dealer: {:2d} | Player: {:2d} |Reward: {:.1f}".format(self.get_dealer_hand(), self.get_player_hand(), reward))
            if done:
                print("END episode\n")
        return self.get_observation(), reward, done

    def animated_train_step(self, action):
        reward = 0
        done = False
        if action:  # hit
            roll = self.roll()
            self.player_hand += roll
            print("You rolled {} and {}\nYour hand: {:2d}\n".format(roll[0], roll[1], self.get_player_hand()))
            if self.is_burst(self.player_hand):
                done = True
                reward = -1
                print("You burst!")
        else:  # stand
            print("="*30,"Dealer's Turn","="*30)
            done = True
            stop_dealer_hit_threshold = self.sum_hand(self.player_hand)
            while self.sum_hand(self.dealer_hand) < stop_dealer_hit_threshold:  # hit
                roll = self.roll()
                self.dealer_hand += roll
                print("Dealer rolled {} and {}\nDealer hand: {:2d}\n".format(roll[0],roll[1], self.get_dealer_hand()))
                if self.animate:
                    ### do dealer animation
                    ###
                    self._update_ui()
                    self.clock.tick(SPEED)

            reward = self.compare(self.hand_score(self.player_hand), self.hand_score(self.dealer_hand))
        return self.get_observation(), reward, done

    def _update_ui(self):
        # self.display.fill(BLACK)
        #
        # for pt in self.snake:
        #     pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
        #     pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x + 4, pt.y + 4, 12, 12))
        #
        # pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))
        #
        # text = font.render("Score: " + str(self.score), True, WHITE)
        # self.display.blit(text, [0, 0])
        pygame.display.flip()











