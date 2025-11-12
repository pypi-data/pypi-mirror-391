from earth_rover_mini_plus_sdk import EarthRoverMini
import asyncio, time

async def main():
    rover = EarthRoverMini("192.168.11.1", 8888)
    await rover.connect()

    # --- 1) Connection + Ping Test ---
    print("\n[TEST] Pinging rover...")
    await rover.safe_ping()
    await asyncio.sleep(1)

    # --- 2) Move / Control Packet Test ---
    print("\n[TEST] Moving rover (speed=60, angular=360) for 3s...")

    # Start the movement task (async)
    move_task = asyncio.create_task(rover.move(3, 60, 360))

    # Take 5 telemetry samples spaced evenly across the movement duration
    x = 5
    vals = {}
    for i in range(x):
        telemetry = await rover.get_telemetry()  # snapshot (non-blocking)
        vals[time.time()] = telemetry

        if telemetry:
            print(f"[TELEMETRY {i+1}/5] RPM={telemetry.get('speed'):.1f}, Heading={telemetry.get('heading'):.1f}")
        else:
            print(f"[TELEMETRY {i+1}/5] No data received")

        await asyncio.sleep(3 / x)  # space samples across ~3 seconds

    # Wait for the move() to finish cleanly
    await move_task

    await asyncio.sleep(1)

    print(vals)

    # --- 3) IMU Calibration ---
    print("\n[TEST] Starting IMU calibration...")
    await rover.imu_calibrate(mode=1)
    await asyncio.sleep(2)

    # --- 4) IMU / MAG Read ---
    print("\n[TEST] Requesting IMU/MAG read...")
    imu_data = await rover.imu_mag_read()
    print(f"[RESULT] IMU/MAG Data: {imu_data}")
    await asyncio.sleep(1)

    # --- 5) IMU Write (Test Bias Values) ---
    print("\n[TEST] Writing IMU bias values...")
    acc_bias  = (100, 200, 300)
    gyro_bias = (10, 20, 30)
    mag_bias  = (1, 2, 3)
    await rover.imu_write(acc_bias, gyro_bias, mag_bias)
    await asyncio.sleep(1)

    # --- 6) MAG Write (Test Bias Values) ---
    print("\n[TEST] Writing MAG bias values...")
    await rover.mag_write((5, 6, 7))
    await asyncio.sleep(1)

    # --- 7) OTA Update Simulation ---
    print("\n[TEST] Requesting OTA update to version 42...")
    await rover.over_the_air_update(42)
    await asyncio.sleep(2)

    # --- Done ---
    print("\n[TEST] All commands sent. Disconnecting...")
    await rover.disconnect()


if __name__ == "__main__":
    asyncio.run(main())