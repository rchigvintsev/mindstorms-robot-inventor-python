from mindstorms import MSHub, Motor, MotorPair, ColorSensor, DistanceSensor, App
from mindstorms.control import wait_for_seconds, wait_until, Timer
from mindstorms.operator import greater_than, greater_than_or_equal_to, less_than, less_than_or_equal_to, equal_to, not_equal_to
import math

ANIM_BLINKING = ['77077:00000:99099:99099:00000'] * 5 + [
    '77077:00000:00000:77077:00000',
    '77077:00000:00000:00000:00000',
    '77077:00000:00000:77077:00000'
] + ['77077:00000:99099:99099:00000'] * 8

ANIM_DIZZY = [
    '77077:00000:88088:89098:00000',
    '77077:00000:88088:98089:00000',
    '77077:00000:98089:88088:00000',
    '77077:00000:89098:88088:00000'
] * 2 + [
    '77077:00000:88088:89098:00000',
    '77077:00000:99099:99099:00000'
]

hub = MSHub()

def start_animation_blinking():
    hub.light_matrix.start_animation(ANIM_BLINKING, 8, False, 'overlay', False)

def start_animation_dizzy():
    hub.light_matrix.start_animation(ANIM_DIZZY, 8, False, 'overlay', False)

hub.status_light.on('blue')
hub.light_matrix.set_orientation('right')
start_animation_blinking()
motor_pair = MotorPair('A', 'E')
motor_pair.move(40, 'cm', -100, 80)
start_animation_dizzy()
hub.speaker.play_sound('Dizzy')
