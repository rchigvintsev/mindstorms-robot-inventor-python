import utime
from mindstorms import MSHub, Motor, MotorPair, ColorSensor, DistanceSensor, App
from mindstorms.control import wait_for_seconds, wait_until, Timer
from mindstorms.operator import greater_than, greater_than_or_equal_to, less_than, less_than_or_equal_to, equal_to, \
    not_equal_to

ANIM_PULSE = [
    '00000:00000:00009:00000:00000',
    '00000:00000:98765:00000:00000'
]

hub = MSHub()
motor_pair_back_legs = MotorPair('A', 'B')
motor_pair_front_legs = MotorPair('C', 'D')
motors = (Motor('A'), Motor('B'), Motor('C'), Motor('D'))
distance_sensor = DistanceSensor('E')
color_sensor = ColorSensor('F')


def start_animation_pulse():
    hub.light_matrix.start_animation(ANIM_PULSE, 2, True, 'slide left')


def set_default_speed(speed):
    new_speed = 0 if speed == 0 else max(-100, min(speed, 100))
    motors[0].set_default_speed(-new_speed)
    motors[2].set_default_speed(-new_speed)
    motors[1].set_default_speed(new_speed)
    motors[3].set_default_speed(new_speed)


def reset_degrees_counted():
    for motor in motors:
        motor.set_degrees_counted(0)


def set_initial_position():
    motors[0].run_to_position(90, 'clockwise')
    motors[2].run_to_position(45, 'clockwise')
    motors[1].run_to_position(270, 'counterclockwise')
    motors[3].run_to_position(315, 'counterclockwise')


def start_motors(speed):
    motors[0].start(-speed)
    motors[2].start(-speed)
    motors[1].start(speed)
    motors[3].start(speed)


def stop_motors():
    for motor in motors:
        motor.stop()


def run_motors_for_seconds(time, speed=100):
    start_motors(speed)
    wait_for_seconds(time)
    stop_motors()


def run_motors_for_degrees(degrees, speed=100):
    offsets = []
    for motor in motors:
        offsets.append(abs(motor.get_degrees_counted()))
    start_motors(speed)

    finished = [False] * 4
    while not all(finished):
        for i, motor in enumerate(motors):
            if finished[i]:
                continue
            degrees_counted = abs(motor.get_degrees_counted())
            if (degrees_counted - offsets[i]) >= degrees:
                motor.stop()
                finished[i] = True
        wait_for_seconds(0.005)


def perform_stunt(color):
    hub.status_light.on(color)
    hub.speaker.play_sound('Activate')

    if color == 'blue':
        run_motors_for_seconds(0.3)
        motor_pair_back_legs.move(1.3, unit='rotations', speed=100)
        motor_pair_front_legs.move(120, unit='degrees', speed=-100)
        wait_for_seconds(0.5)
    elif color == 'green':
        reset_degrees_counted()
        run_motors_for_seconds(0.3)
        run_motors_for_degrees(45, 60)
        wait_for_seconds(1.5)
        run_motors_for_degrees(15, 60)
        wait_for_seconds(0.2)
        motor_pair_front_legs.move(290, unit='degrees', speed=-100)
        wait_for_seconds(0.5)
    elif color == 'yellow':
        for _ in range(2):
            run_motors_for_seconds(0.3, 60)
            run_motors_for_seconds(0.35, 60)
    elif color == 'red':
        reset_degrees_counted()
        run_motors_for_seconds(0.3, 60)
        run_motors_for_degrees(210, 100)
        wait_for_seconds(0.5)


distance_sensor.light_up_all()
hub.light_matrix.set_orientation('right')
start_animation_pulse()
hub.speaker.play_sound('Initialize')
set_default_speed(100)

while True:
    set_initial_position()
    hub.status_light.on('black')

    color = color_sensor.get_color()
    while color not in ('blue', 'green', 'yellow', 'red'):
        wait_for_seconds(0.03)
        color = color_sensor.get_color()

    perform_stunt(color)

    orientation = hub.motion_sensor.get_orientation()
    while orientation != 'front':
        wait_for_seconds(0.03)
        orientation = hub.motion_sensor.get_orientation()

    wait_for_seconds(1)
