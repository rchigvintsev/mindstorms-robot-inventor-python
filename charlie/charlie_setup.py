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

ANIM_SILLY = [
    '07077:70000:00099:99099:99000',
    '77070:00007:99000:99099:00099'
]

ANIM_SCARED = ['00000:00000:99099:99099:00000'] + ['00000:99900:99900:99909:00000'] * 2 + ['00000:00000:99099:99099:00000'] + ['00000:00999:00999:90999:00000'] * 2

hub = MSHub()

def start_animation_blinking():
    hub.light_matrix.start_animation(ANIM_BLINKING, 8, True, 'overlay', False)

def start_animation_happy():
    hub.light_matrix.start_animation(ANIM_HAPPY, 8, True, 'overlay', False)

def start_animation_silly():
    hub.light_matrix.start_animation(ANIM_SILLY, 2, True, 'direct', False)

def start_animation_scared():
    hub.light_matrix.start_animation(ANIM_SCARED, 8, True, 'overlay', False)

left_arm = Motor('B')
left_arm.set_default_speed(75)
right_arm = Motor('F')
right_arm.set_default_speed(75)

arm_motor_pair = MotorPair('F', 'B')
arm_motor_pair.set_default_speed(75)

leg_motor_pair = MotorPair('A', 'E')
leg_motor_pair.set_default_speed(75)

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

def charlie_happy():
    start_animation_happy()
    hub.speaker.start_sound('Hello')

    leg_motor_pair.move(10, 'cm')

    right_arm.run_for_degrees(-90)

    for i in range(3):
        right_arm.run_for_seconds(0.2, 75)
        right_arm.run_for_seconds(0.2, -75)

    right_arm.run_to_position(0, 'shortest path')

def charlie_silly():
    start_animation_silly()
    hub.speaker.start_sound('Humming')
    leg_motor_pair.move(10, 'cm', 100)

    left_arm.run_for_degrees(90)
    left_arm.run_for_degrees(-180)

    left_arm.run_for_degrees(180)
    left_arm.run_for_degrees(-180)

    left_arm.run_to_position(0, 'shortest path')

def charlie_scared():
    start_animation_scared()
    hub.speaker.start_sound('Scared')
    arm_motor_pair.move(90, 'degrees')
    leg_motor_pair.move(5, 'cm', -100)
    arm_motor_pair.move(-90, 'degrees')

hub.status_light.on('orange')
hub.light_matrix.set_orientation('right')
start_animation_blinking()

calibrate()

arm_motor_pair.move(90, 'degrees')
arm_motor_pair.move(-90, 'degrees')

charlie_happy()

start_animation_blinking()
wait_for_seconds(2)

charlie_silly()

start_animation_blinking()
wait_for_seconds(2)

charlie_scared()

start_animation_blinking()
