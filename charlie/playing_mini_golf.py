from mindstorms import MSHub, Motor, MotorPair, ColorSensor, DistanceSensor, App
from mindstorms.control import wait_for_seconds, wait_until, Timer
from mindstorms.operator import greater_than, greater_than_or_equal_to, less_than, less_than_or_equal_to, equal_to, not_equal_to

ANIM_BLINKING = ['77077:00000:99099:99099:00000'] * 5 + [
    '77077:00000:00000:77077:00000',
    '77077:00000:00000:00000:00000',
    '77077:00000:00000:77077:00000'
] + ['77077:00000:99099:99099:00000'] * 8

ANIM_HAPPY = [
    '77077:00000:98098:89089:00000',
    '77077:00000:89089:98098:00000'
]

def start_animation_blinking():
    hub.light_matrix.start_animation(ANIM_BLINKING, 8, True, 'overlay', False)

def start_animation_happy():
    hub.light_matrix.start_animation(ANIM_HAPPY, 8, True, 'overlay', False)

hub = MSHub()

left_arm_motor = Motor('B')
right_leg_motor = Motor('E')

color_sensor = ColorSensor('C')

hub.status_light.on('black')
hub.light_matrix.set_orientation('right')
start_animation_blinking()

left_arm_motor.run_for_seconds(1, -80)

while True:
    color = color_sensor.get_color()
    if color != None and color == 'red':
        hub.speaker.play_sound('1234')
        left_arm_motor.run_for_degrees(235, 80)
        left_arm_motor.run_for_seconds(1, -80)
        hub.speaker.play_sound('Yes')
        right_leg_motor.run_for_degrees(880, 80)
        start_animation_blinking()
    else:
        wait_for_seconds(0.05)
