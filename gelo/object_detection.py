from mindstorms import MSHub, Motor, MotorPair, DistanceSensor
from mindstorms.control import wait_for_seconds, Timer
from math import copysign
from random import randint

ANIM_PULSE = [
    '00000:00000:00009:00000:00000',
    '00000:00000:98765:00000:00000'
]

DIRECTION_FORWARD  = 'forward'
DIRECTION_BACKWARD = 'backward'
DIRECTION_LEFT     = 'left'
DIRECTION_RIGHT    = 'right'

hub = MSHub()
motor_pair_back_legs = MotorPair('A', 'B')
motor_pair_front_legs = MotorPair('C', 'D')
motors = (Motor('A'), Motor('B'), Motor('C'), Motor('D'))
distance_sensor = DistanceSensor('E')
timer = Timer()


def start_animation_pulse():
    hub.light_matrix.start_animation(ANIM_PULSE, 2, True, 'slide left')


def set_speed(speed):
    new_speed = round(speed * 0.3 + copysign(30, speed))
    new_speed = 0 if speed == 0 else max(-60, min(new_speed, 60))
    motor_pair_back_legs.set_default_speed(new_speed)
    motor_pair_front_legs.set_default_speed(new_speed)


def set_legs_position(direction):
    position = {
        'walk': (270, 270, 90, 90),
        DIRECTION_LEFT: (270, 45, 90, 315),
        DIRECTION_RIGHT: (135, 270, 225, 90)
    }
    positions = position.get(direction, position['walk'])
    for motor, pos in zip(motors, positions):
        motor.run_to_position(pos)


def start_walking(direction):
    set_legs_position(direction)
    default_speed = motor_pair_back_legs.get_default_speed()
    walk_speed = {
        DIRECTION_FORWARD: default_speed,
        DIRECTION_BACKWARD: -default_speed,
    }
    speed = walk_speed.get(direction, 50)
    motor_pair_back_legs.start(speed=speed)
    motor_pair_front_legs.start(speed=speed)


def stop_walking():
    motor_pair_back_legs.stop()
    motor_pair_front_legs.stop()


def walk_for_seconds(direction, seconds):
    start_walking(direction)
    wait_for_seconds(seconds)
    stop_walking()


def get_distance():
    distance = distance_sensor.get_distance_cm()
    return 200 if distance is None else distance


distance_sensor.light_up_all()
hub.light_matrix.set_orientation(DIRECTION_LEFT)
start_animation_pulse()
hub.speaker.play_sound('Initialize')
set_speed(80)

while True:
    start_walking(DIRECTION_FORWARD)
    timer.reset()

    while timer.now() < 10:
        if get_distance() < 20:
            direction = DIRECTION_LEFT if randint(1, 2) == 1 else DIRECTION_RIGHT
            walk_for_seconds(direction, 4)
            timer.reset()
            break
        wait_for_seconds(0.01)

    if timer.now() >= 10:
        stop_walking()
        break
