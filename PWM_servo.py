#====================================#
# Date: 2023.8.19
#====================================#
from time import sleep
from rpi_hardware_pwm import HardwarePWM

PWMX_MIN= 4; PWMX_MAX = 13
PWMY_MIN= 4; PWMY_MAX = 13

PWM_x=[]
PWM_y=[]

def PWM_init():
    global PWM_x
    global PWM_y
    PWM_x=HardwarePWM(pwm_channel=0,hz=50)
    PWM_y=HardwarePWM(pwm_channel=1,hz=50)
    PWM_x.start(8.5)
    PWM_y.start(8.5)
    print("PWM func is up!\r\n")

# Accept -90 to 90 value input
def PWMx_Adj(Angle):
    if(abs(Angle)<=90):
        Duty_Cyc_Calc=(Angle/90)*((PWMX_MAX-PWMX_MIN)/2) + ((PWMX_MAX+PWMX_MIN)/2)
        PWM_x.change_duty_cycle(Duty_Cyc_Calc)
    else:
        print("PWM_X Angle Input Out of Range!")

# Accept -90 to 90 value input
def PWMy_Adj(Angle):
    if(abs(Angle)<=90):
        Duty_Cyc_Calc=(Angle/90)*((PWMY_MAX-PWMX_MIN)/2) + ((PWMY_MAX+PWMX_MIN)/2)
        PWM_y.change_duty_cycle(Duty_Cyc_Calc)
    else:
        print("PWM_Y Angle Input Out of Range!")        

def soft_move(func, current_angle, max_limit, step=2, delay=0.05):
    if func == "increase" and current_angle < max_limit:
        while current_angle < max_limit:
            current_angle += step
            sleep(delay)
            if current_angle > max_limit:
                current_angle = max_limit
            yield current_angle
            
    elif func == "decrease" and current_angle > max_limit:
        while current_angle > max_limit:
            current_angle -= step
            sleep(delay)
            if current_angle < max_limit:
                current_angle = max_limit
            yield current_angle