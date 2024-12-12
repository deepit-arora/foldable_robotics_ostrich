import math
import time
from machine import Pin, PWM

# Servo PWM parameters
frequency = 50  # 50 Hz for standard servo
min_pulse = 500  # Extended minimum pulse width in microseconds (corresponds to -90 degrees)
max_pulse = 2500  # Extended maximum pulse width in microseconds (corresponds to 270 degrees)

# GPIO pins for servos
servo_pins = {
    "ankle1": 26,  # First leg ankle servo
    "knee1": 13,   # First leg knee servo
    "knee2": 25,   # Second leg knee servo
    "ankle2": 12,  # Second leg ankle servo
}

# Initialize PWM for servos
servos = {name: PWM(Pin(pin)) for name, pin in servo_pins.items()}
for servo in servos.values():
    servo.freq(frequency)

# Function to set servo angle
def set_servo_angle(servo, angle):
    """
    Set the servo angle by converting it to the appropriate duty cycle.
    :param servo: PWM object for the servo
    :param angle: Angle in degrees (0-180)
    """
    angle = max(0, min(180, angle))  # Clamp angle to valid range
    pulse_width = min_pulse + (angle / 180) * (max_pulse - min_pulse)
    servo.duty_ns(int(pulse_width * 1000))  # Convert microseconds to nanoseconds

# Set all servos to their home position
def set_home_position():
    """
    Set all servos to their home position (default: 90 degrees).
    """
    home_angle = 90  # Home position for all servos
    for name, servo in servos.items():
        set_servo_angle(servo, home_angle)
    print("All servos set to home position (90 degrees).")
    time.sleep(1)  # Allow servos to move to the home position

# Motion parameters
amplitude = 90  # Increased amplitude for servos to rotate more
frequency_motion = 555.5  # Frequency in Hz
phase_offset = math.pi / 2  # 90-degree phase difference for alternating motion

# Main control loop
try:
    set_home_position()  # Initialize servos to home position
    start_time = time.time()  # Record start time for motion calculations
    while True:
        elapsed_time = time.time() - start_time

        # Calculate positions for knee servos (larger amplitude)
        knee_clockwise_pos = 60 * math.cos(2 * math.pi * frequency_motion * elapsed_time) + 90
        knee_clockwise_pos_yellow = max(45, min(90, knee_clockwise_pos))  # Clamp to valid range
        knee_clockwise_pos = max(90, min(120, knee_clockwise_pos))  # Clamp to valid range
        knee_counterclockwise_pos = 180 - knee_clockwise_pos
        knee_counterclockwise_pos_yellow = 180 - knee_clockwise_pos_yellow

        # Calculate positions for ankle servos (standard amplitude)
        ankle_clockwise_pos = amplitude * math.cos(2 * math.pi * frequency_motion * elapsed_time) + 90
        ankle_clockwise_pos = max(0, min(180, ankle_clockwise_pos))  # Clamp to valid range
        ankle_counterclockwise_pos = 180 - ankle_clockwise_pos

        # Apply motion to servos
        set_servo_angle(servos["knee1"], knee_counterclockwise_pos)  # Knee1 clockwise
        set_servo_angle(servos["ankle2"], ankle_clockwise_pos-5)  # Ankle2 clockwise
        set_servo_angle(servos["knee2"], knee_counterclockwise_pos_yellow)  # Knee2 counterclockwise
        set_servo_angle(servos["ankle1"], ankle_clockwise_pos)  # Ankle1 counterclockwise

        # Debug output
        print(f"Knee1: {knee_counterclockwise_pos}, Knee2: {knee_counterclockwise_pos}, Ankle1: {ankle_clockwise_pos}, Ankle2: {ankle_clockwise_pos}")
        
        time.sleep(0.001)  # Short delay for smoother motion

except KeyboardInterrupt:
    print("Motion stopped. Resetting servos to home position.")
    set_home_position()  # Reset servos to home position on exit
    for servo in servos.values():
        servo.deinit()
