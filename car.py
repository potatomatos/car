import RPi.GPIO as GPIO
import time
import numpy


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
        # 创建舵机PWM对象，并指定初始频率
        self.pwm_steer = GPIO.PWM(self.settings.steer_pin, self.settings.steer_freq)
        # 创建电机PWM对象，并指定初始频率
        self.pwm_motor = GPIO.PWM(self.settings.motor_pin_ENA, self.settings.motor_freq)

    def initialize(self):
        """初始化"""
        self.pwm_steer.start(self.settings.steer_dc)  # 启动PWM，并指定初始占空比
        time.sleep(0.04)  # 等待控制周期结束
        self.pwm_steer.ChangeDutyCycle(0)  # 清空占空比，防止抖动
        self.pwm_motor.start(self.settings.motor_dc)  # 启动PWM，并指定初始占空比
        self.motor_stop()  # 初始化状态为静止

    def steer(self):
        """转向"""
        # 开始调整前将转向完成标志置零
        self.settings.steer_finish_flag = False
        # 根据占空比与轴读数的关系式计算目标占空比,并圆整至一位小数，防止频繁改变占空比导致的抖动
        x = 0
        if self.settings.steer_axis_pos > 0:
            x = 1.5
        if self.settings.steer_axis_pos < 0:
            x = 3.5
        target_steer_dc = round(x * self.settings.steer_axis_pos + 7.5, 1)
        # 计算目标值与当前的偏差
        steer_dc_delta = target_steer_dc - self.settings.steer_dc_last

        self.settings.logger.info(f"占空比计算结果:{target_steer_dc}")
        self.settings.logger.info(f"最后一次转向占空比:{self.settings.steer_dc_last}\n")
        self.settings.logger.info(f"占空比差值:{steer_dc_delta}")

        # 当转向与目标存在偏差时进行调整
        i = 0  # 调整次数
        while steer_dc_delta:
            # 按0.1的步长进行调整，使转向平稳
            self.settings.steer_dc_last += numpy.sign(steer_dc_delta) * self.settings.steer_dc_step
            self.settings.steer_dc_last = round(self.settings.steer_dc_last, 1)
            self._steer_dc_change(self.settings.steer_dc_last)
            steer_dc_delta = target_steer_dc - self.settings.steer_dc_last
            i += 1
            self.settings.logger.info(f"\t第{i}次调整：{self.settings.steer_dc_last}")

        self.settings.steer_finish_flag = True  # 此次转向调整完成

    def _steer_dc_change(self, steer_dc):
        """调整舵机角度"""
        self.pwm_steer.ChangeDutyCycle(steer_dc)
        time.sleep(0.02)  # 等待控制周期
        self.pwm_steer.ChangeDutyCycle(0)  # 清空占空比，防止抖动

    def update_controller(self):
        """对手柄控制电机的响应"""
        if not self.moving_stop:
            self.pwm_motor.start(self.settings.motor_dc)  # 防止之前已经关闭电机PWM
            # 变速  axis value: -1 -> 1 turn to 0->2   # speed： 0-2 ，dc：0-100
            self.settings.motor_dc = 50 * (self.settings.speed_axis_pos + 1)
            self.pwm_motor.ChangeDutyCycle(self.settings.motor_dc)
            #  前进 后退
            if self.moving_forward:
                GPIO.output(self.settings.motor_pin_IN1, GPIO.HIGH)
                GPIO.output(self.settings.motor_pin_IN2, GPIO.LOW)
            elif self.moving_back:
                GPIO.output(self.settings.motor_pin_IN1, GPIO.LOW)
                GPIO.output(self.settings.motor_pin_IN2, GPIO.HIGH)

    def motor_stop(self):
        """调整舵机角度"""
        self.moving_stop = True
        self.moving_forward = False
        self.moving_back = False
        self.settings.motor_dc = 0
        self.pwm_motor.ChangeDutyCycle(self.settings.motor_dc)
        # 两个都输入低电平电机则停止
        GPIO.output(self.settings.motor_pin_IN1, GPIO.LOW)
        GPIO.output(self.settings.motor_pin_IN2, GPIO.LOW)

    def destroy(self):
        """释放资源"""
        self.pwm_steer.stop()
        self.pwm_motor.stop()
        GPIO.cleanup()  # 清理释放GPIO资源，将GPIO复位
