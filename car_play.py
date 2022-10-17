import sys
import pygame
import RPi.GPIO as GPIO
from settings import Settings
from car import Car


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
            # self.car.update()

    def _check_controller_events(self):
        """
        判断输入类型
        """
        for event in pygame.event.get():
            # 退出
            if event.type == pygame.QUIT:
                sys.exit()
            # # 按键按下
            # elif event.type == pygame.JOYBUTTONDOWN:
            #     self._check_joy_button_down(event)
            # # 按键松开
            # elif event.type == pygame.JOYBUTTONUP:
            #     self._check_joy_button_down(event)
            # 拨动摇杆
            elif event.type == pygame.JOYAXISMOTION:
                self._check_joy_axis_motion(event)

    def _check_joy_axis_motion(self, event):
        """
        摇杆控制
        """
        # 控件与axis序号的对应关系：
        # LS 0（左-1,右1）,1（上-1,下1）；RS 2（左-1,右1） 3（上-1,下1）；
        # LT 5（顶-1,底1）, RT 4（顶-1,底1）,按下扳机前读到的初始值为0，之后为-1

        # 左摇杆控制转向
        left_stick_x = self.joystick.get_axis(0)
        # 左转右转
        # 当上次转向调整完成后才开始新的一轮转向控制
        if self.settings.steer_finish_flag:
            self.settings.steer_axis_pos = left_stick_x
            print('-----------------------------------------')
            print(f'摇杆读数:{self.settings.steer_axis_pos}\n')
            self.settings.steer_axis_flag = True
            self.car.steer()


if __name__ == '__main__':
    try:
        car = CarPlay()
        car.play()
    except KeyboardInterrupt:
        sys.exit()
    finally:
        GPIO.cleanup()  # 清理释放GPIO资源，将GPIO复位
