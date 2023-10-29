from mindstorms import MSHub, Motor, MotorPair, ColorSensor, DistanceSensor, App
from mindstorms.control import wait_for_seconds, wait_until, Timer
from mindstorms.operator import greater_than, greater_than_or_equal_to, less_than, less_than_or_equal_to, equal_to, not_equal_to
import math

WHEEL_DIAMETER = 56.4 # Robot wheel diameter in millimeters

ANIM_BASKETBALL = [
    '08970:89887:89887:89887:08970',
    '89887:89887:89887:08970:00000',
    '89887:89887:08970:00000:00000',
    '89887:08970:00000:00000:00000'
] + [
    '08970:00000:00000:00000:00000'
] * 3 + [
    '89887:08970:00000:00000:00000'
    '89887:89887:08970:00000:00000',
    '89887:89887:89887:08970:00000',
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

hub = MSHub()
manipulator_motor = Motor('C')
manipulator_motor.set_default_speed(25)
left_wheel_motor = Motor('A')
wheels_motor_pair = MotorPair('A', 'B')
wheels_motor_pair.set_default_speed(50)
distance_sensor = DistanceSensor('D')
color_sensor = ColorSensor('E')

def start_animation_basketball():
    hub.light_matrix.start_animation(ANIM_BASKETBALL, 8, True, 'overlay', False)

def start_animation_celebrate():
    hub.light_matrix.start_animation(ANIM_CELEBRATE, 8, False, 'overlay', False)

# Calculates how many degrees should motor count in order to travel the given distance in centimeters
def distance_to_degrees(distance):
    # Magic number 115 is rounded result of division of 360 degrees by PI
    return 115 * distance * 10 / WHEEL_DIAMETER


start_animation_basketball()
manipulator_motor.run_for_seconds(1)
distance_sensor.light_up_all()
left_wheel_motor.set_degrees_counted(0)
degrees_counted_target = distance_to_degrees(100)
degrees_counted_target_reached = False
wheels_motor_pair.start(0)

while True:
    if not degrees_counted_target_reached:
        degrees_counted_target_reached = abs(left_wheel_motor.get_degrees_counted()) >= degrees_counted_target
        if degrees_counted_target_reached:
            wheels_motor_pair.stop()

    distance = distance_sensor.get_distance_cm()
    if distance != None and distance < 8:
        wheels_motor_pair.stop()
        manipulator_motor.run_for_degrees(-110)
        hub.speaker.play_sound('Hit')
        break

    wait_for_seconds(0.01)

left_wheel_motor.set_degrees_counted(0)
degrees_counted_target_reached = False
wheels_motor_pair.start(0, -40)

while True:
    if not degrees_counted_target_reached:
        degrees_counted_target_reached = abs(left_wheel_motor.get_degrees_counted()) >= degrees_counted_target
        if degrees_counted_target_reached:
            wheels_motor_pair.stop()

    color = color_sensor.get_color()
    if color != None and color == 'cyan':
        wheels_motor_pair.stop()
        hub.status_light.on('cyan')
        manipulator_motor.run_for_seconds(0.4, -75)
        start_animation_celebrate()
        hub.speaker.start_sound('Slam Dunk')
        manipulator_motor.run_for_seconds(1, 25)
        wait_for_seconds(2)
        break

    wait_for_seconds(0.01)

raise SystemExit
