
import struct

OUTPUT_FILE = "patient.bin"

# Fixed field sizes
PATIENT_ID_SIZE = 20
PATIENT_NAME_SIZE = 50
PHONE_SIZE = 15

FORMAT = f"<{PATIENT_ID_SIZE}s{PATIENT_NAME_SIZE}s{PHONE_SIZE}s"


def make_fixed_string(text, size):
    data = text.encode("utf-8")

    if len(data) > size:
        raise ValueError(f"Value too long. Maximum {size} bytes.")

    return data.ljust(size, b"\x00")


patient_id = input("Patient ID: ")
patient_name = input("Patient Name: ")
phone_number = input("Phone Number: ")

patient_id = make_fixed_string(patient_id, PATIENT_ID_SIZE)
patient_name = make_fixed_string(patient_name, PATIENT_NAME_SIZE)
phone_number = make_fixed_string(phone_number, PHONE_SIZE)

data = struct.pack(
    FORMAT,
    patient_id,
    patient_name,
    phone_number
)

with open(OUTPUT_FILE, "wb") as file:
    file.write(data)

print()
print("Patient binary file created successfully!")
print("File:", OUTPUT_FILE)
print("Size:", len(data), "bytes")
