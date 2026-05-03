# Inspired by this video from Anton's Mindstorms channel: https://www.youtube.com/watch?v=GRdy6kBNJLM
# Also his repository: https://github.com/AntonsMindstorms/robot_tools

import hub, utime, random
from mindstorms import MSHub, DistanceSensor, ColorSensor
from mindstorms.operator import equal_to

ANIM_PULSE = ['00000:00000:00009:00000:00000', '00000:00000:98765:00000:00000']

MOTOR_POSITIONING_ERROR = 5
MOTOR_MIN_POWER = 20
MOTOR_MAX_POWER = 100
MOTOR_DEFAULT_SPEED = 50

NORMAL_TIME_SCALE   = 1
OBSTACLE_TIME_SCALE = 0.75

COLOR_STOP   = 'red'
COLOR_PAUSE  = 'yellow'
COLOR_RESUME = 'green'
COLOR_NONE   = 'none'

MAX_DISTANCE_CM = 200

REAR_RIGHT_LEG  = 0
REAR_LEFT_LEG   = 1
FRONT_RIGHT_LEG = 2
FRONT_LEFT_LEG  = 3


def enum(**enums: int):
    return type('Enum', (), enums)


RotationDirection = enum(CLOCKWISE=1, COUNTERCLOCKWISE=-1)
TurnDirection = enum(LEFT=1, RIGHT=-1)


def linear_interpolation(keyframes, time_offset=0, wrap=True):
    # Sort by frame time without changing the source keyframe list
    keyframes = list(keyframes)
    keyframes.sort(key=lambda kf: kf[0])

    cycle_time = keyframes[-1][0]

    if cycle_time == 0:
        # Just stay at initial position
        return lambda ticks: keyframes[0][1]

    min_pos = keyframes[0][1]
    max_pos = keyframes[-1][1]
    accumulation_per_cycle = max_pos - min_pos

    def interpolate(ticks):
        ticks -= time_offset

        if ticks < 0:
            # Wait for time_offset while staying at initial position
            return keyframes[0][1]

        if not wrap:
            if ticks == 0:
                return min_pos

            if ticks >= keyframes[-1][0]:
                return max_pos

        current_time = ticks % cycle_time
        current_cycles = ticks // cycle_time

        for i in range(len(keyframes)):
            frame_time = keyframes[i][0]
            frame_pos = keyframes[i][1]

            if current_time < frame_time:
                prev_frame_time = keyframes[i - 1][0]
                prev_frame_pos = keyframes[i - 1][1]

                time_diff = frame_time - prev_frame_time
                pos_diff = frame_pos - prev_frame_pos

                progress = (current_time - prev_frame_time) / time_diff
                interpolated_pos = prev_frame_pos + progress * pos_diff
                return current_cycles * accumulation_per_cycle + interpolated_pos

        return 0

    return interpolate


class AdvancedTimer:
    def __init__(self):
        self.__start_time = 0
        self.__pause_time = 0

        self.__running = False
        self.__paused = False

        self.__time_scale = 1.0
        self.__time_offset = 0

    @property
    def running(self):
        return self.__running

    @property
    def paused(self):
        return self.running and self.__paused

    @property
    def time(self):
        if not self.running:
            return 0

        if self.paused:
            return utime.ticks_diff(self.__pause_time, self.__start_time) * self.time_scale

        return self.__time_offset + utime.ticks_diff(utime.ticks_ms(), self.__start_time) * self.time_scale

    @property
    def time_scale(self):
        return self.__time_scale

    @time_scale.setter
    def time_scale(self, value):
        if self.running:
            self.__time_offset += utime.ticks_diff(utime.ticks_ms(), self.__start_time) * self.time_scale
            self.__start_time = utime.ticks_ms()

        self.__time_scale = value

    def start(self):
        self.__start_time = utime.ticks_ms()
        self.__pause_time = 0

        self.__running = True
        self.__paused = False

        self.__time_offset = 0

    def stop(self):
        self.__running = False
        self.__paused = False

    def restart(self):
        self.stop()
        self.start()

    def pause(self):
        self.__pause_time = utime.ticks_ms()
        self.__paused = True

    def resume(self):
        self.__start_time += utime.ticks_diff(utime.ticks_ms(), self.__pause_time)
        self.__paused = False

    def sleep(self):
        utime.sleep_ms(10)


