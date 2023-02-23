from mindstorms import MSHub, Motor, MotorPair, ColorSensor, DistanceSensor, App
from mindstorms.control import wait_for_seconds, wait_until, Timer
from mindstorms.operator import greater_than, greater_than_or_equal_to, less_than, less_than_or_equal_to, equal_to, not_equal_to

from utime import ticks_diff, ticks_ms

import math

class Timer():
    """Replacement Timer class that allows decimal points so we can measure times of less than one second."""
    def __init__(self):
        self.start_ticks = 0

    def now(self):
        """Returns the time in seconds since the timer was last reset."""
        return ticks_diff(ticks_ms(), self.start_ticks) / 1000

    def reset(self):
        """Resets the timer."""
        self.start_ticks = ticks_ms()

ANIM_BLINKING = ['77077:00000:99099:99099:00000'] * 5 + [
    '77077:00000:00000:77077:00000',
    '77077:00000:00000:00000:00000',
    '77077:00000:00000:77077:00000'
] + ['77077:00000:99099:99099:00000'] * 8

ANIM_SILLY = [
    '07077:70000:00099:99099:99000',
    '77070:00007:99000:99099:00099'
]

hub = MSHub()

shopping_cart_shake_timer = Timer()

arm_motor_pair = MotorPair('F', 'B')

left_leg_motor = Motor('A')
left_leg_motor.set_default_speed(-70)

right_leg_motor = Motor('E')
right_leg_motor.set_default_speed(70)

def start_animation_blinking():
    hub.light_matrix.start_animation(ANIM_BLINKING, 8, True, 'overlay', False)

def start_animation_silly():
    hub.light_matrix.start_animation(ANIM_SILLY, 2, True, 'direct', False)

def run():
    left_leg_motor.set_degrees_counted(0)
    right_leg_motor.set_degrees_counted(0)

    left_leg_motor.start()
    right_leg_motor.start()

    # About 100 cm
    max_degrees = 2000
    while abs(left_leg_motor.get_degrees_counted()) < max_degrees or abs(right_leg_motor.get_degrees_counted()) < max_degrees:
        yield True

    left_leg_motor.stop()
    right_leg_motor.stop()


def start_running():
    yield from run()

def shopping_cart_shake_delay():
    shopping_cart_shake_timer.reset()
    while shopping_cart_shake_timer.now() < 1:
        yield True

def shake_shopping_cart():
    yield from shopping_cart_shake_delay()

    start_animation_silly()
    
    for i in range(5):
        shopping_cart_shake_timer.reset()
        arm_motor_pair.start(0, -40)
        while shopping_cart_shake_timer.now() < 0.3:
            yield True
        arm_motor_pair.stop()

        shopping_cart_shake_timer.reset()
        arm_motor_pair.start(0, 40)
        while shopping_cart_shake_timer.now() < 0.2:
            yield True
        arm_motor_pair.stop()

def start_shopping_cart_shaking():
    yield from shake_shopping_cart()

hub.status_light.on('pink')
hub.light_matrix.set_orientation('right')
start_animation_blinking()

run_generator = start_running()
shake_shopping_cart_generator = start_shopping_cart_shaking()

hub.speaker.start_sound('Humming')
while True:
    run_result = next(run_generator, None)
    shake_result = next(shake_shopping_cart_generator, None)
    if run_result == None and shake_result == None:
        break
    wait_for_seconds(0.01)

hub.speaker.play_sound('Delivery')
start_animation_blinking()
