from mindstorms import MSHub, Motor, MotorPair, DistanceSensor
from mindstorms.control import wait_for_seconds
from math import copysign

ANIM_PULSE = [
    '00000:00000:00009:00000:00000',
    '00000:00000:98765:00000:00000'
]

LEG_POSITIONS = {
    'walk': (270, 270, 90, 90),
    'left': (270, 45, 90, 315),
    'right': (135, 270, 225, 90)
}

DIRECTION_FORWARD = 'forward'
DIRECTION_BACKWARD = 'backward'

hub = MSHub()
back_legs_motor_pair = MotorPair('A', 'B')
front_legs_motor_pair = MotorPair('C', 'D')
motors = (Motor('A'), Motor('B'), Motor('C'), Motor('D'))
distance_sensor = DistanceSensor('E')

def start_animation_pulse():
    hub.light_matrix.start_animation(ANIM_PULSE, 2, True, 'slide left')

def set_walk_speed(speed):
    if speed == 0:
        new_speed = 0
    else:
        new_speed = max(-60, min(round(speed * 0.3 + copysign(30, speed)), 60))
    back_legs_motor_pair.set_default_speed(new_speed)
    front_legs_motor_pair.set_default_speed(new_speed)

def set_legs_position(direction):
    positions = LEG_POSITIONS.get(direction, LEG_POSITIONS['walk'])
    for motor, pos in zip(motors, positions):
        motor.run_to_position(pos)

def walk_for_seconds(direction, seconds):
    set_legs_position(direction)
    default_speed = back_legs_motor_pair.get_default_speed()
    if direction == DIRECTION_FORWARD:
        speed = default_speed
    elif direction == DIRECTION_BACKWARD:
        speed = -default_speed
    else:
        speed = 50
    back_legs_motor_pair.start(speed=speed)
    front_legs_motor_pair.start(speed=speed)
    wait_for_seconds(seconds)
    back_legs_motor_pair.stop()
    front_legs_motor_pair.stop()

distance_sensor.light_up_all()
hub.light_matrix.set_orientation('left')
start_animation_pulse()
hub.speaker.play_sound('Initialize')
set_walk_speed(80)
walk_for_seconds(DIRECTION_FORWARD, 3)
