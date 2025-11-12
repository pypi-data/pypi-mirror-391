import os

import hsr1



class TestIndChGraph:
    def test_should_plot_graph(self):

        data_filepath = "tests/res/SGP 2022"
        deployment_metadata_filepath = "tests/res/NOAA 2025/HSR1-009 NOAA 2025 Deployment.ini"

        database_location = "tests/temp/databases/databases/my_raw_database.db"

        if os.path.exists(database_location):
            os.remove(database_location)

        data = hsr1.read_txt.read(data_filepath, deployment_metadata_filepath=
                                  deployment_metadata_filepath)
        driver = hsr1.DBDriver(db_name=database_location)
        driver.store(data)
        
        graph = hsr1.Graph(driver)

        graph.daily_integrals(rows=2, days_in_row=3, period=6)
        graph.daily_ind_ch()
        graph.daily_ind_ch(rows=2, days_in_row=3, period=6)

    # def test_should_plot_hdr_graph(self):
    #
    #     data_filepath = "tests/res/SGP 2022"
    #     deployment_metadata_filepath = "tests/res/NOAA 2025/HSR1-009 NOAA 2025 Deployment.ini"
    #
    #     database_location = "tests/temp/databases/databases/my_raw_database.db"
    #
    #     if os.path.exists(database_location):
    #         os.remove(database_location)
    #
    #     data = hsr1.read_txt.read(data_filepath, deployment_metadata_filepath=
    #                               deployment_metadata_filepath)
    #     driver = hsr1.DBDriver(db_name=database_location)
    #     driver.store(data)
    #
    #     graph = hsr1.Graph(driver)
    #
    #     graph.daily_hdr()
    #
    #
