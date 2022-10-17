import RPi.GPIO as GPIO
import time
import numpy
import logging


class Car:
    """小车类"""

    def __init__(self, car_play):
        self.settings = car_play.settings

        self.steer_angle = 0  # 车轮转向角度，0度为正前，左负右正

        self.moving_right = False
        self.moving_left = False
        self.moving_forward = False
        self.moving_back = False
        self.moving_stop = False
        self.speed_up = False
        self.slow_down = False
        # 创建PWM对象，并指定初始频率
        self.pwm_steer = GPIO.PWM(self.settings.steer_pin, self.settings.steer_freq)

    def initialize(self):
        """初始化"""
        self.pwm_steer.start(self.settings.steer_dc)  # 启动PWM，并指定初始占空比
        time.sleep(0.04)  # 等待控制周期结束
        self.pwm_steer.ChangeDutyCycle(0)  # 清空占空比，防止抖动

    def steer(self):
        """转向"""
        # 开始调整前将转向完成标志置零
        self.settings.steer_finish_flag = False
        # 根据占空比与轴读数的关系式计算目标占空比,并圆整至一位小数，防止频繁改变占空比导致的抖动
        target_steer_dc = round(-1.5 * self.settings.steer_axis_pos + 7.5, 1)
        # 计算目标值与当前的偏差
        steer_dc_delta = target_steer_dc - self.settings.steer_dc_last

        logging.info(f"占空比计算结果:{target_steer_dc}")
        logging.info(f"最后一次转向占空比:{self.settings.steer_dc_last}\n")
        logging.info(f"占空比差值:{steer_dc_delta}")

        # 当转向与目标存在偏差时进行调整
        i = 0  # 调整次数
        while steer_dc_delta:
            # 按0.1的步长进行调整，使转向平稳
            self.settings.steer_dc_last += numpy.sign(steer_dc_delta) * self.settings.steer_dc_step
            self.settings.steer_dc_last = round(self.settings.steer_dc_last, 1)
            self._steer_dc_change(self.settings.steer_dc_last)
            steer_dc_delta = target_steer_dc - self.settings.steer_dc_last
            i += 1
            logging.info(f"\t第{i}次调整：{self.settings.steer_dc_last}")

        self.settings.steer_finish_flag = True  # 此次转向调整完成

    def _steer_dc_change(self, steer_dc):
        """调整舵机角度"""
        self.pwm_steer.ChangeDutyCycle(steer_dc)
        time.sleep(0.02)  # 等待控制周期
        self.pwm_steer.ChangeDutyCycle(0)  # 清空占空比，防止抖动