class MotorDrive:
    def __init__(self, motor, positive_direction=RotationDirection.CLOCKWISE, default_speed=70):
        # To allow using of both hub.port.X.motor and Motor('X') objects
        self.__motor = motor._motor_wrapper.motor if '_motor_wrapper' in dir(motor) else motor
        self.__positive_direction = positive_direction
        self.__default_speed = default_speed

    def reset(self):
        """Resets the internal tacho to the current absolute position"""
        self.__motor.preset(self.__absolute_position)

    @property
    def running(self):
        """Checks if the motor is running in any direction"""
        return self.__power != 0

    def run(self, speed):
        """Runs the motor with the given speed. If speed is not specified the default speed will be used."""
        if speed is None:
            speed = self.default_speed
        self.__motor.pwm(speed * self.__positive_direction)

    def stop(self):
        """Stops the motor"""
        self.run(0)

    @property
    def relative_position(self):
        """Returns the relative position taking into account the positive direction of rotation of the motor"""
        return self.__relative_position * self.__positive_direction

    def in_relative_position(self, position):
        """Checks whether the motor is in the given relative position"""
        return position - MOTOR_POSITIONING_ERROR <= self.relative_position <= position + MOTOR_POSITIONING_ERROR

    @property
    def absolute_position(self):
        """Returns the absolute position in the range from 0 to 360 degrees"""
        pos = self.__absolute_position
        if pos < 0:
            pos = 360 + pos
        return pos

    @absolute_position.setter
    def absolute_position(self, value):
        """Moves the motor to the given absolute position with the shortest path and default speed"""
        if self.in_absolute_position(value):
            return

        current_pos = self.absolute_position
        delta = abs(value - current_pos)
        direction = 1

        if (value > current_pos and delta > 180) or (value < current_pos and delta <= 180):
            direction = -1

        if delta > 180:
            delta = 360 - delta

        self.__motor.run_for_degrees(delta, self.default_speed * direction)

    def in_absolute_position(self, position):
        """Checks whether the motor is in the given absolute position"""
        current_pos = self.absolute_position

        left_bound = position - MOTOR_POSITIONING_ERROR
        if left_bound < 0:
            left_bound = 360 + left_bound

        right_bound = position + MOTOR_POSITIONING_ERROR
        if right_bound > 360:
            right_bound = right_bound - 360

        if left_bound < right_bound:
            return left_bound <= current_pos <= right_bound
        return current_pos >= left_bound or current_pos <= right_bound

    @property
    def default_speed(self):
        return self.__default_speed

    @default_speed.setter
    def default_speed(self, value):
        self.__default_speed = value

    @property
    def __relative_position(self):
        return self.__motor.get()[1]

    @property
    def __absolute_position(self):
        return self.__motor.get()[2]

    @property
    def __power(self):
        return self.__motor.get()[3]


class MotionAnimation:
    def __init__(self, drive, interpolation_func):
        self.__drive = drive
        self.__interpolation_func = interpolation_func

    def run(self, ticks):
        target_pos = self.__interpolation_func(ticks)
        # The motor may overshoot the target position and attempt to return. This will result in oscillations
        # as it tries to precisely reach the target position. Here, we allow for some positioning error.
        if self.__drive.in_relative_position(target_pos):
            self.__drive.stop()
        else:
            current_pos = self.__drive.relative_position
            self.__drive.run(self.__limit_motor_power(target_pos - current_pos))

    def stop(self):
        self.__drive.stop()

    def __limit_motor_power(self, power):
        power = int(power)
        if power == 0:
            return 0

        if abs(power) > MOTOR_MAX_POWER:
            power = min(max(power, -MOTOR_MAX_POWER), MOTOR_MAX_POWER)

        # If the power is less than MOTOR_MIN_POWER% the motor won't move
        if abs(power) < MOTOR_MIN_POWER:
            power = MOTOR_MIN_POWER if power > 0 else -MOTOR_MIN_POWER

        return power


