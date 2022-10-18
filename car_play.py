import sys

import pygame

from car import Car
from settings import Settings


class CarPlay:
    def __init__(self):
        self.settings = Settings()

        # 初始化pygame
        pygame.init()
        pygame.joystick.init()
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        self.car = Car(self)

    def play(self):
        """开始控制"""
        self.car.initialize()
        while True:
            self._check_controller_events()
            self.car.update_controller()

    def _check_controller_events(self):
        """
        判断输入类型
        """
        for event in pygame.event.get():
            # 退出
            if event.type == pygame.QUIT:
                sys.exit()
            # 按键按下
            elif event.type == pygame.JOYBUTTONDOWN:
                self._check_joy_button_down(event)
            # 按键松开
            elif event.type == pygame.JOYBUTTONUP:
                self._check_joy_button_down(event)
            # 拨动摇杆
            elif event.type == pygame.JOYAXISMOTION:
                self._check_joy_axis_motion(event)

    def _check_joy_axis_motion(self, event):
        """
        摇杆和扳机控制
        """
        # 控件与axis序号的对应关系：
        # LS 0（左-1,右1）,1（上-1,下1）；RS 2（左-1,右1） 3（上-1,下1）；
        # LT 5（顶-1,底1）, RT 4（顶-1,底1）,按下扳机前读到的初始值为0，之后为-1

        # 左扳机控制速度大小
        # 按下扳机前会读到0,而非-1,导致马达转动，所以把0忽略掉
        if self.joystick.get_axis(5) != 0:
            self.settings.speed_axis_pos = self.joystick.get_axis(5)
            self.settings.logger.info(f'左扳机读数:{self.settings.speed_axis_pos}\n')

        # 右扳机控制刹车
        if self.joystick.get_axis(4) > 0:
            self.car.motor_stop()
        else:
            self.car.moving_stop = False

        # 左摇杆控制转向
        left_stick_x = self.joystick.get_axis(0)
        # 左转右转
        # 当上次转向调整完成后才开始新的一轮转向控制
        if self.settings.steer_finish_flag:
            self.settings.steer_axis_pos = left_stick_x
            self.settings.logger('-----------------------------------------')
            self.settings.logger(f'摇杆读数:{self.settings.steer_axis_pos}\n')
            self.settings.steer_axis_flag = True
            self.car.steer()

    def _check_joy_button_down(self, event):
        """
        按键事件，控制前进后退
        """
        # A0 B1 X3 Y4
        # button_y = self.joystick.get_button(4)
        # button_x = self.joystick.get_button(3)
        button_b = self.joystick.get_button(1)
        button_a = self.joystick.get_button(0)
        # Y 前进 X 后退
        # 前进后退
        if button_a:
            self.car.moving_back = True
        elif button_b:
            self.car.moving_forward = True
        else:
            self.car.moving_back = False
            self.car.moving_forward = False

    def destroy(self):
        """释放资源"""
        self.car.destroy()


if __name__ == '__main__':
    car = CarPlay()
    try:
        car.play()
    except KeyboardInterrupt:
        sys.exit()
    finally:
        car.destroy()  # 释放资源
