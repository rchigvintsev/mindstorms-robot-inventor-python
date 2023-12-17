from mindstorms import MSHub, Motor, MotorPair, ColorSensor, DistanceSensor, App
from mindstorms.control import wait_for_seconds, wait_until, Timer
from mindstorms.operator import greater_than, greater_than_or_equal_to, less_than, less_than_or_equal_to, equal_to, not_equal_to
from hub import port

DIRECTION_RIGHT =  1
DIRECTION_LEFT  = -1

MIN_SPEED = 30
MAX_SPEED = 50
SPEED_HISTORY_LENGTH = 5

MAX_STEERING = 100

REFLECTED_LIGHT_LINE_LOWER_THRESHOLD_RIGHT = 20
REFLECTED_LIGHT_LINE_LOWER_THRESHOLD_LEFT  = 15
REFLECTED_LIGHT_LINE_UPPER_THRESHOLD_RIGHT = 90
REFLECTED_LIGHT_LINE_UPPER_THRESHOLD_LEFT  = 75

hub = MSHub()
wheel_motor_pair = MotorPair('B', 'A')
color_sensor_right = ColorSensor('E')
color_sensor_left = port.F.device # Color and distance sensor from LEGO Boost
color_sensor_left.mode(3) # In mode 3 sensor will measure reflected light

speed_history = [0] * SPEED_HISTORY_LENGTH

def filter_speed(speed):
    speed_history.pop(0)
    speed_history.append(speed)

    speed_sum = 0
    for v in speed_history:
        speed_sum = speed_sum + v
    return round(speed_sum / SPEED_HISTORY_LENGTH)

hub.speaker.play_sound('1234')

while True:
    right_light = color_sensor_right.get_reflected_light()
    left_light = color_sensor_left.get()[0]

    # For right sensor values of reflected light less than or equal REFLECTED_LIGHT_LINE_LOWER_THRESHOLD_RIGHT mean that sensor "sees" black line. 
    # Values more than or equal REFLECTED_LIGHT_LINE_THRESHOLD_RIGHT mean that sensor "sees" white area. Therefore the range in which we will 
    # regulate robot's steering is from REFLECTED_LIGHT_LINE_LOWER_THRESHOLD_RIGHT to REFLECTED_LIGHT_LINE_UPPER_THRESHOLD_RIGHT percents of 
    # reflected light where <=REFLECTED_LIGHT_LINE_LOWER_THRESHOLD_RIGHT means max steering and REFLECTED_LIGHT_LINE_UPPER_THRESHOLD_RIGHT is 
    # zero steering. At first we need to invert reflected light value by substracting measured value from upper bound of our range. Now values 
    # of reflected light will be in a range from 0 to (REFLECTED_LIGHT_LINE_UPPER_THRESHOLD_RIGHT - REFLECTED_LIGHT_LINE_LOWER_THRESHOLD_RIGHT). 
    # Then we need to translate this range to steering range from 0 to MAX_STEERING by multiplying reflected light value by (MAX_STEERING / 
    # (REFLECTED_LIGHT_LINE_UPPER_THRESHOLD_RIGHT - REFLECTED_LIGHT_LINE_LOWER_THRESHOLD_RIGHT)). Finally we need to round the result, limit it 
    # to MAX_STEERING and change sign depending on which sensor value we are reading.
    # 
    # The same procedure is applied to the left sensor except that it "sees" black line when its values are less than or equal 
    # REFLECTED_LIGHT_LINE_LOWER_THRESHOLD_LEFT, and it "sees" white area when its values are greater than or equal REFLECTED_LIGHT_LINE_UPPER_THRESHOLD_LEFT.
    steering = 0
    if right_light < REFLECTED_LIGHT_LINE_UPPER_THRESHOLD_RIGHT:
        steering = min(round((REFLECTED_LIGHT_LINE_UPPER_THRESHOLD_RIGHT - right_light) * 1.43), MAX_STEERING) * DIRECTION_RIGHT
    elif left_light < REFLECTED_LIGHT_LINE_UPPER_THRESHOLD_LEFT:
        steering = steering + min(round((REFLECTED_LIGHT_LINE_UPPER_THRESHOLD_LEFT - left_light) * 1.67), MAX_STEERING) * DIRECTION_LEFT

    # Translate steering value to robot's speed so when steering value is MAX_STEERING robot's speed is MIN_SPEED and vice versa.
    # Make changing of robot's speed a little smoother by taking average value from last SPEED_HISTORY_LENGTH computed values.
    speed = filter_speed(MIN_SPEED + round((MAX_STEERING - abs(steering)) * 0.2))
    wheel_motor_pair.start_at_power(speed, steering)

    # Wait a little to not flood sensors with requests.
    wait_for_seconds(0.01)
