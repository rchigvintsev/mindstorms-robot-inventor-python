from mindstorms import MSHub, Motor, MotorPair, ColorSensor, DistanceSensor, App
from mindstorms.control import wait_for_seconds, wait_until, Timer
from mindstorms.operator import greater_than, greater_than_or_equal_to, less_than, less_than_or_equal_to, equal_to, not_equal_to
import math

ANIM_BOWLING = [
    '08970:89887:89857:89887:08970',
    '08970:89887:89887:89587:08970',
    '08970:89887:85887:89887:08970',
    '08970:89887:85887:89887:08970',
    '08970:89587:89887:89887:08970'
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
wheels_motor_pair.set_default_speed(80)

claw_motor = Motor('C')
claw_motor.set_default_speed(30)

distance_sensor = DistanceSensor('D')
color_sensor = ColorSensor('E')

hub = MSHub()
hub.light_matrix.set_orientation('upside down')

def start_animation_bowling():
    hub.light_matrix.start_animation(ANIM_BOWLING, 7, True, 'overlay', False)

def start_animation_celebrate():
    hub.light_matrix.start_animation(ANIM_CELEBRATE, 8, False, 'overlay', False)

claw_motor.run_for_seconds(1, -30)
claw_motor.run_for_degrees(90)

while True:
    color_sensor.wait_until_color('red')
    start_animation_bowling()
    hub.speaker.play_sound('Success Chime')
    claw_motor.run_for_seconds(1, 30)
    claw_motor.run_for_degrees(-10)
    distance_sensor.light_up_all()

    distance_sensor.wait_for_distance_closer_than(10, 'cm')
    distance_sensor.light_up_all(0)
    wheels_motor_pair.start()
    hub.speaker.start_sound('Bowling')
    claw_motor.run_for_seconds(0.4, -30)
    wheels_motor_pair.stop()
    start_animation_celebrate()
    wheels_motor_pair.move(-16, 'cm')
    hub.speaker.play_sound('Strike')
