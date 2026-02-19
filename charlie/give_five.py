from mindstorms import MSHub, Motor, MotorPair, ColorSensor, DistanceSensor, App
from mindstorms.control import wait_for_seconds, wait_until, Timer
from mindstorms.operator import greater_than, greater_than_or_equal_to, less_than, less_than_or_equal_to, equal_to, not_equal_to

ANIM_BLINKING = ['77077:00000:99099:99099:00000'] * 5 + [
    '77077:00000:00000:77077:00000',
    '77077:00000:00000:00000:00000',
    '77077:00000:00000:77077:00000'
] + ['77077:00000:99099:99099:00000'] * 8

ANIM_HI_FIVE = [
    '90909:90909:99909:90909:90909',
    '09990:09000:09900:00090:09900'
]

ANIM_HAPPY = [
    '77077:00000:98098:89089:00000',
    '77077:00000:89089:98098:00000'
]

hub = MSHub()

left_arm_motor = Motor('B')
left_arm_motor.set_default_speed(75)

right_arm_motor = Motor('F')
right_arm_motor.set_default_speed(75)

legs_motor_pair = MotorPair('A', 'E')

distance_sensor = DistanceSensor('D')

def start_animation_blinking():
    hub.light_matrix.start_animation(ANIM_BLINKING, 8, True, 'overlay', False)

def start_animation_hi_five():
    hub.light_matrix.start_animation(ANIM_HI_FIVE, 2, False, 'direct', False)

def start_animation_happy():
    hub.light_matrix.start_animation(ANIM_HAPPY, 8, True, 'overlay', False)

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

hub.status_light.on('yellow')
hub.light_matrix.set_orientation('right')
start_animation_blinking()
calibrate()
distance_sensor.light_up_all(100)

while True:
    distance = distance_sensor.get_distance_cm()
    if distance != None and distance < 12:
        break
    wait_for_seconds(0.1)

start_animation_hi_five()
hub.speaker.play_sound('Hi 5')
right_arm_motor.run_for_degrees(-120)
start_animation_blinking()

happy = False
timer = Timer()
while True:
    happy = right_arm_motor.get_speed() < -10
    if happy or timer.now() >= 5:
        break
    wait_for_seconds(0.01)

if happy:
    start_animation_happy()
    hub.speaker.start_sound('Yipee')
    right_arm_motor.run_to_position(0, 'clockwise')
else:
    hub.light_matrix.show('77077:00000:99999:99099:00008')
    hub.speaker.start_sound('Sad')
    right_arm_motor.run_to_position(0, 'clockwise')
    legs_motor_pair.move(-20, 'cm')

wait_for_seconds(3)
raise SystemExit