class WalkAnimationManager:
    CYCLE_TIME_MILLIS = 700
    HALF_CYCLE_OFFSET = round(CYCLE_TIME_MILLIS / 2)

    # (time in millis, motor relative position)
    KEYFRAMES = [
        (0, -20),
        (CYCLE_TIME_MILLIS * 0.63, 45),
        (CYCLE_TIME_MILLIS, 340)
    ]

    # (time in millis, motor relative position)
    REVERSE_KEYFRAMES = [
        (0, -20),
        (CYCLE_TIME_MILLIS * 0.63, -85),
        (CYCLE_TIME_MILLIS, -380)
    ]

    def __init__(self, legs):
        self.__legs = legs

        self.__animations = self.__create_animations(legs, WalkAnimationManager.KEYFRAMES)
        self.__reverse_animations = self.__create_animations(legs, WalkAnimationManager.REVERSE_KEYFRAMES)

    def reset(self):
        for leg in self.__legs:
            leg.reset()

    def go_forward(self, ticks):
        for anim in self.__animations:
            anim.run(ticks)

    def go_backward(self, ticks):
        for anim in self.__reverse_animations:
            anim.run(ticks)

    def turn_left(self, ticks):
        self.__animations[REAR_RIGHT_LEG].run(ticks)
        self.__reverse_animations[REAR_LEFT_LEG].run(ticks)
        self.__animations[FRONT_RIGHT_LEG].run(ticks)
        self.__reverse_animations[FRONT_LEFT_LEG].run(ticks)

    def turn_right(self, ticks):
        self.__reverse_animations[REAR_RIGHT_LEG].run(ticks)
        self.__animations[REAR_LEFT_LEG].run(ticks)
        self.__reverse_animations[FRONT_RIGHT_LEG].run(ticks)
        self.__animations[FRONT_LEFT_LEG].run(ticks)

    def stop(self):
        self.__stop_legs()
        self.__move_to_idle_position()

    @staticmethod
    def __create_animations(legs, keyframes):
        return [
            # Right rear leg animation
            MotionAnimation(legs[REAR_RIGHT_LEG], linear_interpolation(keyframes)),
            # Left rear leg animation
            MotionAnimation(legs[REAR_LEFT_LEG], linear_interpolation(keyframes, WalkAnimationManager.HALF_CYCLE_OFFSET)),
            # Right front leg animation
            MotionAnimation(legs[FRONT_RIGHT_LEG], linear_interpolation(keyframes, WalkAnimationManager.HALF_CYCLE_OFFSET)),
            # Left front leg animation
            MotionAnimation(legs[FRONT_LEFT_LEG], linear_interpolation(keyframes))
        ]

    def __stop_legs(self):
        for leg in self.__legs:
            leg.stop()

    def __move_to_idle_position(self):
        for i in range(4):
            leg = self.__legs[i]
            if i % 2 == 0:
                # Right side motor
                leg.absolute_position = 20
            else:
                # Left side motor
                leg.absolute_position = 340


class ColorReader:
    def __init__(self, sensor):
        self.__sensor = sensor

    def read(self):
        color = self.__sensor.get_color()
        if equal_to(color, None):
            return COLOR_NONE
        return color


class DistanceReader:
    ALPHA = 0.3

    def __init__(self, sensor):
        self.__sensor = sensor
        self.__value = 100

    def read(self):
        self.__value = DistanceReader.ALPHA * self.__read_filtered() + (1 - DistanceReader.ALPHA) * self.__value
        return self.__value

    def __read_filtered(self, samples=7):
        values = []
        for _ in range(samples):
            values.append(self.__read())

        values.sort()
        trimmed_values = values[1:-1]
        if len(trimmed_values) == 0:
            return MAX_DISTANCE_CM

        return sum(trimmed_values) / len(trimmed_values)

    def __read(self):
        distance = self.__sensor.get_distance_cm()
        if equal_to(distance, None):
            return MAX_DISTANCE_CM
        return distance


