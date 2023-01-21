from mindstorms import MSHub, Motor, MotorPair, ColorSensor, DistanceSensor, App
from mindstorms.control import wait_for_seconds, wait_until, Timer
from mindstorms.operator import greater_than, greater_than_or_equal_to, less_than, less_than_or_equal_to, equal_to, not_equal_to
import math

ANIM_WAKE_UP = [
    '77077:00000:00000:00000:00000',

    '77077:00000:00000:99000:00000',
    '77077:00000:99000:99000:00000',
    '77077:00000:99000:99000:00000',
    '77077:00000:00000:99000:00000',

    '77077:00000:00000:00099:00000',
    '77077:00000:00099:00099:00000',
    '77077:00000:00099:00099:00000',
    '77077:00000:00000:00099:00000',

    '77077:00000:00000:99000:00000',
    '77077:00000:99000:99099:00000',
    '77077:00000:99099:99099:00000',
    '77077:00000:89089:98098:00000',
    '77077:00000:98098:89089:00000',
    '77077:00000:99099:99099:00000',
    '77077:00000:99099:99099:00000'
]

ANIM_HAPPY = [
    '77077:00000:98098:89089:00000',
    '77077:00000:89089:98098:00000'
]

ANIM_BLINKING = ['77077:00000:99099:99099:00000'] * 5 + [
    '77077:00000:00000:77077:00000',
    '77077:00000:00000:00000:00000',
    '77077:00000:00000:77077:00000'
] + ['77077:00000:99099:99099:00000'] * 8

hub = MSHub()
left_hand = Motor('B')
right_hand = Motor('F')
hands = MotorPair('B', 'F')

def calibrate():
    left_hand.start(70)
    right_hand.start(-70)

    wait_for_seconds(0.25)

    left_hand_stopped = False
    right_hand_stopped = False

    while True:
        if not left_hand_stopped and left_hand.get_speed() == 0:
            left_hand.stop()
            left_hand_stopped = True
        if not right_hand_stopped and right_hand.get_speed() == 0:
            right_hand.stop()
            right_hand_stopped = True
        if left_hand_stopped and right_hand_stopped:
            break

    left_hand.set_degrees_counted(0)
    right_hand.set_degrees_counted(0)

    left_hand.start(-25)
    right_hand.start(25)

    left_hand_stopped = False
    right_hand_stopped = False

    while True:
        if not left_hand_stopped and left_hand.get_degrees_counted() <= -165:
            left_hand.stop()
            left_hand_stopped = True
        if not right_hand_stopped and right_hand.get_degrees_counted() >= 195:
            right_hand.stop()
            right_hand_stopped = True
        if left_hand_stopped and right_hand_stopped:
            break

def play_animation_wake_up():
    hub.light_matrix.play_animation(ANIM_WAKE_UP, 3, 'overlay', False)

def start_animation_happy():
    hub.light_matrix.start_animation(ANIM_HAPPY, 8, True, 'overlay', False)

def start_animation_blinking():
    hub.light_matrix.start_animation(ANIM_BLINKING, 8, True, 'overlay', False)

hub.status_light.on('green')
hub.light_matrix.set_orientation('right')
hub.light_matrix.show('77077:00000:00000:00000:00000')

calibrate()

while True:
    new_gesture = hub.motion_sensor.wait_for_new_gesture()
    if new_gesture == 'tapped':
        break

play_animation_wake_up()
hands.move(90, 'degrees', 0, -70)
hub.speaker.play_sound('Hi')
wait_for_seconds(1)
hands.move(90, 'degrees', 0, 70)
start_animation_happy()
hub.speaker.play_sound('Hello')
start_animation_blinking()
