# coding=utf-8
import time
import pygame
from pygame.locals import *
import random
from PIL import Image, ImageDraw, ImageFont


class Base(object):
    def __init__(self, screen, x, y, width, height):
        # 坐标
        self.x = x
        self.y = y
        # 块本身的高和宽
        self.width = width
        self.height = height
        # 设置要显示内容的窗口
        self.screen = screen


class Block(Base):
    def __init__(self, screen, x, y, width=46, height=44):
        super(Block, self).__init__(screen, x, y, width, height)
        self.isbomb = False
        # 块所处的位置，用序号表示
        self.number = 0
        # 每个块都有很多状态，这是每个状态需要的图片
        self.image_paths = ["./resource/1.png", "./resource/2.png", "./resource/3.png"
                      , "./resource/4.png", "./resource/5.png", "./resource/6.png"
                      , "./resource/7.png","./resource/8.png", "./resource/isbomb.png"
                      , "./resource/ifitisbomb.png", "./resource/top.png","./resource/empty.png"]
        # 与状态关联的图片，预加载，避免卡顿
        self.images = self.load_images()
        # 块所处的状态   默认是顶层未点击状态
        self.DEFAULT_STATE = 11
        self.state = self.DEFAULT_STATE

    def reset_state(self):
        self.state = self.DEFAULT_STATE

    # 返回字典类型，key值对应图像状态，value对应图像
    def load_images(self):
        i = 1
        images = {}
        # 此层循环可以用枚举实现,这样不用自己维护索引  待有空再改
        for image_path in self.image_paths:
            image = pygame.image.load(image_path).convert()
            images[i] = image
            i += 1
        return images

    def change_state(self, button):
        """
        改变块所处的状态
        :param button:  鼠标的有效点击，一般为  "left"   "right"   "center"
        :return:
        """
        if self.state > 8 and self.state != 12:
            if button == "right":
                if self.state != 9:
                    self.state = 9
                else:
                    self.state = 11
            elif button == "center":
                if self.state != 10:
                    self.state = 10
                else:
                    self.state = 11

    def in_me(self, x, y):
        """
        判断鼠标是否点击了本块
        :param x: 鼠标点击的横坐标
        :param y: 鼠标点击的纵坐标
        :return:  返回是否点击的本块
        """
        if self.x<= x <=self.x+self.width and self.y<= y <= self.y+self.height:
            return True
        else:
            return False

    def display(self):
        """
        根据本块的状态显示本块
        :return:
        """
        self.screen.blit(self.images[self.state], (self.x, self.y))


class Buttom(Base):
    def __init__(self, screen, x, y, width, height, image_path):
        super(Buttom, self).__init__(screen, x, y, width, height)
        self.image = pygame.image.load(image_path).convert()

    def in_me(self, x, y):
        if self.x <= x <= self.x+self.width and self.y <= y <= self.y+self.height:
            return True
        else:
            return False

    def display(self):
        self.screen.blit(self.image, (self.x, self.y))


class GameOver(object):
    def __init__(self, screen):
        self.quit = Buttom(screen,296, 302, 67, 38, "./resource/quit.png")
        self.restart = Buttom(screen, 59, 300, 123, 44, "./resource/restart.png")
        self.info = Buttom(screen,102, 93, 0, 0, "./resource/fail.png")
        """
        1 表示即不退出，也不重新开始
        0 表示退出
        2 表示重新开始
        """
        self.quit_or_restart = 1

    def action(self, x, y):
        if self.quit.in_me(x, y):
            self.quit_or_restart = 0
        if self.restart.in_me(x, y):
            self.quit_or_restart = 2

    def display(self):
        self.quit.display()
        self.restart.display()
        self.info.display()


