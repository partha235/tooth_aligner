from machine import Pin, ADC, I2C
import time


# ============================================================
# LED
# ============================================================

led = Pin(2, Pin.OUT)


# ============================================================
# BUZZER
# ============================================================

buzzer = Pin(4, Pin.OUT)
buzzer.value(0)


# ============================================================
# QRE1113
# ============================================================

adc = ADC(Pin(25))
adc.atten(ADC.ATTN_11DB)
adc.width(ADC.WIDTH_12BIT)

THRESHOLD = 200


# ============================================================
# BOX ALERT
# ============================================================

# TEST
ONE_HOUR = 60

# FINAL:
# ONE_HOUR = 60 * 60

in_box_start = None
alert_triggered = False


# ============================================================
# DS3231
# ============================================================

i2c = I2C(
    0,
    scl=Pin(22),
    sda=Pin(21),
    freq=100000
)

RTC_ADDR = 0x68


# ============================================================
# FILE
# ============================================================

LOG_FILE = "events.txt"


# ============================================================
# BCD
# ============================================================

def bcd_to_dec(value):
    return (value >> 4) * 10 + (value & 0x0F)


# ============================================================
# RTC
# ============================================================

def get_datetime():

    data = i2c.readfrom_mem(RTC_ADDR, 0x00, 7)

    second = bcd_to_dec(data[0] & 0x7F)
    minute = bcd_to_dec(data[1])
    hour = bcd_to_dec(data[2] & 0x3F)

    day = bcd_to_dec(data[4])
    month = bcd_to_dec(data[5] & 0x1F)
    year = 2000 + bcd_to_dec(data[6])

    return year, month, day, hour, minute, second


# ============================================================
# DATETIME -> SECONDS
# ============================================================

def datetime_to_seconds(dt):

    year, month, day, hour, minute, second = dt

    days = 0

    # Previous years
    for y in range(2000, year):

        if (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0):
            days += 366
        else:
            days += 365

    # Previous months
    month_days = [
        31, 28, 31, 30, 31, 30,
        31, 31, 30, 31, 30, 31
    ]

    for m in range(1, month):

        days += month_days[m - 1]

        # Leap year February
        if m == 2:

            if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                days += 1

    days += day - 1

    total = days * 86400
    total += hour * 3600
    total += minute * 60
    total += second

    return total


# ============================================================
# CREATE LOG
# ============================================================

def create_log():

    try:

        with open(LOG_FILE, "r"):
            pass

    except OSError:

        with open(LOG_FILE, "w") as f:
            f.write("DATE,TIME,EVENT\n")


# ============================================================
# LOG EVENT
# ============================================================

def log_event(event):

    year, month, day, hour, minute, second = get_datetime()

    line = "{:04d}-{:02d}-{:02d},{:02d}:{:02d}:{:02d},{}\n".format(
        year,
        month,
        day,
        hour,
        minute,
        second,
        event
    )

    with open(LOG_FILE, "a") as f:
        f.write(line)

    print("LOG:", line, end="")


# ============================================================
# SENSOR
# ============================================================

def read_sensor():

    total = 0

    for _ in range(10):

        total += adc.read()
        time.sleep_ms(5)

    return total // 10


# ============================================================
# BUZZER ALERT
# ============================================================

def buzzer_alert():

    print()
    print("==============================")
    print("!!! ALIGNER ALERT !!!")
    print("ALIGNER IN BOX > 1 HOUR")
    print("==============================")

    for _ in range(3):

        buzzer.value(1)
        time.sleep_ms(500)

        buzzer.value(0)
        time.sleep_ms(500)


# ============================================================
# START
# ============================================================

create_log()

print()
print("==============================")
print("       ALIGNER BOX")
print("==============================")


# ============================================================
# INITIAL SENSOR STATE
# ============================================================

sensor = read_sensor()

if sensor < THRESHOLD:

    state = "IN_BOX"

else:

    state = "OUT_OF_BOX"


print("Initial ADC   :", sensor)
print("Initial state :", state)


# ============================================================
# INITIAL TIMER
# ============================================================

if state == "IN_BOX":

    in_box_start = datetime_to_seconds(get_datetime())

    print("Timer started.")
    print("Start time:", get_datetime())


# ============================================================
# MAIN LOOP
# ============================================================

while True:

    # --------------------------------------------------------
    # LED
    # --------------------------------------------------------

    led.value(not led.value())


    # --------------------------------------------------------
    # SENSOR
    # --------------------------------------------------------

    sensor = read_sensor()

    print(
        "ADC:",
        sensor,
        "STATE:",
        state
    )


    # ========================================================
    # OUT -> IN
    # ========================================================

    if state == "OUT_OF_BOX":

        if sensor < THRESHOLD:

            count = 0

            for _ in range(3):

                if read_sensor() < THRESHOLD:
                    count += 1

                time.sleep_ms(100)


            if count == 3:

                state = "IN_BOX"

                # Start timer using DS3231
                in_box_start = datetime_to_seconds(
                    get_datetime()
                )

                alert_triggered = False

                log_event("ALIGNER_IN_BOX")

                print("Timer started.")
                print("Start time:", get_datetime())


    # ========================================================
    # IN -> OUT
    # ========================================================

    elif state == "IN_BOX":

        if sensor > THRESHOLD:

            count = 0

            for _ in range(3):

                if read_sensor() > THRESHOLD:
                    count += 1

                time.sleep_ms(100)


            if count == 3:

                state = "OUT_OF_BOX"

                in_box_start = None
                alert_triggered = False

                buzzer.value(0)

                log_event("ALIGNER_REMOVED")

                print("Timer stopped.")


    # ========================================================
    # BOX TIME
    # ========================================================

    if state == "IN_BOX" and in_box_start is not None:

        now = datetime_to_seconds(get_datetime())

        elapsed = now - in_box_start

        print(
            "TIME IN BOX:",
            elapsed,
            "/",
            ONE_HOUR,
            "seconds"
        )


        # ----------------------------------------------------
        # ALERT
        # ----------------------------------------------------

        if elapsed >= ONE_HOUR:
        
            buzzer_alert()
        
            in_box_start = now
        
            print("1 HOUR ALERT!")
            print("Timer reset.")
            


    # ========================================================
    # LOOP DELAY
    # ========================================================

    time.sleep_ms(500)