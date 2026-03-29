import hub, utime
from mindstorms import MSHub, DistanceSensor

ANIM_PULSE = ['00000:00000:00009:00000:00000', '00000:00000:98765:00000:00000']
MOTOR_POSITIONING_ERROR = 5


def enum(**enums: int):
    return type('Enum', (), enums)


RotationDirection = enum(CLOCKWISE=1, COUNTERCLOCKWISE=-1)
Interpolation = enum(LINEAR=1)


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

    def pause(self):
        self.__pause_time = utime.ticks_ms()
        self.__paused = True

    def resume(self):
        self.__start_time += utime.ticks_diff(utime.ticks_ms(), self.__pause_time)
        self.__paused = False

    def stop(self):
        self.__running = False
        self.__paused = False

    def wait_for_millis(self, millis):
        self.run_for_millis((lambda _: None), millis)

    def wait_for_func(self, func, delay=0):
        self.start()
        self.__wait_for_delay(delay)
        while not func(self.time):
            self.__sleep()
        self.stop()

    def run_for_millis(self, func, millis, delay=0):
        self.start()
        self.__wait_for_delay(delay)
        ticks = self.time
        while ticks < millis:
            func(ticks)
            self.__sleep()
            ticks = self.time
        self.stop()

    def __wait_for_delay(self, delay):
        if delay > 0:
            while self.time < delay:
                self.__sleep()

    def __sleep(self):
        utime.sleep_ms(10)


def linear_interpolation(keyframes, wrap=True, time_offset=0):
    cycle_time = keyframes[-1][0]

    if cycle_time == 0:
        # Just stay at initial position
        return lambda ticks: keyframes[0][1]

    min_pos = keyframes[0][1]
    max_pos = keyframes[-1][1]
    accumulation_per_cycle = (max_pos - min_pos)

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
                interpolated_pos = (prev_frame_pos + progress * pos_diff)
                return current_cycles * accumulation_per_cycle + interpolated_pos

        return 0

    return interpolate


class MotorDrive:
    def __init__(self, motor, positive_direction=RotationDirection.CLOCKWISE, default_speed=70):
        # To allow using of both hub.port.X.motor and Motor('X') objects
        self.__motor = (motor._motor_wrapper.motor if '_motor_wrapper' in dir(motor) else motor)
        self.__positive_direction = positive_direction
        self.__default_speed = default_speed

    def reset(self):
        """Resets the internal tacho to the current absolute position"""
        self.__motor.preset(self.__absolute_position)

    @property
    def running(self):
        """Checks if the motor is running"""
        return self.__power > 0

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
        current_pos = self.relative_position
        return position - MOTOR_POSITIONING_ERROR <= current_pos <= position + MOTOR_POSITIONING_ERROR

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
    def __init__(self, drive, keyframes, wrap=True, time_offset=0, interpolation=Interpolation.LINEAR):
        self.__drive = drive

        # Sort by frame time
        keyframes.sort(key=lambda kf: kf[0])

        if len(keyframes) == 0 or keyframes[0][0] != 0:
            # Add zero time frame with the motor in the current position
            keyframes.insert(0, (0, drive.relative_position))

        if interpolation == Interpolation.LINEAR:
            self.__interpolation_func = linear_interpolation(keyframes, wrap, time_offset)
        else:
            raise Exception('Unsupported interpolation: ' + str(interpolation))

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

        if abs(power) > 100:
            power = min(max(power, -100), 100)

        # If the power is less than 20% the motor won't move
        if abs(power) < 20:
            power = 20 if power > 0 else -20

        return power


class WalkAnimationManager:
    CYCLE_TIME_MILLIS = 700

    # (time in millis, motor position)
    KEYFRAMES = [
        (0, -20),
        (CYCLE_TIME_MILLIS * 0.63, 45),
        (CYCLE_TIME_MILLIS, 340)
    ]

    def __init__(self, legs):
        self.__legs = legs

        self.__animations = [
            # Right rear leg animation
            MotionAnimation(legs[0], WalkAnimationManager.KEYFRAMES, True),
            # Left rear leg animation
            MotionAnimation(legs[1], WalkAnimationManager.KEYFRAMES, True, WalkAnimationManager.CYCLE_TIME_MILLIS / 2),
            # Right front leg animation
            MotionAnimation(legs[2], WalkAnimationManager.KEYFRAMES, True, WalkAnimationManager.CYCLE_TIME_MILLIS / 2),
            # Left front leg animation
            MotionAnimation(legs[3], WalkAnimationManager.KEYFRAMES, True)
        ]

        self.__left_side_timer = AdvancedTimer()
        self.__right_side_timer = AdvancedTimer()

    def walk(self, time):
        self.reset()

        self.__left_side_timer.start()
        self.__right_side_timer.start()

        left_ticks = self.__left_side_timer.time
        right_ticks = self.__right_side_timer.time

        while left_ticks < time or right_ticks < time:
            self.__run_left(left_ticks)
            self.__run_right(right_ticks)

            utime.sleep_ms(10)

            left_ticks = self.__left_side_timer.time
            right_ticks = self.__right_side_timer.time

        self.__left_side_timer.stop()
        self.__right_side_timer.stop()

        self.stop()

    def reset(self):
        for leg in self.__legs:
            leg.reset()

    def stop(self):
        for leg in self.__legs:
            leg.stop()
        self.__set_idle()

    def __set_idle(self):
        for i in range(4):
            leg = self.__legs[i]
            if i % 2 == 0:
                # Turn right side motors clockwise
                leg.absolute_position = 40
            else:
                # Turn left side motors counterclockwise
                leg.absolute_position = 320

    def __run_left(self, ticks):
        self.__animations[1].run(ticks)
        self.__animations[3].run(ticks)

    def __run_right(self, ticks):
        self.__animations[0].run(ticks)
        self.__animations[2].run(ticks)

    def __stop_left(self):
        self.__legs[1].stop()
        self.__legs[3].stop()

    def __stop_right(self):
        self.__legs[0].stop()
        self.__legs[2].stop()


ms_hub = MSHub()
distance_sensor = DistanceSensor('E')
walk_anim_manager = WalkAnimationManager([
    # Right rear leg motor
    MotorDrive(hub.port.A.motor, RotationDirection.COUNTERCLOCKWISE),
    # Left rear leg motor
    MotorDrive(hub.port.B.motor),
    # Right front leg motor
    MotorDrive(hub.port.C.motor, RotationDirection.COUNTERCLOCKWISE),
    # Left front leg motor
    MotorDrive(hub.port.D.motor)
])


def start_animation_pulse():
    ms_hub.light_matrix.start_animation(ANIM_PULSE, 2, True, 'slide left')


def walk(time=10_000):
    walk_anim_manager.walk(time)


distance_sensor.light_up_all()
ms_hub.light_matrix.set_orientation('left')
start_animation_pulse()
ms_hub.speaker.start_sound('Initialize')
walk()

raise SystemExit
