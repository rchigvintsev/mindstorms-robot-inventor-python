from mindstorms import MSHub, Motor, MotorPair, ColorSensor, DistanceSensor, App
from mindstorms.control import wait_for_seconds, wait_until, Timer
from mindstorms.operator import greater_than, greater_than_or_equal_to, less_than, less_than_or_equal_to, equal_to, not_equal_to
import math

ANIM_LOOKING = ['77077:00000:88088:98098:00000', '77077:00000:88088:89089:00000']
ANIM_HAPPY = ['77077:00000:98098:89089:00000', '77077:00000:89089:98098:00000']
ANIM_SCARED = ['00000:00000:99099:99099:00000'] + ['00000:99900:99900:99909:00000'] * 2 + ['00000:00000:99099:99099:00000'] + ['00000:00999:00999:90999:00000'] * 2
ANIM_ANGRY = ['90009:09090:00000:97097:00000' + '90009:09090:00000:79079:00000'] * 2

hub = MSHub()

def start_animation_looking():
    hub.light_matrix.start_animation(ANIM_LOOKING, 1, True, 'direct', False)

def start_animation_happy():
    hub.light_matrix.start_animation(ANIM_HAPPY, 8, True, 'overlay', False)

def start_animation_scared():
    hub.light_matrix.start_animation(ANIM_SCARED, 8, True, 'overlay', False)

def start_animation_angry():
    hub.light_matrix.start_animation(ANIM_ANGRY, 1, False, 'direct', False)

left_arm = Motor('B')
right_arm = Motor('F')

def calibrate():
    timer = Timer()
    timer.reset()

    left_arm.start_at_power(70)
    right_arm.start_at_power(-70)

    wait_for_seconds(0.25)

    while left_arm.get_speed() > 15 and timer.now() < 1:
        pass
    left_arm.stop()

    while right_arm.get_speed() < -15 and timer.now() < 1:
        pass
    right_arm.stop()

    wait_for_seconds(0.2)

    right_arm.set_degrees_counted(right_arm.get_position() - 360)
    right_arm.run_to_degrees_counted(0, 30)

    left_arm.set_degrees_counted(left_arm.get_position())
    left_arm.run_to_degrees_counted(0, 30)

hub.status_light.off()
hub.light_matrix.set_orientation('right')
start_animation_looking()

calibrate()

color_sensor = ColorSensor('C')
motor_pair_feet = MotorPair('A', 'E')

while True:
    color = color_sensor.get_color()
    if not_equal_to(color, None):
        if color == 'green':
            hub.status_light.on('green')
            start_animation_happy()
            motor_pair_feet.move(40, steering=-100)
            motor_pair_feet.move(40, steering=100)
            hub.speaker.play_sound('Chuckle')
        elif color == 'yellow':
            hub.status_light.on('yellow')
            start_animation_scared()
            hub.speaker.start_sound('Scared')
            motor_pair_feet.move(-20)
        elif color == 'red':
            hub.status_light.on('red')
            start_animation_angry()
            hub.speaker.start_sound('No')
            motor_pair_feet.move(20)

        hub.status_light.off()
        start_animation_looking()

    wait_for_seconds(0.1)
