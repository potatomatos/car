import RPi.GPIO as GPIO  # 引入GPIO模块
import logging


class Settings:
    """存储设置的类"""

    def __init__(self):
        """初始化静态设置"""
        logging.basicConfig(level=logging.INFO)  # 设置日志级别
        self.logger = logging
        GPIO.setmode(GPIO.BCM)  # 使用BCM编号方式

        # 舵机配置
        self.steer_pin = 17  # 转向舵机PWM引脚
        self.steer_freq = 50  # 舵机PWM频率
        self.steer_dc = 7.5  # 舵机PWM占空比
        GPIO.setup(self.steer_pin, GPIO.OUT)  # 将GPIO设置为输出模式

        # 电机配置
        """
            IN1 & IN2 电机驱动器A的输入引脚，控制电机A转动及旋转角度
            IN1输入高电平HIGH，IN2输入低电平LOW，对应电机A正转
            IN1输入低电平LOW，IN2输入高电平HIGH，对应电机A反转
            IN1、IN2同时输入高电平HIGH或低电平LOW，对应电机A停止转动
            调速就是改变IN1、IN2高电平的占空比（需拔掉ENA处跳帽）
            https://img-blog.csdnimg.cn/img_convert/347ec1a493911c3c609231d7ee4bf2e4.jpeg
        """
        self.motor_pin_IN1 = 19  # 电机正传/反转/停止控制PWM引脚，对应L298N的IN1引脚
        self.motor_pin_IN2 = 26  # 电机正传/反转/停止控制PWM引脚，对应L298N的IN2引脚
        self.motor_pin_ENA = 13  # 电机转速控制PWM引脚，对应L298N的ENA引脚
        self.motor_freq = 1000  # 电机PWM频率
        self.motor_dc = 0  # 电机PWM占空比
        GPIO.setup(self.motor_pin_IN1, GPIO.OUT)  # 将GPIO设置为输出模式
        GPIO.setup(self.motor_pin_IN2, GPIO.OUT)  # 将GPIO设置为输出模式
        GPIO.setup(self.motor_pin_ENA, GPIO.OUT)  # 将GPIO设置为输出模式

        # 用于手柄控制的变量
        self.steer_dc_last = 7.5  # 记录的上一次转向占空比
        self.steer_finish_flag = True  # 完成一次转向控制的标志
        self.steer_axis_pos = 0  # 本次控制方向的轴读数，左负右正
        self.steer_axis_pos_last = 0  # 上次控制方向的轴读数，左负右正
        self.steer_axis_flag = False  # 摇杆读数成功标志
        self.steer_dc_step = 0.1  # 转向调整步长
        self.speed_axis_pos = -1  # 控制速度的轴读数
