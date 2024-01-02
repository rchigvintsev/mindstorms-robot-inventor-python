from mindstorms import MSHub, Motor, MotorPair, ColorSensor, DistanceSensor, App
from mindstorms.control import wait_for_seconds, wait_until, Timer
from mindstorms.operator import greater_than, greater_than_or_equal_to, less_than, less_than_or_equal_to, equal_to, not_equal_to
import math

WHEEL_DIAMETER = 56.4 # Robot wheel diameter in millimeters

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

# Calculates how many degrees should motor count in order to travel the given distance in centimeters
def distance_to_degrees(distance):
    # Magic number 115 is rounded result of division of 360 degrees by PI
    return 115 * distance * 10 / WHEEL_DIAMETER

wheels_motor_pair = MotorPair('B', 'A')
wheels_motor_pair.set_default_speed(60)

right_wheel_motor = Motor('A')

kick_motor = Motor('C')
kick_motor.set_stop_action('hold')

distance_sensor = DistanceSensor('D')
color_sensor = ColorSensor('E')

hub = MSHub()
hub.light_matrix.set_orientation('upside down')

def start_animation_celebrate():
    hub.light_matrix.start_animation(ANIM_CELEBRATE, 8, False, 'overlay', False)

kick_motor.run_for_seconds(1, -100)
kick_motor.run_for_degrees(325, 100)
distance_sensor.light_up_all()

degrees_counted_target = distance_to_degrees(30)
degrees_counted_target_reached = True

while True:
    if not degrees_counted_target_reached:
        degrees_counted_target_reached = abs(right_wheel_motor.get_degrees_counted()) >= degrees_counted_target
        if degrees_counted_target_reached:
            wheels_motor_pair.stop()

    distance = distance_sensor.get_distance_cm()
    if not_equal_to(distance, None) and less_than(distance, 10):
        degrees_counted_target_reached = False
        right_wheel_motor.set_degrees_counted(0)
        wheels_motor_pair.start(0)

    color = color_sensor.get_color()
    if not_equal_to(color, None) and equal_to(color, 'red'):
        wheels_motor_pair.stop()
        degrees_counted_target_reached = True

        hub.status_light.on('red')
        hub.speaker.start_sound('Hit')
        kick_motor.run_for_rotations(1, 100)
        hub.status_light.off()
        start_animation_celebrate()
        hub.speaker.start_sound('Goal')

    wait_for_seconds(0.01)
