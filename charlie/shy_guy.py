from mindstorms import MSHub, Motor, MotorPair, ColorSensor, DistanceSensor, App
from mindstorms.control import wait_for_seconds, wait_until, Timer
from mindstorms.operator import greater_than, greater_than_or_equal_to, less_than, less_than_or_equal_to, equal_to, not_equal_to

ANIM_BLINKING = ['77077:00000:99099:99099:00000'] * 5 + [
    '77077:00000:00000:77077:00000',
    '77077:00000:00000:00000:00000',
    '77077:00000:00000:77077:00000'
] + ['77077:00000:99099:99099:00000'] * 8

ANIM_LOOKING = ['77077:00000:88088:98098:00000', '77077:00000:88088:89089:00000']

ANIM_SCARED = ['00000:00000:99099:99099:00000'] + ['00000:99900:99900:99909:00000'] * 2 + ['00000:00000:99099:99099:00000'] + ['00000:00999:00999:90999:00000'] * 2

hub = MSHub()

left_arm_motor = Motor('B')
left_arm_motor.set_default_speed(-75)
right_arm_motor = Motor('F')
right_arm_motor.set_default_speed(75)

leg_motor_pair = MotorPair('A', 'E')
leg_motor_pair.set_default_speed(80)

arm_motor_pair = MotorPair('F', 'B')
arm_motor_pair.set_default_speed(75)

distance_sensor = DistanceSensor('D')

def start_animation_blinking():
    hub.light_matrix.start_animation(ANIM_BLINKING, 8, True, 'overlay', False)

def start_animation_looking():
    hub.light_matrix.start_animation(ANIM_LOOKING, 1, True, 'direct', False)

def start_animation_scared():
    hub.light_matrix.start_animation(ANIM_SCARED, 8, True, 'overlay', False)

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

hub.status_light.on('red')
hub.light_matrix.set_orientation('right')
start_animation_blinking()

calibrate()

while True:
    start_animation_looking()
    distance_sensor.light_up_all(100)

    while True:
        distance = distance_sensor.get_distance_cm()
        if distance != None and distance < 30:
            break
        wait_for_seconds(0.1)

    distance_sensor.light_up_all(0)
    start_animation_scared()
    hub.speaker.start_sound('Scared')
    arm_motor_pair.move(90, 'degrees')
    leg_motor_pair.move(-15, 'cm')
    leg_motor_pair.move(20, 'cm', 100)
    hub.speaker.start_sound('Scared')
    leg_motor_pair.move(30, 'cm')
    leg_motor_pair.move(20, 'cm', 100)
    hub.speaker.play_sound('Scared')
    arm_motor_pair.move(-90, 'degrees')
