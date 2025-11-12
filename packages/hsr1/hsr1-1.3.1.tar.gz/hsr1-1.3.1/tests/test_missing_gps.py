import hsr1

import os


class TestMissingGps:
    def test_should_plot_as_much_as_possible(self):
        data_filepath = "tests/res/no_gps_noaa"
        # data_filepath = "tests/res/NOAA 2025"
        deployment_metadata_filepath = "tests/res/NOAA 2025/HSR1-009 NOAA 2025 Deployment.ini"

        database_location = "tests/temp/databases/databases/my_database_no_gps.db"

        if os.path.exists(database_location):
            os.remove(database_location)

        db_driver = hsr1.DBDriver(database_location)

        txt_data = hsr1.read_txt.read(data_filepath, deployment_metadata_filepath=
                                  deployment_metadata_filepath)

        db_driver.store(txt_data)
        
        g = hsr1.Graph(db_driver)
        g.plot_integral()
        g.plot_aod_day()
        g.plot_gps()
        g.plot_accessory()

        os.remove(database_location)
