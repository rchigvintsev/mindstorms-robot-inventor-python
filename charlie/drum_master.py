from mindstorms import MSHub, Motor, MotorPair, ColorSensor, DistanceSensor, App
from mindstorms.control import wait_for_seconds, wait_until, Timer
from mindstorms.operator import greater_than, greater_than_or_equal_to, less_than, less_than_or_equal_to, equal_to, not_equal_to

ANIM_COOL = ['00000:77077:99999:99099:00000', '77000:00077:99999:99099:00000'] * 2 + ['00000:77077:00000:99999:99099', '00077:77000:99999:99099:00000'] * 2
ANIM_HAPPY = [
    '77077:00000:98098:89089:00000',
    '77077:00000:89089:98098:00000'
]
ANIM_BLINKING = ['77077:00000:99099:99099:00000'] * 5 + [
    '77077:00000:00000:77077:00000',
    '77077:00000:00000:00000:00000',
    '77077:00000:00000:77077:00000'
] + ['77077:00000:99099:99099:00000'] * 8

STROKE = {
    'soft': (50, 55),
    'hard': (60, 66),
    'lift': (-45, -38),
    'stop': (0, 0)
}

RHYTHM = [
    ('hard', 'lift'),
    ('lift', 'stop'),
    ('soft', 'stop'),
    ('lift', 'stop'),
    ('soft', 'hard'),
    ('lift', 'lift'),
    ('soft', 'stop'),
    ('lift', 'stop')
]

hub = MSHub()

left_arm_motor = Motor('B')
left_arm_motor.set_default_speed(75)
right_arm_motor = Motor('F')
right_arm_motor.set_default_speed(75)

arms_motor_pair = MotorPair('B', 'F')
legs_motor_pair = MotorPair('A', 'E')

def start_animation_cool(fps=5):
    hub.light_matrix.start_animation(ANIM_COOL, 5, True, 'direct', False)

def start_animation_happy():
    hub.light_matrix.start_animation(ANIM_HAPPY, 8, True, 'overlay', False)

def start_animation_blinking():
    hub.light_matrix.start_animation(ANIM_BLINKING, 8, True, 'overlay', False)

def calibrate():
    timer = Timer()
    timer.reset()

    left_arm_motor.start_at_power(70)
    right_arm_motor.start_at_power(-70)

    wait_for_seconds(0.25)

    while left_arm_motor.get_speed() > 15 and timer.now() < 1:
        pass
    left_arm_motor.stop()

    while right_arm_motor.get_speed() < -15 and timer.now() < 1:
        pass
    right_arm_motor.stop()

    wait_for_seconds(0.2)

    right_arm_motor.set_degrees_counted(right_arm_motor.get_position() - 360)
    right_arm_motor.run_to_degrees_counted(0, 30)

    left_arm_motor.set_degrees_counted(left_arm_motor.get_position())
    left_arm_motor.run_to_degrees_counted(0, 30)

def play_drums(bars, tempo):
    if bars == 0 or tempo == 0:
        return

    rhythm = RHYTHM * bars
    rhythm[-1] = ('lift', 'soft')
    delay = 15 / tempo
    factor = max(0.7, min(tempo / 110, 1.4))
    for hihat, snare in rhythm:
        left_power = round(STROKE[hihat][0] * factor)
        right_power = round(STROKE[snare][1] * factor)
        arms_motor_pair.start_tank_at_power(left_power, right_power)
        wait_for_seconds(delay)
    arms_motor_pair.stop()

hub.status_light.on('white')
hub.light_matrix.set_orientation('right')
hub.light_matrix.show('77077:00000:99999:99099:00000')

calibrate()

left_arm_motor.run_to_position(15, 'shortest path')
right_arm_motor.run_to_position(345, 'shortest path')

hub.speaker.play_sound('1234')

start_animation_cool()
play_drums(4, 80)
start_animation_cool(8)

wait_for_seconds(0.2)

play_drums(4, 130)
left_arm_motor.run_to_position(15, 'shortest path')
right_arm_motor.run_to_position(345, 'shortest path')

for _ in range(8):
    wait_for_seconds(0.1)
    arms_motor_pair.start_tank_at_power(-50, 50)
    wait_for_seconds(0.1)
    arms_motor_pair.start_tank_at_power(50, -50)

start_animation_happy()
hub.speaker.start_sound('Yes')

left_arm_motor.run_to_position(60, 'shortest path')
right_arm_motor.run_to_position(335, 'shortest path')

legs_motor_pair.move(3, 'cm')
legs_motor_pair.move(2.5, 'cm', -100)

for _ in range(3):
    right_arm_motor.start_at_power(40)
    wait_for_seconds(0.12)
    right_arm_motor.start_at_power(-40)
    wait_for_seconds(0.12)

right_arm_motor.run_to_position(300, 'shortest path')
left_arm_motor.run_for_seconds(0.5, -75)
left_arm_motor.run_to_position(25, 'shortest path')

legs_motor_pair.move(5, 'cm', 100)

for _ in range(3):
    left_arm_motor.start_at_power(-40)
    wait_for_seconds(0.12)
    left_arm_motor.start_at_power(40)
    wait_for_seconds(0.12)

left_arm_motor.run_to_position(60, 'shortest path')
right_arm_motor.run_for_seconds(0.5, 75)
right_arm_motor.run_to_position(345, 'shortest path')
left_arm_motor.run_to_position(15, 'shortest path')

start_animation_blinking()

legs_motor_pair.move(2.5, 'cm', -100)
legs_motor_pair.move(-3, 'cm')