class GameWin(object):
    def __init__(self, screen):
        self.screen = screen
        # 标题，闯关成功
        self.title = Buttom(screen, 106, 64, 244, 120, "./resource/success_info.png")
        # 下一关
        self.next_level = Buttom(screen, 132, 321, 187, 101, "./resource/next_level.png")
        # 成绩
        self.grade = None

    def in_next_level_block(self, x, y):
        if self.next_level.in_me(x, y):
            return True
        else:
            return False

    def display(self):
        self.title.display()
        self.next_level.display()
        self.grade.display()

    def generate_photo_of_grade(self, grade):
        image = Image.new(mode='RGBA', size=(281, 60), color="#ffffff")
        draw_table = ImageDraw.Draw(im=image)
        draw_table.text(xy=(0, 0), text=grade+"S", fill='#000000', font=ImageFont.truetype('./resource/fang_song.ttf', 50))
        image.save('./resource/grade.png', 'PNG')
        image.close()
        self.grade = Buttom(self.screen, 162, 206, 0, 0, "./resource/grade.png")


class ControlCenter(object):
    """
    用于数据控制，控制所有块的数据操作，以及游戏状态变换
    """
    def __init__(self, screen):
        self.screen = screen
        self.blocks = None
        self.number_of_bomb = 15
        """
        1 表示不知胜败
        0 表示失败
        2 表示成功
        """
        self.win = 1
        self.start_time = time.time()
        self.init_blocks()

    def get_number_of_blocks_have_not_been_clicked(self):
        """
        获取所有块中依然处于未点击状态的块的数量
        :return: 微电机状态的块的数量
        """
        number = 0
        for block in self.blocks:
            if block.state in [9, 10, 11]:
                number += 1
        return number

    def init_blocks(self):
        """
        初始化所有的块
        :return:
        """
        blocks = []
        # 生成100个块
        for i in range(10):
            for j in range(10):
                block = Block(self.screen, j * 46, i * 44)
                block.number = i * 10 + j
                blocks.append(block)
        self.blocks = blocks
        numbers = self.get_bomb_block_numbers()
        # 生成n个随机雷
        for i in range(self.number_of_bomb):
            self.blocks[numbers[i]].isbomb = True

    def get_grade(self):
        end_time = time.time()
        return end_time - self.start_time

    def get_the_block_from_coordinate(self, x, y):
        """
        通过鼠标点击的坐标直接获得所点击的block
        :param x:
        :param y:
        :return:
        """
        block_to_manage = self.blocks[0]
        number_of_clicked = int(x/block_to_manage.width) + int(y/block_to_manage.height)*10
        return self.blocks[number_of_clicked ]

    def get_bomb_block_numbers(self):
        """
        随机生成self.number_of_bomb个雷
        :return: 雷块的位置
        """
        numbers = []
        while True:
            number = random.randint(0,99)
            numbers.append(number)
            numbers = list(set(numbers))
            if len(numbers) == self.number_of_bomb:
                break
        return numbers

    @staticmethod
    def get_close_block_number(block):
        """
        得到block周围的所有块的位置
        :param block: 需要判断的块
        :return: 周围块的位置
        """
        number = block.number
        if number%10 == 0:
            numbers = [number+1, number+10, number-10, number-9,number+11]
        elif number%10 == 9:
            numbers = [number-10, number-11, number-1, number+9, number+10]
        else:
            numbers = [number+1, number+10, number-10, number-9,number+11, number-11, number-1, number+9 ]

        ret = []
        for item in numbers:
            if 0 <= item <= 99:
                ret.append(item)
        return ret

    @staticmethod
    def get_time_of_play_game(start_time):
        """
        获取玩家玩游戏的时间
        :param start_time: 起始时间
        :return: 时间间隔
        """
        end_time = time.time()
        duration = end_time - start_time
        place_of_dot = str(duration).index('.')
        return duration[0: place_of_dot+4]

    def reset(self):
        """
        重置游戏到开始状态
        :return:
        """
        # 重置游戏状态
        self.win = 1
        # 重置游戏开始时间
        self.start_time = time.time()
        # 重置所有的块信息
        for block in  self.blocks:
            block.reset_state()
        numbers = self.get_bomb_block_numbers()
        # 重置炸弹块
        for i in range(len(self.blocks)):
            self.blocks[i].isbomb = False
        for i in range(self.number_of_bomb):
            self.blocks[numbers[i]].isbomb = True

    def display(self):
        """
        显示所有块
        :return:
        """
        for block in self.blocks:
            block.display()


