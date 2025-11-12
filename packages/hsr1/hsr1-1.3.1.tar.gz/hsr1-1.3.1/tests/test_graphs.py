import os

import hsr1

class TestGraphs:

    def test_should_plot_integral_summary_graph(self):
        data_filepath = "tests/res/databases/Ispra 10s"
        deployment_metadata_filepath = "tests/res/databases/Ispra 10s/HSR1-005 ISRC 2024 Deployment.ini"
        database_location = "tests/temp/databases/ispra_database.db"
        # database_location = "/home/albie/PeakDesign/Albie datasets/Quest 2025/databases/HSR1-004 PML Quest 2025.db"
        # deployment_metadata_filepath = "~/PeakDesign/Albie datasets/Quest 2025/HSR1-004 2025 Deployment.ini"
        # database_location = "tests/temp/databases/quest_database.db"

        if os.path.exists(database_location):
            os.remove(database_location)

        data = hsr1.read_txt.read(data_filepath, deployment_metadata_filepath=
                                  deployment_metadata_filepath)
        driver = hsr1.DBDriver(db_name=database_location)
        driver.store(data)
        
        g = hsr1.Graph(driver, block=True)

        g.plot_integral(flag=True)
        g.plot_gps()
        g.plot_accessory()
        
