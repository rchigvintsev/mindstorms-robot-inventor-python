"""This program is based on the project "Balancing Bot I" developed by Dimitri Dekyvere and Laurens Valk"""

from mindstorms import MSHub, Motor, MotorPair, ColorSensor, DistanceSensor, App
from mindstorms.control import wait_for_seconds, wait_until, Timer
from mindstorms.operator import greater_than, greater_than_or_equal_to, less_than, less_than_or_equal_to, equal_to, not_equal_to

from utime import ticks_diff, ticks_ms

import hub
import math
import array

WAIT_TIME = 0.03

ANIM_BLINKING = ['77077:00000:99099:99099:00000'] * 5 + [
    '77077:00000:00000:77077:00000',
    '77077:00000:00000:00000:00000',
    '77077:00000:00000:77077:00000'
] + ['77077:00000:99099:99099:00000'] * 8

ANIM_SILLY = [
    '07077:70000:00099:99099:99000',
    '77070:00007:99000:99099:00099'
]

ms_hub = MSHub()
left_leg_motor = Motor('A')
right_leg_motor = Motor('E')

def start_animation_blinking():
    ms_hub.light_matrix.start_animation(ANIM_BLINKING, 8, True, 'overlay', False)

def start_animation_silly():
    ms_hub.light_matrix.start_animation(ANIM_SILLY, 2, True, 'direct', False)

def reset_motors():
    left_leg_motor.set_degrees_counted(0)
    right_leg_motor.set_degrees_counted(0)

def start_at_power(left_power, right_power):
    left_leg_motor.start_at_power(round(left_power * -1))
    right_leg_motor.start_at_power(round(right_power))

def stop():
    left_leg_motor.stop()
    right_leg_motor.stop()

def get_pitch():
    return ms_hub.motion_sensor.get_roll_angle() - 71.4 # 71.4 degrees is an optimal angle when robot is relatively balanced

pitch = get_pitch()
pitch_target = pitch
motor_angle_buffer = [0] * 9
fallen = False

def reset():
    global pitch
    global pitch_target
    global motor_angle_buffer

    reset_motors()
    pitch = get_pitch()
    pitch_target = pitch
    motor_angle_buffer = [0] * 9

def on_fall():
    global fallen

    stop()
    ms_hub.speaker.play_sound('Ouch')
    start_animation_silly()

    fallen = True

def on_rise():
    global fallen

    reset()
    ms_hub.speaker.play_sound('Tadaa')
    start_animation_blinking()

    fallen = False

reset_motors()
ms_hub.light_matrix.set_orientation('right')
start_animation_blinking()

while True:
    if fallen:
        if abs(get_pitch()) <= 15:
            ms_hub.left_button.wait_until_pressed()
            ms_hub.left_button.wait_until_released()
            on_rise()
        else:
            wait_for_seconds(WAIT_TIME)
        continue

    if abs(get_pitch()) > 30:
        on_fall()
        continue

    angular_velocity = hub.motion.gyroscope()[1]
    a = angular_velocity * 0.035

    pitch += a
    b = pitch * 9.5


    left_angle = left_leg_motor.get_degrees_counted()
    right_angle = right_leg_motor.get_degrees_counted()

    motor_angle = right_angle - left_angle
    motor_speed = (motor_angle - motor_angle_buffer.pop(0)) / 0.224
    motor_angle_buffer.append(motor_angle)
    c = motor_speed * 0.0455

    error = motor_angle - pitch_target
    d = error * 0.0195

    balance_power = a + b + c + d
    if abs(balance_power) > 175:
        on_fall()
        continue

    steering_power = (left_angle + right_angle) * 0.2
    left_power = balance_power + steering_power
    right_power = balance_power - steering_power
    start_at_power(left_power + math.copysign(10, left_power), right_power + math.copysign(10, right_power))

    wait_for_seconds(WAIT_TIME)
