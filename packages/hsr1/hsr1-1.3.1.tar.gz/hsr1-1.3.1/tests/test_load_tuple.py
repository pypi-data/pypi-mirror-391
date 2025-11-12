import os

import pandas as pd

import hsr1

class TestLoadTuple:
    def test_should_return_tuple_of_dataframes(self):
        
        data_filepath = "tests/res/NOAA 2025"
        deployment_metadata_filepath = "tests/res/NOAA 2025/HSR1-009 NOAA 2025 Deployment.ini"

        database_location = "tests/temp/databases/my_database.db"

        db_driver = hsr1.DBDriver(database_location)

        data = hsr1.read_txt.read(data_filepath, deployment_metadata_filepath=
                                  deployment_metadata_filepath)
        db_driver.store(data)

        loaded_data = db_driver.load_tuple()
        assert(type(loaded_data) == tuple)

        assert(type(loaded_data[0]) == pd.DataFrame)

        os.remove(database_location)

    def test_should_return_same_data_as_input(self):
        data_filepath = "tests/res/NOAA 2025"
        deployment_metadata_filepath = "tests/res/NOAA 2025/HSR1-009 NOAA 2025 Deployment.ini"

        database_location = "tests/temp/databases/my_database.db"

        if os.path.exists(database_location):
            os.remove(database_location)
        db_driver = hsr1.DBDriver(database_location)

        data = hsr1.read_txt.read(data_filepath, deployment_metadata_filepath=
                                  deployment_metadata_filepath)
        db_driver.store(data)

        loaded_data = db_driver.load_tuple()

        loaded_data[2]["dataseries_id"] = "''"
        loaded_data[2]["deployment_id"] = ""

        assert(data[0].equals(loaded_data[0]))
        assert(data[1].equals(loaded_data[1]))
        assert(data[2].equals(loaded_data[2]))
        assert(data[3].columns.equals(loaded_data[3].columns))
        assert(data[3].index.equals(loaded_data[3].index))
        assert(data[3].dtypes.equals(loaded_data[3].dtypes))
        assert(data[3].equals(loaded_data[3]))
        os.remove(database_location)


    def test_should_return_same_once_loaded_stored_and_loaded(self):
        data_filepath = "tests/res/NOAA 2025"
        deployment_metadata_filepath = "tests/res/NOAA 2025/HSR1-009 NOAA 2025 Deployment.ini"

        database_location_a = "tests/temp/databases/my_database_a.db"
        database_location_b = "tests/temp/databases/my_database_b.db"
        
        if os.path.exists(database_location_a):
            os.remove(database_location_a)
        if os.path.exists(database_location_b):
            os.remove(database_location_b)

        db_driver_a = hsr1.DBDriver(database_location_a)
        db_driver_b = hsr1.DBDriver(database_location_b)

        data = hsr1.read_txt.read(data_filepath, deployment_metadata_filepath=
                                  deployment_metadata_filepath)
        db_driver_a.store(data)

        interim_data = db_driver_a.load_tuple()

        db_driver_b.store(interim_data)
        loaded_data = db_driver_b.load_tuple()

        # dataseries ids are created when the database is stored, so they will be different both times.
        # this is expected behaviour, so ignore it to test the rest.
        loaded_data[0]["dataseries_id"] = "''"
        data[0]["dataseries_id"] = "''"

        loaded_data[1]["dataseries_id"] = "''"
        data[1]["dataseries_id"] = "''"

        loaded_data[3]["dataseries_id"] = "''"
        data[3]["dataseries_id"] = "''"

        loaded_data[2]["dataseries_id"] = "''"
        loaded_data[2]["deployment_id"] = ""

        assert(data[0].columns.equals(loaded_data[0].columns))
        assert(data[0].index.equals(loaded_data[0].index))
        assert(data[0].dtypes.equals(loaded_data[0].dtypes))
        for col in data[0].columns:
            print(col, data[0][col].equals(loaded_data[0][col]))
        print(data[0]["dataseries_id"])
        print(loaded_data[0]["dataseries_id"])
        assert(data[0].equals(loaded_data[0]))
        assert(data[1].equals(loaded_data[1]))
        assert(data[2].equals(loaded_data[2]))
        assert(data[3].columns.equals(loaded_data[3].columns))
        assert(data[3].index.equals(loaded_data[3].index))
        assert(data[3].dtypes.equals(loaded_data[3].dtypes))
        assert(data[3].equals(loaded_data[3]))
        os.remove(database_location_a)
        os.remove(database_location_b)



    def test_non_accessory_data(self):
        data_filepath = "tests/res/SGP 2022"
        # data_filepath = "/home/albie/PeakDesign/Albie datasets/SGP 2022/"
        deployment_metadata_filepath = "tests/res/SGP 2022/SGP 2022 Deployment.ini"

        database_location_a = "tests/temp/databases/my_database_a.db"
        database_location_b = "tests/temp/databases/my_database_b.db"
        
        if os.path.exists(database_location_a):
            os.remove(database_location_a)
        if os.path.exists(database_location_b):
            os.remove(database_location_b)

        db_driver_a = hsr1.DBDriver(database_location_a)
        db_driver_b = hsr1.DBDriver(database_location_b)

        data = hsr1.read_txt.read(data_filepath, deployment_metadata_filepath=
                                  deployment_metadata_filepath)
        db_driver_a.store(data)

        interim_data = db_driver_a.load_tuple()

        db_driver_b.store(interim_data)
        loaded_data = db_driver_b.load_tuple()

        # dataseries ids are created when the database is stored, so they will be different both times.
        # this is expected behaviour, so ignore it to test the rest.
        loaded_data[0]["dataseries_id"] = "''"
        data[0]["dataseries_id"] = "''"

        loaded_data[1]["dataseries_id"] = "''"
        data[1]["dataseries_id"] = "''"

        loaded_data[2]["dataseries_id"] = "''"
        loaded_data[2]["deployment_id"] = ""

        assert(data[2].columns.equals(loaded_data[2].columns))
        assert(data[2].index.equals(loaded_data[2].index))
        # assert(data[2].dtypes.equals(loaded_data[2].dtypes))
        for col in data[2].columns:
            print(col, data[2][col].equals(loaded_data[2][col]))
        assert(data[0].equals(loaded_data[0]))
        assert(data[1].equals(loaded_data[1]))
        assert(data[2].equals(loaded_data[2]))
        os.remove(database_location_a)
        os.remove(database_location_b)



    def test_raw(self):
        data_filepath = "tests/res/SGP 2022 1d"
        deployment_metadata_filepath = "tests/res/SGP 2022 1d/SGP 2022 Deployment.ini"

        database_location_a = "tests/temp/databases/my_database_a.db"
        database_location_b = "tests/temp/databases/my_database_b.db"
        
        if os.path.exists(database_location_a):
            os.remove(database_location_a)
        if os.path.exists(database_location_b):
            os.remove(database_location_b)

        db_driver_a = hsr1.DBDriver(database_location_a)
        db_driver_b = hsr1.DBDriver(database_location_b)

        data = hsr1.read_txt.read_raw_txt(data_filepath, deployment_metadata_filepath=
                                  deployment_metadata_filepath)
        db_driver_a.store_raw(data)

        loaded_data = db_driver_a.load_raw_tuple()
        # interim_data = db_driver_a.load_raw_tuple()
        #
        # db_driver_b.store_raw(interim_data)
        # loaded_data = db_driver_b.load_raw_tuple()

        # dataseries ids are created when the database is stored, so they will be different both times.
        # this is expected behaviour, so ignore it to test the rest.
        # loaded_data[0]["dataseries_id"] = "''"
        # data[0]["dataseries_id"] = "''"
        #
        # loaded_data[1]["dataseries_id"] = "''"
        # data[1]["dataseries_id"] = "''"
        #
        loaded_data[1]["dataseries_id"] = "''"
        loaded_data[1]["deployment_id"] = ""

        assert(data[1].columns.equals(loaded_data[1].columns))
        assert(data[1].index.equals(loaded_data[1].index))
        assert(data[1].dtypes.equals(loaded_data[1].dtypes))
        for col in data[1].columns:
            print(col, data[1][col].equals(loaded_data[1][col]))
        assert(data[0][0].equals(loaded_data[0][0]))
        assert(data[1].equals(loaded_data[1]))
        os.remove(database_location_a)
        # os.remove(database_location_b)
