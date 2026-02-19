from mindstorms import MSHub, Motor, MotorPair, ColorSensor, DistanceSensor, App
from mindstorms.control import wait_for_seconds, wait_until, Timer
from mindstorms.operator import greater_than, greater_than_or_equal_to, less_than, less_than_or_equal_to, equal_to, not_equal_to
import random

ANIM_BLINKING = ['77077:00000:99099:99099:00000'] * 5 + [
    '77077:00000:00000:77077:00000',
    '77077:00000:00000:00000:00000',
    '77077:00000:00000:77077:00000'
] + ['77077:00000:99099:99099:00000'] * 8

ANIM_HAPPY = [
    '77077:00000:98098:89089:00000',
    '77077:00000:89089:98098:00000'
]

hub = MSHub()

left_arm_motor = Motor('B')
left_arm_motor.set_default_speed(70)

right_arm_motor = Motor('F')
right_arm_motor.set_default_speed(70)

legs_motor_pair = MotorPair('A', 'E')
legs_motor_pair.set_default_speed(70)

distance_sensor = DistanceSensor('D')
color_sensor = ColorSensor('C')

def start_animation_blinking():
    hub.light_matrix.start_animation(ANIM_BLINKING, 8, True, 'overlay', False)

def start_animation_happy():
    hub.light_matrix.start_animation(ANIM_HAPPY, 8, True, 'overlay', False)

def calibrate():
    timer = Timer()
    timer.reset()

    left_arm_motor.start_at_power(70)
    right_arm_motor.start_at_power(-70)

    wait_for_seconds(0.25)

    while left_arm_motor.get_speed() > 15 and timer.now() < 1:
        pass
    left_arm_motor.stop()

    while right_arm_motor.get_speed() < -15 and timer.now() < 1:
        pass
    right_arm_motor.stop()

    wait_for_seconds(0.2)

    right_arm_motor.set_degrees_counted(right_arm_motor.get_position() - 360)
    right_arm_motor.run_to_degrees_counted(0, 30)

    left_arm_motor.set_degrees_counted(left_arm_motor.get_position())
    left_arm_motor.run_to_degrees_counted(0, 30)

hub.status_light.on('azure')
hub.light_matrix.set_orientation('right')
start_animation_blinking()
calibrate()
distance_sensor.light_up_all(100)

while True:
    legs_motor_pair.start()

    color = color_sensor.get_color()
    if color != None and color == 'red':
        legs_motor_pair.stop()
        start_animation_happy()
        hub.speaker.start_sound('Delivery')
        right_arm_motor.run_for_seconds(1)
        wait_for_seconds(3)
        hub.speaker.play_sound('Tadaa')
        start_animation_blinking()
        right_arm_motor.run_to_position(0, 'counterclockwise')
        wait_for_seconds(3)
        break


    distance = distance_sensor.get_distance_cm()
    if distance != None and distance < 25:
        rnd_val = random.randint(0, 3)
        if rnd_val == 0:
            legs_motor_pair.move(10, 'cm', -100)
        elif rnd_val == 1:
            legs_motor_pair.move(10, 'cm', 100)
        elif rnd_val == 2:
            legs_motor_pair.move(20, 'cm', -100)
    else:
        wait_for_seconds(0.1)

raise SystemExit
