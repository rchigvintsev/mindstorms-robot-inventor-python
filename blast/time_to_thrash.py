from mindstorms import MSHub, Motor, MotorPair, ColorSensor, DistanceSensor, App
from mindstorms.control import wait_for_seconds, wait_until, Timer
from mindstorms.operator import greater_than, greater_than_or_equal_to, less_than, less_than_or_equal_to, equal_to, not_equal_to

ANIM_HAMMER = [
    '09990:00000:00000:00000:00000',
    '88888:09990:00000:00000:00000',
    '77777:88888:09990:00000:00000',
    '66666:77777:88888:09990:00000',
    '55555:66666:77777:88888:09990'
]

hub = MSHub()
arms_and_head_motor = Motor('D')
hammer_motor = Motor('B')

def start_animation_hammer():
    hub.light_matrix.start_animation(ANIM_HAMMER, 5, True, 'direct', False)

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

hub.status_light.on('red')
hub.light_matrix.set_orientation('left')
start_animation_hammer()
hammer_motor.run_for_seconds(1)
calibrate()
arms_and_head_motor.run_for_rotations(1.7, -100)

for i in range(3):
    hub.speaker.start_sound('Hammer')
    hammer_motor.start(-100)
    arms_and_head_motor.run_for_rotations(3, 100)
    hammer_motor.start(100)
    arms_and_head_motor.run_for_rotations(3, -100)

hammer_motor.stop()
hub.speaker.play_sound('Laugh')
