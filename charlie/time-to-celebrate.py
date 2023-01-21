from mindstorms import MSHub, Motor, MotorPair, ColorSensor, DistanceSensor, App
from mindstorms.control import wait_for_seconds, wait_until, Timer
from mindstorms.operator import greater_than, greater_than_or_equal_to, less_than, less_than_or_equal_to, equal_to, not_equal_to
import math

ANIM_BLINKING = ['77077:00000:99099:99099:00000'] * 5 + [
    '77077:00000:00000:77077:00000',
    '77077:00000:00000:00000:00000',
    '77077:00000:00000:77077:00000'
] + ['77077:00000:99099:99099:00000'] * 8

hub = MSHub()

def start_animation_blinking():
    hub.light_matrix.start_animation(ANIM_BLINKING, 8, True, 'overlay', False)

left_arm = Motor('B')
right_arm = Motor('F')

def calibrate():
    timer = Timer()
    timer.reset()

    left_arm.start_at_power(70)
    right_arm.start_at_power(-70)

    wait_for_seconds(0.25)

    while left_arm.get_speed() > 15 and timer.now() < 1:
        pass
    left_arm.stop()

    while right_arm.get_speed() < -15 and timer.now() < 1:
        pass
    right_arm.stop()

    wait_for_seconds(0.2)

    right_arm.set_degrees_counted(right_arm.get_position() - 360)
    right_arm.run_to_degrees_counted(0, 30)

    left_arm.set_degrees_counted(left_arm.get_position())
    left_arm.run_to_degrees_counted(0, 30)

hub.status_light.on('azure')
hub.light_matrix.set_orientation('right')
start_animation_blinking()

calibrate()
wait_for_seconds(3)

hub.speaker.start_sound('Humming')
for _ in range(2):
    right_arm.run_for_degrees(-100)
    right_arm.run_for_degrees(100)

    left_arm.run_for_degrees(100)
    left_arm.run_for_degrees(-100)

hub.speaker.start_sound('Humming')

motor_pair_left = MotorPair('B', 'E')
motor_pair_right = MotorPair('A', 'F')
for _ in range(2):
    motor_pair_right.move(-5, steering=-100)
    motor_pair_right.move(5, steering=-100)
    motor_pair_left.move(-5, steering=100)
    motor_pair_left.move(5, steering=100)

motor_pair = MotorPair('A', 'E')
motor_pair.set_default_speed(80)
motor_pair.move(40, steering=100)
motor_pair.move(40, steering=-100)

right_arm.run_to_position(270, 'counterclockwise')
wait_for_seconds(1)

right_arm.run_for_seconds(1)

hub.speaker.play_sound('Tadaa')
right_arm.run_to_position(0, 'counterclockwise')
