from mindstorms import MSHub, Motor, MotorPair, ColorSensor, DistanceSensor, App
from mindstorms.control import wait_for_seconds, wait_until, Timer
from mindstorms.operator import greater_than, greater_than_or_equal_to, less_than, less_than_or_equal_to, equal_to, not_equal_to
import math

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

DIRECTION_RIGHT = 1
DIRECTION_LEFT  = -1

REFLECTED_LIGHT_HISTORY_LENGTH             = 10
REFLECTED_LIGHT_LOST_LINE_THRESHOLD        = 30
REFLECTED_LIGHT_DIRECTION_CHANGE_THRESHOLD = 95

hub = MSHub()
manipulator_motor = Motor('C')
manipulator_motor.set_default_speed(25)
wheels_motor_pair = MotorPair('B', 'A')
wheels_motor_pair.set_default_speed(50)
distance_sensor = DistanceSensor('D')
color_sensor = ColorSensor('E')


reflected_light_history = [0] * REFLECTED_LIGHT_HISTORY_LENGTH
direction = DIRECTION_RIGHT
direction_changed = False
line_lost = False

def start_animation_basketball():
    hub.light_matrix.start_animation(ANIM_BASKETBALL, 8, True, 'overlay', False)

def start_animation_celebrate():
    hub.light_matrix.start_animation(ANIM_CELEBRATE, 8, False, 'overlay', False)

def is_time_to_change_direction(reflected_light):
    global direction_changed

    # Direction is already changed and we are turning trying to find a line
    if direction_changed:
        return False
    previous_reflected_light = reflected_light_history.pop(0)
    return reflected_light > REFLECTED_LIGHT_DIRECTION_CHANGE_THRESHOLD and previous_reflected_light > REFLECTED_LIGHT_DIRECTION_CHANGE_THRESHOLD

def change_direction():
    global direction
    global direction_changed
    global reflected_light_history

    direction = direction * -1
    direction_changed = True
    reflected_light_history = [0] * REFLECTED_LIGHT_HISTORY_LENGTH


start_animation_basketball()
manipulator_motor.run_for_seconds(1)
distance_sensor.light_up_all()

distance_sensor.wait_for_distance_closer_than(8, 'cm')
hub.speaker.play_sound('Success Chime')
manipulator_motor.run_for_degrees(-110)

while True:
    color = color_sensor.get_color()
    if color != None and color == 'cyan':
        wheels_motor_pair.stop()
        hub.status_light.on('cyan')
        manipulator_motor.run_for_seconds(0.4, -75)
        start_animation_celebrate()
        hub.speaker.start_sound('Explosion')
        manipulator_motor.run_for_seconds(1, 25)
        break

    steering = 0
    reflected_light = color_sensor.get_reflected_light()
    if reflected_light > REFLECTED_LIGHT_LOST_LINE_THRESHOLD:
        line_lost = True
        if is_time_to_change_direction(reflected_light):
            change_direction()
        reflected_light_history.append(reflected_light)
        steering = round(min(2.5 * (reflected_light - REFLECTED_LIGHT_LOST_LINE_THRESHOLD), 100.0)) * direction
    else:
        if line_lost:
            reflected_light_history = [0] * REFLECTED_LIGHT_HISTORY_LENGTH
            line_lost = False
        direction_changed = False
    
    wheels_motor_pair.start_at_power(35, steering)

    wait_for_seconds(0.01)
