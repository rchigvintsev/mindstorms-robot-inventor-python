from mindstorms import MSHub, Motor, MotorPair, ColorSensor, DistanceSensor, App
from mindstorms.control import wait_for_seconds, wait_until, Timer
from mindstorms.operator import greater_than, greater_than_or_equal_to, less_than, less_than_or_equal_to, equal_to, not_equal_to
import math

hub = MSHub()

motor_pair = MotorPair('A', 'B')
motor_pair.set_default_speed(50)

distance_sensor = DistanceSensor('D')
distance_sensor.light_up_all()

while True:
    distance_sensor.wait_for_distance_closer_than(10, 'cm')
    motor_pair.move(71, 'cm', 100)
    motor_pair.move(71, 'cm', -100)
