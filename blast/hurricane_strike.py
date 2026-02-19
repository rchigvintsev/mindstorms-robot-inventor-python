from mindstorms import MSHub, Motor, MotorPair, ColorSensor, DistanceSensor, App
from mindstorms.control import wait_for_seconds, wait_until, Timer
from mindstorms.operator import greater_than, greater_than_or_equal_to, less_than, less_than_or_equal_to, equal_to, not_equal_to

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

wheels_motor_pair = MotorPair('C', 'A')
wheels_motor_pair.set_default_speed(20)

arms_and_head_motor = Motor('D')
trigger_motor = Motor('B')

distance_sensor = DistanceSensor('F')

hub = MSHub()
hub.status_light.on('red')
hub.light_matrix.set_orientation('left')

def start_animation_scanning():
    hub.light_matrix.start_animation(ANIM_SCANNING, 5, True, 'overlay', False)

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

start_animation_scanning()
trigger_motor.run_for_seconds(0.5, 100)
calibrate()
arms_and_head_motor.run_for_rotations(1.7, 100)
distance_sensor.light_up(100, 100, 100, 100)
hub.speaker.play_sound('Seek and Destroy')
wheels_motor_pair.start(0)
distance_sensor.wait_for_distance_closer_than(9, 'cm')

arms_and_head_motor.start(-100)
wait_for_seconds(0.1)
wheels_motor_pair.move(42, 'cm', -100, 100)
hub.speaker.start_sound('Damage')
trigger_motor.run_for_degrees(80, -100)
arms_and_head_motor.stop()

for _ in range(3):
    trigger_motor.run_for_seconds(0.2, 100)
    trigger_motor.run_for_seconds(0.2, -100)

arms_and_head_motor.start(100)
trigger_motor.start(100)
wait_for_seconds(0.5)
arms_and_head_motor.stop()
trigger_motor.stop()

hub.speaker.play_sound('Target Destroyed')
