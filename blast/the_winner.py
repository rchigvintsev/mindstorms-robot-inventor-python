from mindstorms import MSHub, Motor, MotorPair, ColorSensor
from mindstorms.control import wait_for_seconds, Timer
from mindstorms.operator import greater_than, greater_than_or_equal_to, less_than, less_than_or_equal_to, equal_to, not_equal_to

ANIM_EQUALIZER = [
    '11111:18111:17717:66616:55555',
    '19100:18108:77177:66166:55555',
    '11109:18108:77177:66166:55555',
    '19111:18181:77171:66661:55555',
    '11191:18181:17771:66666:55555',
    '11911:18818:17777:16666:55555',
    '11911:11818:17777:66666:55555',
    '91111:81181:71771:66666:55555',
    '11191:81181:71171:61661:55555',
    '11111:11181:71171:61666:55555',
    '11111:11181:71777:61666:55555',
    '11911:11818:17717:66666:55555',
    '11919:11818:11717:11666:15555',
    '19111:18181:17177:66666:55555'
]

timer = Timer()

wheels_motor_pair = MotorPair('C', 'A')
wheels_motor_pair.set_default_speed(80)

left_leg_motor = Motor('C')
right_leg_motor = Motor('A')

arms_and_head_motor = Motor('D')
claw_motor = Motor('B')

color_sensor = ColorSensor('E')

hub = MSHub()
hub.status_light.on('black')
hub.light_matrix.set_orientation('left')

def start_animation_equalizer():
    hub.light_matrix.start_animation(ANIM_EQUALIZER, 5, True, 'direct', False)

def calibrate():
    timer = Timer()
    arms_and_head_motor.start_at_power(100)
    wait_for_seconds(0.3)
    while arms_and_head_motor.get_speed() > 50 and timer.now() < 3:
        pass
    arms_and_head_motor.stop()
    wait_for_seconds(0.2)
    hub.motion_sensor.reset_yaw_angle()
    wait_for_seconds(0.1)
    timer.reset()
    arms_and_head_motor.start(-50)
    while hub.motion_sensor.get_yaw_angle() > -42 and timer.now() < 2:
        pass
    arms_and_head_motor.stop()
    wait_for_seconds(0.2)
    arms_and_head_motor.set_degrees_counted(0)

start_animation_equalizer()
calibrate()

power = 0
i = 1
while True:
    color = color_sensor.get_color()
    if not_equal_to(color, None):
        if equal_to(color, 'blue'):
            hub.status_light.on('blue')
            hub.speaker.start_sound('Whirl')
            wheels_motor_pair.move(35, 'cm', -100)
        elif equal_to(color, 'green'):
            hub.status_light.on('green')
            hub.speaker.start_sound('Scanning')
            wheels_motor_pair.stop()
            for _ in range(6):
                right_leg_motor.run_for_degrees(90, -80)
                left_leg_motor.run_for_degrees(90, 80)
        elif equal_to(color, 'yellow'):
            hub.status_light.on('yellow')
            hub.speaker.start_sound('Laugh')
            wheels_motor_pair.stop()
            for _ in range(3):
                wheels_motor_pair.move(6, 'cm', -100)
                wheels_motor_pair.move(6, 'cm', 100)
        elif equal_to(color, 'red'):
            hub.status_light.on('red')
            hub.speaker.start_sound('Affirmative')
            wheels_motor_pair.stop()
            arms_and_head_motor.run_for_degrees(600, 100)
            arms_and_head_motor.run_for_degrees(1200, -100)
            arms_and_head_motor.run_for_degrees(600, 100)

        hub.status_light.on('black')

    wheels_motor_pair.start_at_power(power, 0)
    power += i
    if power > 40 or power < -40:
        i *= -1
    wait_for_seconds(0.003)
