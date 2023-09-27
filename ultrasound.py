#====================================#
# Date: 2023.8.19
#====================================#
import RPi.GPIO as GPIO
import time

#====================================#
# Ultrasound
#====================================#
Trig_Pin = 23
Echo_Pin = 24

def ultrasound_init():
    # 设置GPIO的引脚模式为BCM模式
    GPIO.setmode(GPIO.BCM)

    # 设置管脚的输入输出模式和初始电平
    GPIO.setup(Trig_Pin,GPIO.OUT,initial = GPIO.LOW)
    GPIO.setup(Echo_Pin,GPIO.IN)

    time.sleep(1)

def checkdist():
#    GPIO输出一段不小于10us的电平
    GPIO.output(Trig_Pin,GPIO.HIGH)
    time.sleep(0.000015)
#    Trig_Pin回到低电平状态
    GPIO.output(Trig_Pin,GPIO.LOW)
    while not GPIO.input(Echo_Pin):
        pass
    # 一直等到Echo_Pin 有了反应，计算开始时间
    start = time.time()
    while GPIO.input(Echo_Pin):
        pass
    #只要echo_Pin不再接收，计算结束时间，并计算总时长
    end = time.time()
    # 计算距离
    length = (end-start)*340/2
    return length


def dist_output():
    while True: 
        dist = checkdist()
        # 如果距离小于1米，则输出提示信息
        if dist < 1:
            print("Something is closing!")
            print(f"从基准至目标--距离>> {dist:.2f}m")
        # 如果距离大于25米，则不输出
        elif dist < 25:
            print(f"从基准至目标--距离>> {dist:.2f}m")
        # 当其他情况出现时，输出noise detected
        else:
            print("Noise detected!")
        time.sleep(2)