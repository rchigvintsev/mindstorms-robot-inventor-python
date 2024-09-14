from mindstorms import MSHub, Motor
from mindstorms.control import wait_for_seconds, Timer

hub = MSHub()
steering_motor = Motor('A')
driving_motor = Motor('B')

def calibrate():
    timer = Timer()
    timer.reset()
    steering_motor.start(80)
    wait_for_seconds(0.5)
    while steering_motor.get_speed() > 10 and timer.now() < 2:
        pass
    steering_motor.stop()
    wait_for_seconds(0.2)
    pos = (15 - steering_motor.get_position()) % 30
    steering_motor.set_degrees_counted(90 - pos)
    steering_motor.run_to_degrees_counted(0, 35)

calibrate()

steering_motor.run_to_degrees_counted(50, 35)
driving_motor.set_default_speed(80)
driving_motor.run_for_rotations(-16)
