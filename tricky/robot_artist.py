from mindstorms import MSHub, Motor, MotorPair, ColorSensor, DistanceSensor, App
from mindstorms.control import wait_for_seconds, wait_until, Timer
from mindstorms.operator import greater_than, greater_than_or_equal_to, less_than, less_than_or_equal_to, equal_to, not_equal_to
import math

WHEEL_DIAMETER = 55.8 # Robot wheel diameter in millimeters
DISTANCE_BETWEEN_WHEELS = 112 # in millimeters
R = 5.0 # Radius of the circle in centimeters in which the star is inscribed

DIRECTION_LEFT  = -1
DIRECTION_RIGHT =  1

hub = MSHub()

wheels_motor_pair = MotorPair('B', 'A')
wheels_motor_pair.set_default_speed(30)

right_wheel_motor = Motor('A')

pen_motor = Motor('C')
pen_motor.run_to_position(165, 'shortest path')

def lift_pen():
    pen_motor.run_for_degrees(90, -100)

def lower_pen():
    pen_motor.run_for_degrees(90, 100)

def turn_angle_to_motor_degrees(angle):
    return angle * DISTANCE_BETWEEN_WHEELS / WHEEL_DIAMETER * 0.95

def turn(angle, direction):
    # Since pen is placed in front of the robot we cannot just turn to the desired direction.
    # At first we should move robot forward so its pivot point is exactly on the end of the drawn line.
    # Then we turn robot in the desired direction and move back so new line will be connected with the previous.

    wheels_motor_pair.move(8.5, 'cm')
    target_degrees_counted = turn_angle_to_motor_degrees(angle)
    right_wheel_motor.set_degrees_counted(0)
    if direction == DIRECTION_LEFT:
        steering = -100
    else:
        steering = 100
    wheels_motor_pair.start(steering)
    while True:
        degrees_counted = abs(right_wheel_motor.get_degrees_counted())
        if degrees_counted >= target_degrees_counted:
            wheels_motor_pair.stop()
            break
        wait_for_seconds(0.01)
    wheels_motor_pair.move(-8, 'cm')

def turn_left(angle):
    turn(angle, DIRECTION_LEFT)

def turn_right(angle):
    turn(angle, DIRECTION_RIGHT)

# Let's calculate the distance that robot must move in order to draw one leg of the star's ray.

# 36 is an angle between two lines coming from the center of the star: one line is passing through
# the top point of the star and another line is passing through the bottom point of the right leg
# of the star's ray.

# 126 is an angle between two lines coming from the bottom point of the right leg of the star's ray:
# one line is passing through the point of the star and another line is passing throught the center
# of the star.
d = round((R * math.sin(math.radians(36))) / math.sin(math.radians(126)))

# Drawing five rays of the star in a clockwise direction
for _ in range(5):
    lower_pen()
    wheels_motor_pair.move(d, 'cm')
    lift_pen()
    turn_left(62)
    lower_pen()
    wheels_motor_pair.move(d, 'cm')
    lift_pen()
    turn_right(144)
