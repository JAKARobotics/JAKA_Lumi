#!/usr/bin/env python3
"""Minimal Python controller to command DH Modbus gripper open/close.

Default port/baud/id match the C++ example (/dev/DH_hand, 115200, id=1).
You need the `pyserial` package installed (`pip install pyserial`).
Run: python3 python_open_gripper.py --state 0   # open
     python3 python_open_gripper.py --state 1   # close
"""

import argparse
import sys
import time

import serial


def calc_crc(data: bytes) -> int:
    """Modbus RTU CRC16 (poly 0xA001, low byte first)."""
    crc = 0xFFFF
    for ch in data:
        crc ^= ch
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc & 0xFFFF


def write_register(ser: serial.Serial, slave_id: int, address: int, value: int, retries: int = 3) -> bool:
    """Function 0x06: write a single holding register."""
    frame = bytearray(
        [
            slave_id,
            0x06,
            (address >> 8) & 0xFF,
            address & 0xFF,
            (value >> 8) & 0xFF,
            value & 0xFF,
        ]
    )
    crc = calc_crc(frame)
    frame.extend((crc & 0xFF, (crc >> 8) & 0xFF))

    for _ in range(retries):
        ser.reset_input_buffer()
        ser.write(frame)
        resp = ser.read(8)
        if resp == frame:
            return True
    return False


def read_register(ser: serial.Serial, slave_id: int, address: int, retries: int = 40) -> int:
    """Function 0x03: read one holding register; returns the register value."""
    frame = bytearray(
        [
            slave_id,
            0x03,
            (address >> 8) & 0xFF,
            address & 0xFF,
            0x00,
            0x01,
        ]
    )
    crc = calc_crc(frame)
    frame.extend((crc & 0xFF, (crc >> 8) & 0xFF))

    for _ in range(retries):
        ser.reset_input_buffer()
        ser.write(frame)
        resp = ser.read(7)
        if len(resp) != 7:
            continue
        if resp[0] != slave_id or resp[1] != 0x03 or resp[2] != 0x02:
            continue
        if calc_crc(resp[:-2]) != (resp[-2] | (resp[-1] << 8)):
            continue
        return (resp[3] << 8) | resp[4]
    raise RuntimeError(f"Failed to read register 0x{address:04X}")


def ensure_initialized(ser: serial.Serial, slave_id: int, timeout_s: float = 8.0) -> None:
    """Send initialization command if needed and wait until finished."""
    try:
        init_state = read_register(ser, slave_id, 0x0200, retries=3)
        if init_state == 1:
            return
    except Exception:
        pass

    print("Initializing gripper...")
    if not write_register(ser, slave_id, 0x0100, 0xA5):
        raise RuntimeError("Failed to send initialization command")

    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            init_state = read_register(ser, slave_id, 0x0200, retries=3)
            if init_state == 1:
                print("Initialization complete")
                return
        except Exception:
            pass
        time.sleep(0.1)
    raise RuntimeError("Initialization did not finish in time")


def move_gripper(ser: serial.Serial, slave_id: int, target_pos: int, timeout_s: float = 5.0) -> int:
    """Command the gripper to the target position and wait until it stops moving."""
    if not write_register(ser, slave_id, 0x0103, target_pos):
        raise RuntimeError("Failed to send target position")

    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            grip_state = read_register(ser, slave_id, 0x0201, retries=2)
            if grip_state != 0:  # not moving
                break
        except Exception:
            pass
        time.sleep(0.1)
    try:
        return read_register(ser, slave_id, 0x0202, retries=3)
    except Exception:
        return -1

def command_gripper(
    state: int,
    port: str = "/dev/DH_hand",
    baud: int = 115200,
    slave_id: int = 1,
    position: int | None = None,
) -> None:
    """
    state: 0=open, 1=close
    position: optional override; 0-1000 (0=closed, 1000=fully open)
    """
    default_open = 1000
    default_close = 0
    target = position if position is not None else (default_open if state == 0 else default_close)

    with serial.Serial(
        port=port,
        baudrate=baud,
        bytesize=8,
        parity=serial.PARITY_NONE,
        stopbits=1,
        timeout=0.2,
    ) as ser:
        ensure_initialized(ser, slave_id)
        final_pos = move_gripper(ser, slave_id, target)
        action = "opened" if state == 0 else "closed"
        print(f"Gripper {action} to target {target}, current position={final_pos}")

def main() -> int:
    parser = argparse.ArgumentParser(description="Control DH Modbus gripper: 0=open, 1=close.")
    parser.add_argument("--port", default="/dev/DH_hand", help="Serial port (default: /dev/DH_hand)")
    parser.add_argument("--baud", type=int, default=115200, help="Baud rate (default: 115200)")
    parser.add_argument("--id", type=int, default=1, help="Modbus slave ID (default: 1)")
    parser.add_argument("--state", type=int, choices=[0, 1], required=True, help="0=open, 1=close")
    parser.add_argument("--open-pos", type=int, default=1000, help="Position used for open (default: 1000)")
    parser.add_argument("--close-pos", type=int, default=0, help="Position used for close (default: 0)")
    args = parser.parse_args()

    target = args.open_pos if args.state == 0 else args.close_pos

    try:
        with serial.Serial(
            port=args.port,
            baudrate=args.baud,
            bytesize=8,
            parity=serial.PARITY_NONE,
            stopbits=1,
            timeout=0.2,
        ) as ser:
            print(f"Connected to {args.port} @ {args.baud}, id={args.id}")
            ensure_initialized(ser, args.id)
            final_pos = move_gripper(ser, args.id, target)
            action = "opened" if args.state == 0 else "closed"
            print(f"Gripper {action} to target {target}, current position={final_pos}")
    except Exception as exc:
        print(f"Error: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
