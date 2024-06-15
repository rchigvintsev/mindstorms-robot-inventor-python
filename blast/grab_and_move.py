from mindstorms import MSHub, Motor, MotorPair, ColorSensor
from mindstorms.control import wait_for_seconds, Timer

ANIM_SCANNING = [
    '00000:00000:56789:00000:00000',
    '00000:00000:45698:00000:00000',
    '00000:00000:34987:00000:00000',
    '00000:00000:29876:00000:00000',
    '00000:00000:98765:00000:00000',
    '00000:00000:89654:00000:00000',
    '00000:00000:78943:00000:00000',
    '00000:00000:67892:00000:00000'
]

wheels_motor_pair = MotorPair('C', 'A')
wheels_motor_pair.set_default_speed(20)

left_leg_motor = Motor('C')
right_leg_motor = Motor('C')

arms_and_head_motor = Motor('D')
claw_motor = Motor('B')

color_sensor = ColorSensor('E')

hub = MSHub()
hub.status_light.on('red')
hub.light_matrix.set_orientation('left')

def start_animation_scanning():
    hub.light_matrix.start_animation(ANIM_SCANNING, 5, True, 'overlay', False)

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

start_animation_scanning()
calibrate()

right_leg_motor.set_degrees_counted(0)
claw_motor.run_for_seconds(1)
arms_and_head_motor.run_for_degrees(-80)

hub.speaker.start_sound('Scanning')
wheels_motor_pair.start()
color_sensor.wait_until_color('red')

wheels_motor_pair.stop()
hub.speaker.play_sound('Target Acquired')
wheels_motor_pair.move(-4, 'cm')
wheels_motor_pair.move(3, 'cm', -100)
arms_and_head_motor.run_for_degrees(-100)
wheels_motor_pair.move(6, 'cm')
hub.speaker.start_sound('Grab')
claw_motor.start_at_power(-50)
wait_for_seconds(0.5)
arms_and_head_motor.run_for_degrees(-200)
wheels_motor_pair.move(-8, 'cm')
left_leg_motor.run_for_degrees(620, 50)
arms_and_head_motor.run_for_degrees(150)

wheels_motor_pair.set_default_speed(80)
wheels_motor_pair.move(right_leg_motor.get_degrees_counted(), 'degrees')
arms_and_head_motor.run_for_degrees(-100)
claw_motor.run_to_degrees_counted(-50, 75)
arms_and_head_motor.run_for_degrees(250)
wheels_motor_pair.move(1, 'cm', -100)
hub.speaker.play_sound('Mission Accomplished')
