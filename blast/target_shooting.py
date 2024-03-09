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

ANIM_TARGET_DESTROYED = [
    '99999:99999:99999:99999:99999',
    '77777:77777:77777:77777:77777',
    '55555:55555:55755:55555:55555',
    '33333:33333:33833:33333:33333',
    '00000:00700:07970:00700:00000',
    '00800:08980:89998:08980:00800',
    '08980:89998:99999:89998:08980',
    '89998:99999:99999:99999:89998',
    '88888:88888:88188:88888:88888',
    '99999:99099:90909:99099:99999',
    '99099:90909:09990:90909:99099',
    '91919:19991:99999:19991:91919',
    '19991:99999:99999:99999:19991',
    '18881:88888:88888:88888:18881',
    '17771:77777:77777:77777:17771',
    '06660:66666:66666:66666:06660',
    '05550:55555:55555:55555:05550',
    '04440:44444:44444:44444:04440',
    '13331:33333:33333:33333:13331',
    '00000:00000:00000:00000:00000'
]

wheels_motor_pair = MotorPair('C', 'A')
arms_and_head_motor = Motor('D')
trigger_motor = Motor('B')

hub = MSHub()
hub.status_light.on('red')
hub.light_matrix.set_orientation('left')

def start_animation_scanning():
    hub.light_matrix.start_animation(ANIM_SCANNING, 5, True, 'overlay', False)

def start_animation_target_destroyed():
    hub.light_matrix.start_animation(ANIM_TARGET_DESTROYED, 4, False, 'overlay', False)

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
calibrate()
wheels_motor_pair.move(5, 'cm', -100)
arms_and_head_motor.run_for_rotations(1.2, -60)
hub.speaker.start_sound('Laser')
trigger_motor.run_for_seconds(0.4, 100)
hub.speaker.start_sound('Laser')
trigger_motor.run_for_degrees(-140, 100)
trigger_motor.run_for_degrees(60, 100)
start_animation_target_destroyed()
hub.speaker.play_sound('Damage')
hub.speaker.play_sound('Target Destroyed')