def main():
    # 1. 创建一个窗口，用来显示内容
    screen = pygame.display.set_mode((460, 440), 0, 32)

    # 2. 创建一个和窗口大小的图片，用来充当背景
    background = pygame.image.load("./resource/background.png").convert()

    control_center = ControlCenter(screen)
    game_over = GameOver(screen)
    game_win = GameWin(screen)
    # 退出标识
    exit_flag = False
    while not exit_flag:

        # 设定需要显示的背景图
        screen.blit(background, (0, 0))
        # 对鼠标，键盘事件进行监听判断
        for event in pygame.event.get():

            if event.type == QUIT:
                    # 退出
                    exit_flag = True
                    break
            if control_center.win == 1:
                # 输赢状态不知
                left, center, right = pygame.mouse.get_pressed()
                if left:  # 左键点击
                    # print "left  clicked"
                    x, y = pygame.mouse.get_pos()
                    block_clicked = None
                    for block in control_center.blocks:
                        if block.in_me(x, y):
                            block_clicked = block
                            # print "find the block clicked"

                    if block_clicked.isbomb:
                        # 点到炸弹
                        control_center.win = 0
                    # 用于处理本块周围的block的栈井
                    stack_wall = []
                    stack_wall.append(block_clicked)
                    has_been_managed = []
                    while stack_wall:
                        # print "yes"
                        block = stack_wall.pop()
                        if block not in has_been_managed:
                            has_been_managed.append(block)
                        numbers = control_center.get_close_block_number(block)
                        # # print numbers
                        number_of_close_bomb = 0
                        for number in numbers:
                            if control_center.blocks[number].isbomb:
                                number_of_close_bomb += 1
                        # print number_of_close_bomb
                        if number_of_close_bomb == 0:
                            for number in numbers:
                                if control_center.blocks[number] not in has_been_managed:
                                    stack_wall.append(control_center.blocks[number])
                            block.state = 12
                        else:
                            block.state = number_of_close_bomb
                            # print block.state
                if center:
                    x, y = pygame.mouse.get_pos()
                    block_clicked = control_center.get_the_block_from_coordinate(x, y)
                    block_clicked.change_state("center")
                elif right:
                    x, y = pygame.mouse.get_pos()
                    block_clicked = control_center.get_the_block_from_coordinate(x, y)
                    block_clicked.change_state("right")

            elif control_center.win == 0:
                left, center, right = pygame.mouse.get_pressed()
                if left:
                    x, y = pygame.mouse.get_pos()
                    game_over.action(x, y)

                if game_over.quit_or_restart == 0:
                    # 退出
                    exit_flag = True
                    break
                elif game_over.quit_or_restart == 2:
                    # 重新开始
                    control_center.reset()
                    game_over.quit_or_restart = 1
                # print("game over")
            else:
                # 游戏成功
                left, center, right = pygame.mouse.get_pressed()
                if left:
                    x, y = pygame.mouse.get_pos()
                    if game_win.in_next_level_block(x, y):
                        control_center.reset()

        if control_center.get_number_of_blocks_have_not_been_clicked() == control_center.number_of_bomb and control_center.win == 1:
            grade = str(control_center.get_grade())
            place_of_dot = grade.index(".")
            grade = grade[0: place_of_dot+4]
            game_win.generate_photo_of_grade(grade)
            control_center.win = 2

        if control_center.win == 1:
            control_center.display()
        elif control_center.win == 0:
            game_over.display()
        else:
            game_win.display()
        pygame.display.update()
        time.sleep(0.03)  # 用于控制帧数


if __name__ == "__main__":
    main()
