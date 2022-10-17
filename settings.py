import RPi.GPIO as GPIO  # 引入GPIO模块


class Settings:
    """存储设置的类"""

    def __init__(self):
        """初始化静态设置"""
        self.steer_pin = 17  # 转向舵机PWM引脚
        self.steer_freq = 50  # 舵机PWM频率

        GPIO.setmode(GPIO.BCM)  # 使用BCM编号方式
        GPIO.setup(self.steer_pin, GPIO.OUT)  # 将GPIO设置为输出模式

        """初始化动态设置"""
        self.steer_dc = 7.5  # 舵机PWM占空比

        # 用于手柄控制的变量
        self.steer_dc_last = 7.5  # 记录的上一次转向占空比
        self.steer_finish_flag = True  # 完成一次转向控制的标志
        self.steer_axis_pos = 0  # 本次控制方向的轴读数，左负右正
        self.steer_axis_pos_last = 0  # 上次控制方向的轴读数，左负右正
        self.steer_axis_flag = False
        self.steer_dc_step = 0.1  # 转向调整步长
