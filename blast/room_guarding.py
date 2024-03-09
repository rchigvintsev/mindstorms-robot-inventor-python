from mindstorms import MSHub, Motor, MotorPair, ColorSensor, DistanceSensor, App
from mindstorms.control import wait_for_seconds, wait_until, Timer
from mindstorms.operator import greater_than, greater_than_or_equal_to, less_than, less_than_or_equal_to, equal_to, not_equal_to
import math

ANIM_SCANNING = [
    '00000:00000:56789:00000:00000',
    '00000:00000:45698:00000:00000',
    '00000:00000:34987:00000:00000',
    '00000:00000:29876:00000:00000',
    '00000:00000:98765:00000:00000',
    '00000:00000:89654:00000:00000',
    '00000:00000:78943:00000:00000',
    '00000:00000:67892:00000:00000'
]

ANIM_CROSSHAIR = ['00900:06960:99099:06960:00900'] * 4

ANIM_SHUT_DOWN = [
    '00000:00000:99999:00000:00000',
    '00000:00000:89998:00000:00000',
    '00000:00000:78987:00000:00000',
    '00000:00000:67976:00000:00000',
    '00000:00000:56965:00000:00000',
    '00000:00000:45854:00000:00000',
    '00000:00000:14841:00000:00000',
    '00000:00700:17971:00700:00000',
    '00000:00700:17971:00700:00000',
    '00000:00800:18981:00800:00000',
    '00000:00700:17971:00700:00000',
    '00000:00000:10901:00000:00000',
    '00000:00000:10901:00000:00000',
    '00000:00000:10801:00000:00000',
    '00000:00000:10801:00000:00000',
    '00000:00000:10701:00000:00000',
    '00000:00000:10601:00000:00000',
    '00000:00000:10501:00000:00000',
    '00000:00000:10101:00000:00000',
    '00000:00000:00000:00000:00000'
]

DIRECTION_LEFT  = 0
DIRECTION_RIGHT = 1

wheels_motor_pair = MotorPair('C', 'A')
wheels_motor_pair.set_default_speed(10)

left_wheel_motor = Motor('C')
arms_and_head_motor = Motor('D')
trigger_motor = Motor('B')

distance_sensor = DistanceSensor('F')

hub = MSHub()
hub.status_light.on('red')
hub.light_matrix.set_orientation('left')

def start_animation_scanning():
    hub.light_matrix.start_animation(ANIM_SCANNING, 5, True, 'overlay', False)

def start_animation_crosshair():
    hub.light_matrix.start_animation(ANIM_CROSSHAIR, 2, False, 'fade in', False)

def start_animation_shut_down():
    hub.light_matrix.start_animation(ANIM_SHUT_DOWN, 6, False, 'overlay', False)

def calibrate():
    timer = Timer()
    arms_and_head_motor.start_at_power(100)
    wait_for_seconds(0.3)
    while arms_and_head_motor.get_speed() > 50 and timer.now() < 3:
        pass
    arms_and_head_motor.stop()
    wait_for_seconds(0.2)
    hub.motion_sensor.reset_yaw_angle()
    wait_for_seconds(0.1)
    timer.reset()
    arms_and_head_motor.start(-50)
    while hub.motion_sensor.get_yaw_angle() > -42 and timer.now() < 2:
        pass
    arms_and_head_motor.stop()
    wait_for_seconds(0.2)
    arms_and_head_motor.set_degrees_counted(0)

def is_enemy_detected():
    distance = distance_sensor.get_distance_cm()
    return distance != None and distance < 40

def scan_room(direction):
    hub.speaker.start_sound('Scanning')
    if direction == DIRECTION_LEFT:
        distance_sensor.light_up(0, 0, 100, 100)
        steering = -100
    else:
        distance_sensor.light_up(100, 100, 0, 0)
        steering = 100
    left_wheel_motor.set_degrees_counted(0)
    wheels_motor_pair.start(steering)
    while True:
        if is_enemy_detected():
            wheels_motor_pair.stop()
            distance_sensor.light_up(100, 100, 100, 100)
            start_animation_crosshair()
            hub.speaker.play_sound('Target Acquired')
            arms_and_head_motor.run_for_rotations(3, -100)
            hub.speaker.start_sound('Laser')
            trigger_motor.run_for_seconds(0.4, 100)
            hub.speaker.start_sound('Laser')
            trigger_motor.run_for_degrees(-140, 100)
            trigger_motor.run_for_degrees(60, 100)
            wait_for_seconds(1)
            arms_and_head_motor.run_for_rotations(1.5, 100)
            start_animation_shut_down()
            hub.speaker.play_sound('Shut Down')
            raise SystemExit

        if abs(left_wheel_motor.get_degrees_counted()) > 120:
            wheels_motor_pair.stop()
            break

        wait_for_seconds(0.01)

start_animation_scanning()
calibrate()
arms_and_head_motor.run_for_rotations(1.8, 100)

while True:
    scan_room(DIRECTION_LEFT)
    scan_room(DIRECTION_RIGHT)
