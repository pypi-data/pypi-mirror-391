import os

import hsr1


class TestIndChLoading:
    def test_should_read_ind_ch_correctly(self):
        
        data_filepath = "tests/res/NOAA 2025"
        deployment_metadata_filepath = "tests/res/NOAA 2025/HSR1-009 NOAA 2025 Deployment.ini"
        database_location = "tests/temp/databases/my_database.db"

        if os.path.exists(database_location):
            os.remove(database_location)

        data = hsr1.read_txt.read(data_filepath, deployment_metadata_filepath=
                                  deployment_metadata_filepath)
        

        driver = hsr1.DBDriver(db_name=database_location)
        driver.store(data)

        ind_ch_data = driver.load(["ch1"])
        assert("ch1" in ind_ch_data.columns)


    def test_should_be_able_to_load_hdr_correctly(self):
        
        data_filepath = "tests/res/NOAA 2025"
        deployment_metadata_filepath = "tests/res/NOAA 2025/HSR1-009 NOAA 2025 Deployment.ini"
        database_location = "tests/temp/databases/my_database.db"

        if os.path.exists(database_location):
            os.remove(database_location)

        data = hsr1.read_txt.read(data_filepath, deployment_metadata_filepath=
                                  deployment_metadata_filepath)


        driver = hsr1.DBDriver(db_name=database_location)
        driver.store(data)
        
        hdr_data = driver.load(table="hdr")
        assert("offset_1" in hdr_data.columns)


    def test_should_be_able_to_add_ind_ch_and_hdr_to_existing_database(self):
        data_filepath = "tests/res/NOAA 2025"
        deployment_metadata_filepath = "tests/res/NOAA 2025/HSR1-009 NOAA 2025 Deployment.ini"
        database_location = "tests/temp/databases/my_database.db"

        if os.path.exists(database_location):
            os.remove(database_location)

        data = hsr1.read_txt.read(data_filepath, deployment_metadata_filepath=
                                  deployment_metadata_filepath, end_date="2025-03-20")
        data = tuple(list(data[:3]) + [data[-1]])
        for datafile in data:
            print(datafile.columns)


        database_location = "tests/temp/databases/my_database.db"

        driver = hsr1.DBDriver(db_name=database_location)
        driver.store(data)
        
        hdr_data = hsr1.read_txt.read(data_filepath, deployment_metadata_filepath=deployment_metadata_filepath, start_date="2025-03-21", end_date="2025-03-21")
        driver.store(hdr_data)

        non_hdr_data = hsr1.read_txt.read(data_filepath, deployment_metadata_filepath=deployment_metadata_filepath, start_date="2025-03-22")
        non_hdr_data = tuple(list(non_hdr_data[:3]) + [non_hdr_data[-1]])
        driver.store(non_hdr_data)


    def test_should_load_new_tables_correctly(self):
        data_filepath = "tests/res/NOAA 2025"
        deployment_metadata_filepath = "tests/res/NOAA 2025/HSR1-009 NOAA 2025 Deployment.ini"
        database_location = "tests/temp/databases/my_database.db"

        if os.path.exists(database_location):
            os.remove(database_location)

        data = hsr1.read_txt.read(data_filepath, deployment_metadata_filepath=
                                  deployment_metadata_filepath)
        driver = hsr1.DBDriver(db_name=database_location)
        driver.store(data)


        loaded_data = driver.load([], table="ind_ch")
        assert("ch0" in loaded_data.columns)

        loaded_data = driver.load(["ch0", "offset_1"])
        assert("ch0" in loaded_data.columns and "offset_1" in loaded_data.columns)

        loaded_data = driver.load_hdr()
        assert("offset_1" in loaded_data.columns)