class WanderBehavior:
    def __init__(self, color_reader, distance_reader, walk_manager, timer):
        self.__color_reader = color_reader
        self.__distance_reader = distance_reader
        self.__walk_manager = walk_manager
        self.__timer = timer

        self.__running = True
        self.__obstacle_detected = False
        self.__turn_direction = TurnDirection.RIGHT
        self.__distance = MAX_DISTANCE_CM
        self.__last_distance_read_time = 0

    def run(self):
        self.__start_walking(NORMAL_TIME_SCALE)

        while True:
            if self.__should_stop():
                break

            if self.__running:
                self.__update_distance_if_needed()
                self.__update_obstacle_state()
                self.__move()

            self.__timer.sleep()

        self.__stop_walking()

    def __should_stop(self):
        color = self.__color_reader.read()
        if color == COLOR_STOP:
            return True

        if color == COLOR_PAUSE:
            self.__pause()
        elif color == COLOR_RESUME:
            self.__resume()

        return False

    def __pause(self):
        if not self.__running:
            return

        self.__walk_manager.stop()
        self.__timer.stop()
        self.__running = False

    def __resume(self):
        if self.__running:
            return

        self.__start_walking(self.__current_time_scale)
        self.__running = True

    def __update_distance_if_needed(self):
        now = utime.ticks_ms()
        interval = self.__distance_read_interval

        if self.__last_distance_read_time == 0 or utime.ticks_diff(now, self.__last_distance_read_time) >= interval:
            self.__last_distance_read_time = now
            self.__distance = self.__distance_reader.read()

    def __update_obstacle_state(self):
        if not self.__obstacle_detected and self.__distance < 30:
            self.__start_avoiding_obstacle()
        elif self.__obstacle_detected and self.__distance > 100:
            self.__stop_avoiding_obstacle()

    def __start_avoiding_obstacle(self):
        self.__restart_walking(OBSTACLE_TIME_SCALE)
        self.__obstacle_detected = True
        self.__turn_direction = random.choice([TurnDirection.LEFT, TurnDirection.RIGHT])

    def __stop_avoiding_obstacle(self):
        self.__restart_walking(NORMAL_TIME_SCALE)
        self.__obstacle_detected = False

    def __move(self):
        ticks = self.__timer.time
        if not self.__obstacle_detected:
            self.__walk_manager.go_forward(ticks)
        elif self.__turn_direction == TurnDirection.RIGHT:
            self.__walk_manager.turn_right(ticks)
        else:
            self.__walk_manager.turn_left(ticks)

    @property
    def __distance_read_interval(self):
        if self.__obstacle_detected:
            return 1000
        return 100

    @property
    def __current_time_scale(self):
        if self.__obstacle_detected:
            return OBSTACLE_TIME_SCALE
        return NORMAL_TIME_SCALE

    def __start_walking(self, time_scale):
        self.__walk_manager.reset()
        self.__timer.time_scale = time_scale
        self.__timer.start()

    def __restart_walking(self, time_scale):
        self.__stop_walking()
        self.__start_walking(time_scale)

    def __stop_walking(self):
        self.__walk_manager.stop()
        self.__timer.stop()


class Gelo:
    def __init__(self):
        self.__hub = MSHub()
        self.__distance_sensor = DistanceSensor('E')
        self.__wander_behavior = WanderBehavior(
            ColorReader(ColorSensor('F')),
            DistanceReader(self.__distance_sensor),
            WalkAnimationManager(self.__create_legs()),
            AdvancedTimer()
        )

    def initialize(self):
        self.__distance_sensor.light_up_all()
        self.__hub.light_matrix.set_orientation('left')
        self.__hub.speaker.start_sound('Initialize')
        self.__start_animation_pulse()

    def wander(self):
        self.__wander_behavior.run()

    def __start_animation_pulse(self):
        self.__hub.light_matrix.start_animation(ANIM_PULSE, 2, True, 'slide left')

    def __create_legs(self):
        return [
            # Right rear leg motor.
            MotorDrive(hub.port.A.motor, RotationDirection.COUNTERCLOCKWISE, MOTOR_DEFAULT_SPEED),
            # Left rear leg motor.
            MotorDrive(hub.port.B.motor, RotationDirection.CLOCKWISE, MOTOR_DEFAULT_SPEED),
            # Right front leg motor.
            MotorDrive(hub.port.C.motor, RotationDirection.COUNTERCLOCKWISE, MOTOR_DEFAULT_SPEED),
            # Left front leg motor.
            MotorDrive(hub.port.D.motor, RotationDirection.CLOCKWISE, MOTOR_DEFAULT_SPEED)
        ]


def main():
    robot = Gelo()
    robot.initialize()
    robot.wander()


main()
raise SystemExit
