from mindstorms import MSHub, MotorPair, DistanceSensor

hub = MSHub()

motor_pair = MotorPair('A', 'B')
motor_pair.set_default_speed(50)

distance_sensor = DistanceSensor('D')
distance_sensor.light_up_all()

while True:
    distance_sensor.wait_for_distance_closer_than(10, 'cm')
    motor_pair.move(71, 'cm', 100)
    motor_pair.move(71, 'cm', -100)
