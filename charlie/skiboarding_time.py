from mindstorms import MSHub, Motor, MotorPair, ColorSensor, DistanceSensor, App
from mindstorms.control import wait_for_seconds, wait_until, Timer
from mindstorms.operator import greater_than, greater_than_or_equal_to, less_than, less_than_or_equal_to, equal_to, not_equal_to

ANIM_COOL = ['00000:77077:99999:99099:00000', '77000:00077:99999:99099:00000'] * 2 + ['00000:77077:00000:99999:99099', '00077:77000:99999:99099:00000'] * 2
ARMS_SPEED = 60

hub = MSHub()

left_arm_motor = Motor('B')
left_arm_motor.set_default_speed(ARMS_SPEED)

right_arm_motor = Motor('F')
right_arm_motor.set_default_speed(ARMS_SPEED)

def start_animation_cool(fps=5):
    hub.light_matrix.start_animation(ANIM_COOL, 5, True, 'direct', False)

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

# Moves arms to the given position through the shortest path
def move_arms_to_position(position = 0):
    left_arm_degrees = left_arm_motor.get_degrees_counted()
    right_arm_degrees = right_arm_motor.get_degrees_counted()

    left_arm_motor_speed = 0
    right_arm_motor_speed = 0

    if left_arm_degrees != 0:
        if left_arm_degrees < 0:
            left_arm_motor_speed = ARMS_SPEED
        else:
            left_arm_motor_speed = -ARMS_SPEED

    if right_arm_degrees != 0:
        if right_arm_degrees < 0:
            right_arm_motor_speed = ARMS_SPEED
        else:
            right_arm_motor_speed = -ARMS_SPEED

    if left_arm_motor_speed != 0 or right_arm_motor_speed != 0:
        if left_arm_motor_speed != 0:
            left_arm_motor.start(left_arm_motor_speed)
        if right_arm_motor_speed != 0:
            right_arm_motor.start(right_arm_motor_speed)

        while left_arm_motor_speed != 0 or right_arm_motor_speed != 0:
            if left_arm_motor_speed != 0:
                left_arm_degrees = left_arm_motor.get_degrees_counted()
                if left_arm_degrees == 0 or (left_arm_motor_speed < 0 and left_arm_degrees < 0) or (left_arm_motor_speed > 0 and left_arm_degrees > 0):
                    left_arm_motor.stop()
                    left_arm_motor_speed = 0

            if right_arm_motor_speed != 0:
                right_arm_degrees = right_arm_motor.get_degrees_counted()
                if right_arm_degrees == 0 or (right_arm_motor_speed < 0 and right_arm_degrees < 0) or (right_arm_motor_speed > 0 and right_arm_degrees > 0):
                    right_arm_motor.stop()
                    right_arm_motor_speed = 0

hub.status_light.on('azure')
hub.light_matrix.set_orientation('right')
start_animation_cool()
calibrate()

hub.speaker.start_sound('Yipee')

for _ in range(6):
    move_arms_to_position()

    wait_for_seconds(0.2)

    left_arm_motor.start(-ARMS_SPEED)
    right_arm_motor.start(ARMS_SPEED)

    while left_arm_motor.get_degrees_counted() > -85 and right_arm_motor.get_degrees_counted() < 85:
        pass

    left_arm_motor.stop()
    right_arm_motor.stop()

    wait_for_seconds(0.2)

move_arms_to_position()
hub.speaker.play_sound('Like')
