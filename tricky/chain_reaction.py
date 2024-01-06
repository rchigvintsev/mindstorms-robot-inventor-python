from mindstorms import MSHub, Motor, MotorPair, ColorSensor, DistanceSensor, App
from mindstorms.control import wait_for_seconds, wait_until, Timer
from mindstorms.operator import greater_than, greater_than_or_equal_to, less_than, less_than_or_equal_to, equal_to, not_equal_to
import math

ANIM_COUNTDOWN = [
    '09990:09000:09990:00090:09990',
    '09090:09090:09990:00090:00090',
    '09990:00090:09990:00090:09990',
    '09990:00090:09990:09000:09990',
    '00900:09900:00900:00900:09990',
    '99999:99999:99999:99999:99999'
]

ANIM_CELEBRATE = [
    '00000:00000:00000:00000:00900',
    '00000:00000:00000:00900:00800',
    '00000:00000:00900:00800:00700',
    '00000:00000:00900:00500:00300',
    '00000:00000:00900:00100:00100',
    '00000:00600:06960:00600:00100',
    '00000:05750:07970:05750:00100',
    '00000:07970:09990:07970:00100',
    '70807:08980:89898:08980:70807',
    '90809:09890:98689:08980:90909',
    '90809:09690:96569:08680:90909',
    '70907:09190:90909:09090:70907',
    '07070:70907:09090:70907:07070',
    '70907:09090:90909:09090:70907',
    '60806:08080:80808:08080:60806',
    '40704:07070:70707:07070:40704',
    '30603:06060:60606:06060:30603',
    '50505:05050:50505:05050:50505',
    '00000:00000:00000:00000:00000'
]

wheels_motor_pair = MotorPair('B', 'A')
wheels_motor_pair.set_default_speed(60)

kick_motor = Motor('C')

distance_sensor = DistanceSensor('D')

hub = MSHub()
hub.light_matrix.set_orientation('upside down')

def start_animation_count_down():
    hub.light_matrix.start_animation(ANIM_COUNTDOWN, 1, False, 'fade out', False)

def start_animation_celebrate():
    hub.light_matrix.start_animation(ANIM_CELEBRATE, 8, False, 'overlay', False)

kick_motor.run_for_seconds(1, -100)
kick_motor.run_for_degrees(120, 100)
distance_sensor.light_up_all()

while True:
    distance = distance_sensor.get_distance_cm()
    if not_equal_to(distance, None) and less_than(distance, 10):
        start_animation_count_down()
        hub.speaker.play_sound('Countdown')
        kick_motor.run_for_rotations(1, 100)
        wheels_motor_pair.move(10, 'cm', 0, -20)
        start_animation_celebrate()
        hub.speaker.start_sound('Goal')
        wheels_motor_pair.start(100, 75)
        kick_motor.run_for_rotations(5, 100)
        wheels_motor_pair.stop()

    wait_for_seconds(0.01)
