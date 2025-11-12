import os

import hsr1


class TestDailyGraphs:
    def test_all_graphs_should_plot_with_defaults(self):
        data_filepath = "tests/res/NOAA 2025"
        deployment_metadata_filepath = "tests/res/NOAA 2025/HSR1-009 NOAA 2025 Deployment.ini"

        database_location = "tests/temp/databases/my_database.db"

        db_driver = hsr1.DBDriver(database_location)

        if os.path.exists(database_location):
            os.remove(database_location)

        data = hsr1.read_txt.read(data_filepath, deployment_metadata_filepath=
                                  deployment_metadata_filepath)
        db_driver.store(data)
        
        g = hsr1.Graph(db_driver)

        g.daily_integrals()
        g.daily_temps()
        g.daily_hdr()
        g.daily_ind_ch()

    def test_all_graphs_should_plot_with_parameters_set(self):
        data_filepath = "tests/res/NOAA 2025"
        deployment_metadata_filepath = "tests/res/NOAA 2025/HSR1-009 NOAA 2025 Deployment.ini"

        database_location = "tests/temp/databases/my_database.db"

        db_driver = hsr1.DBDriver(database_location)

        if os.path.exists(database_location):
            os.remove(database_location)

        data = hsr1.read_txt.read(data_filepath, deployment_metadata_filepath=
                                  deployment_metadata_filepath)
        db_driver.store(data)
        
        g = hsr1.Graph(db_driver)

        g.daily_integrals(flag=True)
        g.daily_temps(flag=True, title_prefix="my title ")
        g.daily_hdr(flag=True, max_limit=2)
        g.daily_ind_ch(flag=True)

        
    def test_all_graphs_should_plot_layout_correctly(self):
        data_filepath = "tests/res/long_sgp_2022"
        deployment_metadata_filepath = "tests/res/long_sgp_2022/SGP 2022 Deployment.ini"

        database_location = "tests/temp/databases/long_sgp_database.db"

        db_driver = hsr1.DBDriver(database_location)

        if not os.path.exists(database_location):
            data = hsr1.read_txt.read(data_filepath, deployment_metadata_filepath=
                                      deployment_metadata_filepath)
            db_driver.store(data)
            
        g = hsr1.Graph(db_driver)

        g.daily_integrals(period="weekly", rows=1, days_in_row=4)
