import ctypes as ct
import sys
import os


def load_photon_spectr():
    """Lädt PhotonSpectr.dll (32-bit) aus dem Verzeichnis dieses Skripts."""
    # Sicherstellen, dass 32-bit Python läuft (Pointergröße 4 Byte)
    if ct.sizeof(ct.c_void_p) != 4:
        raise RuntimeError("PhotonSpectr.dll ist 32-bit. Bitte einen 32-bit Python-Interpreter verwenden.")

    dll_name = "PhotonSpectr.dll"
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dll_path = os.path.join(base_dir, dll_name)

    # Falls die DLL woanders liegt, hier den Pfad anpassen
    return ct.WinDLL(dll_path)


# DLL laden
spm = load_photon_spectr()

# kurze Aliase
c_int = ct.c_int
c_float = ct.c_float
c_ushort = ct.c_ushort
c_char_p = ct.c_char_p
POINTER = ct.POINTER


# --- Funktionsprototypen (entsprechend deinem C++-Beispiel) ---

spm.PHO_EnumerateDevices.argtypes = []
spm.PHO_EnumerateDevices.restype = c_int

spm.PHO_Open.argtypes = [c_int]
spm.PHO_Open.restype = c_int

spm.PHO_Close.argtypes = [c_int]
spm.PHO_Close.restype = c_int

spm.PHO_GetVer.argtypes = [c_int, c_char_p, c_int]
spm.PHO_GetVer.restype = c_int

spm.PHO_GetMl.argtypes = [c_int, c_char_p, c_int]
spm.PHO_GetMl.restype = c_int

spm.PHO_GetFw.argtypes = [c_int, c_char_p, c_int]
spm.PHO_GetFw.restype = c_int

spm.PHO_GetSn.argtypes = [c_int, c_char_p, c_int]
spm.PHO_GetSn.restype = c_int

spm.PHO_GetPn.argtypes = [c_int, ct.POINTER(c_int)]
spm.PHO_GetPn.restype = c_int

spm.PHO_GetStartEnd.argtypes = [c_int, ct.POINTER(c_int), ct.POINTER(c_int)]
spm.PHO_GetStartEnd.restype = c_int

spm.PHO_GetLut.argtypes = [c_int, ct.POINTER(c_float), c_int]
spm.PHO_GetLut.restype = c_int

spm.PHO_GetDeviceID.argtypes = [c_int, c_char_p, c_int]
spm.PHO_GetDeviceID.restype = c_int

spm.PHO_SetDeviceID.argtypes = [c_int, c_char_p, c_int]
spm.PHO_SetDeviceID.restype = c_int

spm.PHO_SetTime.argtypes = [c_int, c_float]
spm.PHO_SetTime.restype = c_int

spm.PHO_GetTime.argtypes = [c_int, ct.POINTER(c_float)]
spm.PHO_GetTime.restype = c_int

spm.PHO_SetAverage.argtypes = [c_int, c_int]
spm.PHO_SetAverage.restype = c_int

spm.PHO_GetAverage.argtypes = [c_int, ct.POINTER(c_int)]
spm.PHO_GetAverage.restype = c_int

spm.PHO_SetDs.argtypes = [c_int, c_int]
spm.PHO_SetDs.restype = c_int

spm.PHO_GetDs.argtypes = [c_int, ct.POINTER(c_int)]
spm.PHO_GetDs.restype = c_int

spm.PHO_GetCt.argtypes = [c_int, ct.POINTER(c_int)]
spm.PHO_GetCt.restype = c_int

spm.PHO_GetDark.argtypes = [c_int, ct.POINTER(c_int)]
spm.PHO_GetDark.restype = c_int

spm.PHO_GetTemperature.argtypes = [c_int, ct.POINTER(c_float)]
spm.PHO_GetTemperature.restype = c_int

spm.PHO_SetMode.argtypes = [c_int, c_int, c_int]
spm.PHO_SetMode.restype = c_int

spm.PHO_GetMode.argtypes = [c_int, ct.POINTER(c_int)]
spm.PHO_GetMode.restype = c_int

spm.PHO_Acquire.argtypes = [c_int, c_int, c_int, ct.POINTER(c_ushort)]
spm.PHO_Acquire.restype = c_int

spm.PHO_StreamOpen.argtypes = [c_int, c_int, c_int, c_int]
spm.PHO_StreamOpen.restype = c_int

spm.PHO_StreamClose.argtypes = [c_int]
spm.PHO_StreamClose.restype = c_int

spm.PHO_StreamStart.argtypes = [c_int]
spm.PHO_StreamStart.restype = c_int

spm.PHO_StreamStop.argtypes = [c_int]
spm.PHO_StreamStop.restype = c_int

spm.PHO_StreamAcquire.argtypes = [c_int, ct.POINTER(ct.POINTER(c_ushort)), ct.POINTER(c_int)]
spm.PHO_StreamAcquire.restype = c_int

spm.PHO_StreamRelease.argtypes = [c_int, ct.POINTER(c_ushort)]
spm.PHO_StreamRelease.restype = c_int

