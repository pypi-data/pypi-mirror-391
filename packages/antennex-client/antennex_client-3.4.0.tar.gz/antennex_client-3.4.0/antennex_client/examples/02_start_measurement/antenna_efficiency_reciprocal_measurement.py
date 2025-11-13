from antennex_client import *

#
# Perform Antenna Efficiency measurement with The Wireless Connector.
#
# The measurement setup requires:
# - Antenna Efficiency application license is present on The Wireless Connector
# - VNA
# - Antenna (reciprocal) is connected to VNA on port 1
# - VNA is calibrated to the desired reference plane of the antenna
#
# This example will acquire the efficiency and provide a plot and metrics.
#

if __name__ == "__main__":

    antenna_frequency_start = 60e9
    antenna_frequency_end = 64e9

    # Create an instance of the API class
    hostname = hostname_from_file("hostname.txt")
    ReverbClient = create_client("http://" + hostname + ":8080")

    if not ReverbClient.is_version_greater_than("3.4"):
        print("This example requires The Wireless Connector software version 3.4 or higher.")
        exit()

    #Running this example required a license for the Antenna Efficiency application to be installed on the chamber.
    licenses_installed = ReverbClient.get_license_info()
    assert "AntennaEfficiency" in licenses_installed.licenses, "Antenna Efficiency application is not licensed."

    #Set the system to Antenna Efficiency mode
    ReverbClient.set_machine_mode(AcquisitionMode.ANTENNAEFFICIENCY)

    # Start an acquisition between 60 and 64 GHz.
    ReverbClient.restore_settings_to_defaults("measurement")
    settings = Settings()
    settings.frequency_start = antenna_frequency_start
    settings.frequency_end = antenna_frequency_end
    settings.stirrer_steps0 = 2
    settings.stirrer_steps1 = 2
    settings.antenna_efficiency = AntennaEfficiencySettings()
    settings.antenna_efficiency.dut_type = DutType.RECIPROCAL
    settings.antenna_efficiency.dut_port = VnaPort(portNumber=1)

    ReverbClient.set_settings("measurement", settings)

    # The acquire function with the optional argument Wait set to true is
    # blocking and the script will continue after the acquisition is finished.
    # Wait is set to True by default.
    print("Measurement is starting...")
    ReverbClient.acquire(
        acquisition_type=AcquisitionTypes.ANTENNAEFFICIENCY, wait=True)
    print("Measurement is finished.")

    # Get the data from the chamber
    totalEfficiency = ReverbClient.get_data(DataTypes.TOTALEFFICIENCY)
    radiationEfficiency = ReverbClient.get_data(DataTypes.RADIATIONEFFICIENCY)
    mismatchEfficiency = ReverbClient.get_data(DataTypes.MISMATCHEFFICIENCY)

    # Plot the data using the supplied plot_result function
    plot_result(totalEfficiency)
    plot_result(radiationEfficiency)
    plot_result(mismatchEfficiency)

    # Display metrics about the measurement
    #print(totalEfficiency.metrics)
    print("Total efficiency     = " + "{:4.1f}".format(totalEfficiency.metrics.peak_efficiency) + " " + totalEfficiency.unit)
    print("Radiation efficiency = " + "{:4.1f}".format(radiationEfficiency.metrics.peak_efficiency) + " " + radiationEfficiency.unit)
    print("Mismatch efficiency  = " + "{:4.1f}".format(mismatchEfficiency.metrics.peak_efficiency) + " " + mismatchEfficiency.unit)

    # sava data as json, as retrieved from instrument
    save_as_json(totalEfficiency, "TotalEfficiency.json")
    save_as_json(radiationEfficiency, "RadiationEfficiency.json")
    save_as_json(mismatchEfficiency, "MismatchEfficiency.json")

    # sava data as csv
    save_as_csv(totalEfficiency, "TotalEfficiency.csv")
    save_as_csv(radiationEfficiency, "RadiationEfficiency.csv")
    save_as_csv(mismatchEfficiency, "MismatchEfficiency.csv")