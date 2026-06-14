from mindstorms import MSHub, Motor, MotorPair, ColorSensor, DistanceSensor, App
from mindstorms.control import wait_for_seconds, wait_until, Timer
from mindstorms.operator import greater_than, greater_than_or_equal_to, less_than, less_than_or_equal_to, equal_to, not_equal_to
import math
import utime


hub = MSHub()
motors = (Motor('A'), Motor('B'), Motor('C'), Motor('D'))
distance_sensor = DistanceSensor('E')
timer = Timer()

def set_initial_position():
    motors[0].run_to_position(90, 'clockwise')
    motors[2].run_to_position(45, 'clockwise')
    motors[1].run_to_position(270, 'counterclockwise')
    motors[3].run_to_position(315, 'counterclockwise')

def stop_motors():
    for motor in motors:
        motor.stop()

def run_motors_to_position(position, speed=15):
    for motor in motors:
        motor.run_to_position(position, 'shortest path', 15)

def wait(seconds):
    timer.reset()
    while timer.now() <= seconds:
        orientation = hub.motion_sensor.get_orientation()
        if orientation == 'back':
            hub.speaker.play_sound('Deactivate')
            stop_motors()
            raise SystemExit
        wait_for_seconds(0.03)

distance_sensor.light_up_all()
hub.speaker.play_sound('Initialize')
set_initial_position()
motors[-1].run_to_position(0, 'counterclockwise')

hub.speaker.start_sound('Activate')
motors[2].start_at_power(50)
motors[3].start_at_power(50)
motors[0].start_at_power(-50)
motors[1].start_at_power(50)
wait(10)

hub.speaker.start_sound('Kick')
motors[2].start_at_power(70)
motors[3].start_at_power(60)
motors[0].start_at_power(-60)
motors[1].start_at_power(70)
wait(10)

hub.speaker.start_sound('Kick')
motors[2].start_at_power(80)
motors[3].start_at_power(80)
motors[0].start_at_power(-80)
motors[1].start_at_power(80)
wait(10)

stop_motors()
hub.speaker.start_sound('Deactivate')
run_motors_to_position(180)
distance_sensor.light_up_all(0)
wait_for_seconds(2)
raise SystemExit