spm.PHO_GetAnalog.argtypes = [c_int, c_int, ct.POINTER(c_int)]
spm.PHO_GetAnalog.restype = c_int


def main():
    print("Enumerating devices......")
    num_devices = spm.PHO_EnumerateDevices()
    if num_devices == 0:
        print("No spectrometers found!")
        return

    print(f"The number of spectrometers connected is {num_devices}")

    if num_devices > 1:
        dev_index = int(input(f"Select a spectrometer number from 0 to {num_devices - 1}: "))
    else:
        dev_index = 0

    if dev_index < 0 or dev_index >= num_devices:
        print("The selected spectrometer number is not available!")
        return

    print(f"Opening connection to spectrometer number {dev_index}")
    if spm.PHO_Open(dev_index) == 0:
        print("Error opening device")

    # DLL version
    dll_version = ct.create_string_buffer(64)
    if spm.PHO_GetVer(dev_index, dll_version, len(dll_version)) == 0:
        print("Error on GetVer")
    else:
        dll_version_str = dll_version.value.decode(errors="ignore")
        print("The DLL version is", dll_version_str)

    # Model
    model = ct.create_string_buffer(14)
    if spm.PHO_GetMl(dev_index, model, 13) == 0:
        print("Error on GetMl")
    else:
        model_str = model.value.decode(errors="ignore")
        print("The spectrometer model is", model_str)

    # Firmware version
    fw_version = ct.create_string_buffer(10)
    if spm.PHO_GetFw(dev_index, fw_version, 9) == 0:
        print("Error on GetFw")
    else:
        fw_version_str = fw_version.value.decode(errors="ignore")
        print("The firmware version is", fw_version_str)

    # Serial number
    serial = ct.create_string_buffer(9)
    if spm.PHO_GetSn(dev_index, serial, 9) == 0:
        print("Error on GetSn")
    else:
        serial_str = serial.value.decode(errors="ignore")
        print("The serial number is", serial_str)

    # Number of CCD pixels
    num_pixels = c_int()
    if spm.PHO_GetPn(dev_index, ct.byref(num_pixels)) == 0:
        print("Error on GetPn")
    print("The number of CCD pixels is", num_pixels.value)

    # Start and end pixel
    start_pixel = c_int()
    end_pixel = c_int()
    if spm.PHO_GetStartEnd(dev_index, ct.byref(end_pixel), ct.byref(start_pixel)) == 0:
        print("Error on GetStartEnd")
    print("Start pixel number is", start_pixel.value)
    print("End pixel number is", end_pixel.value)

    # LUT coefficients
    lut = (c_float * 4)()
    if spm.PHO_GetLut(dev_index, lut, 4) == 0:
        print("Error on GetLUT")
    print("LUT coefficient 0 is", lut[0])
    print("LUT coefficient 1 is", lut[1])
    print("LUT coefficient 2 is", lut[2])
    print("LUT coefficient 3 is", lut[3])

    # Wavelengths per pixel
    npix = num_pixels.value
    wavelength = [0.0] * npix
    for i in range(npix):
        wavelength[i] = lut[0] + lut[1] * i + lut[2] * i * i + lut[3] * i * i * i

    if start_pixel.value < npix:
        print(
            f"The wavelength at pixel number {start_pixel.value}, for example, "
            f"is {wavelength[start_pixel.value]} nm"
        )

    # Device ID
    device_id1 = ct.create_string_buffer(64)
    if spm.PHO_GetDeviceID(dev_index, device_id1, len(device_id1)) == 0:
        print("Error on GetDeviceID. Device ID may not be available on this spectrometer.")
    else:
        device_id1_str = device_id1.value.decode(errors="ignore")
        print(f'The device ID is "{device_id1_str}"')
        new_device_id_answer = input("Change the device ID? (Y/N) ").strip()
        if new_device_id_answer.lower() == "y":
            device_id2_str = input("Select a new device ID: ")
            device_id2_str = device_id2_str[:63]  # Platz für Nullterminator
            device_id2_buf = ct.create_string_buffer(64)
            device_id2_buf.value = device_id2_str.encode()

            if spm.PHO_SetDeviceID(dev_index, device_id2_buf, len(device_id2_buf)) == 0:
                print("Error on SetDeviceID")

            device_id3 = ct.create_string_buffer(64)
            if spm.PHO_GetDeviceID(dev_index, device_id3, len(device_id3)) == 0:
                print("Error on GetDeviceID")
            else:
                device_id3_str = device_id3.value.decode(errors="ignore")
                print(f'The device ID has been changed to "{device_id3_str}"')

    # Exposure time
    exposure_time = float(input("Select the new exposure time in milliseconds: "))
    if spm.PHO_SetTime(dev_index, exposure_time) == 0:
        print("Error on SetTime")

    exposure_time_var = c_float()
    if spm.PHO_GetTime(dev_index, ct.byref(exposure_time_var)) == 0:
        print("Error on GetTime")
    print("The exposure time is", exposure_time_var.value, "ms")

    # Averaging number
    averaging_number_value = int(input("Select the number of times to average (1 to 16): "))
    if spm.PHO_SetAverage(dev_index, averaging_number_value) == 0:
        print("Error on SetAverage")

    averaging_number = c_int()
    if spm.PHO_GetAverage(dev_index, ct.byref(averaging_number)) == 0:
        print("Error on GetAverage")
    print("The averaging number is", averaging_number.value)

    # Dark subtraction
    dark_subtraction_status_value = int(input("Select the new dark subtraction mode (0: off, 1: on): "))
    if spm.PHO_SetDs(dev_index, dark_subtraction_status_value) == 0:
        print("Error on SetDs")

    dark_subtraction_status = c_int()
    if spm.PHO_GetDs(dev_index, ct.byref(dark_subtraction_status)) == 0:
        print("Error on GetDs")
    print("The dark subtraction status is", dark_subtraction_status.value)

    # Connection type
    connection_type = c_int()
    if spm.PHO_GetCt(dev_index, ct.byref(connection_type)) == 0:
        print("Error on GetCt")
    print("The connection type is", connection_type.value)

    # Dark level
    dark_level = c_int()
    if spm.PHO_GetDark(dev_index, ct.byref(dark_level)) == 0:
        print("Error on GetDark")
    print("The dark level is", dark_level.value)

    # Temperature
    temperature = c_float()
    if spm.PHO_GetTemperature(dev_index, ct.byref(temperature)) == 0:
        print("Error on GetTemperature")
    print("The temperature is", temperature.value)

    # Acquisition mode
    print("Mode 0: Continuous mode")
    print("Mode 1: Variable-delay hardware triggering mode")
    print("Mode 2: Scan-delay hardware triggering mode")
    print("Mode 3: Microsecond-delay hardware triggering mode")
    print("Mode 4: Streaming continuous mode")
    print("Mode 5: Streaming hardware triggering mode")
    print("Mode 6: Streaming exposure start/stop hardware triggering mode")
    print("Note: triggering modes require external triggering circuitry")
    mode_value = int(input("Select the acquisition mode: "))

    # Spectrum buffer
    spectrum = (c_ushort * npix)()

    if 0 <= mode_value <= 3:
        scan_delay = 0
        if mode_value == 2:
            scan_delay = int(input("Enter a scan delay from 0 to 15: "))
        elif mode_value == 3:
            scan_delay = int(input("Enter a scan delay in microseconds: "))

        if spm.PHO_SetMode(dev_index, mode_value, scan_delay) == 0:
            print("Error on SetMode")

        mode = c_int()
        if spm.PHO_GetMode(dev_index, ct.byref(mode)) == 0:
            print("Error on GetMode")
        print("The acquisition mode is", mode.value)

        print("Acquiring CCD data...")
        if spm.PHO_Acquire(dev_index, 0, npix, spectrum) == 0:
            print("Error on Acquire")

    elif 4 <= mode_value <= 6:
        # Streaming modes
        returned_spectrum_length = c_int()
        p_spectrum = ct.POINTER(c_ushort)()

        if spm.PHO_StreamOpen(dev_index, 128, npix, mode_value - 4) == 0:
            print("Error on StreamOpen")

        mode = c_int()
        if spm.PHO_GetMode(dev_index, ct.byref(mode)) == 0:
            print("Error on GetMode")
        print("The acquisition mode is", mode.value)

        print("Acquiring CCD data 1000 times...")
        if spm.PHO_StreamStart(dev_index) == 0:
            print("Error on StreamStart")

        for _ in range(1000):
            if spm.PHO_StreamAcquire(dev_index, ct.byref(p_spectrum), ct.byref(returned_spectrum_length)) == 0:
                print("Error on StreamAcquire")

            if bool(p_spectrum):
                # Daten in den 'spectrum'-Buffer kopieren
                ct.memmove(
                    spectrum,
                    p_spectrum,
                    npix * ct.sizeof(c_ushort),
                )
                if spm.PHO_StreamRelease(dev_index, p_spectrum) == 0:
                    print("Error on StreamRelease")

        if spm.PHO_StreamStop(dev_index) == 0:
            print("Error on StreamStop")
        if spm.PHO_StreamClose(dev_index) == 0:
            print("Error on StreamClose")

    if npix > 200:
        print(
            f"The amplitude at pixel number 200 ({wavelength[200]} nm), "
            f"for example, is {spectrum[200]} counts"
        )

    # Analog ports
    analog_reading = c_int()
    for port in range(4):
        if spm.PHO_GetAnalog(dev_index, port, ct.byref(analog_reading)) == 0:
            print(f"Error on GetAnalog at port {port}")
        print(f"The analog input amplitude at port {port} is {analog_reading.value}")

    # Close connection
    print("Closing connection...")
    if spm.PHO_Close(dev_index) == 0:
        print("Error on Close")

    input("Done... Press Enter to exit.")


if __name__ == "__main__":
    main()
