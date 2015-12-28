# weather_data

This file includes 3 main functions to allow the downloading and the treatment of the weather data available from three different sources. The sources are AEMET, METEOCAT, and WUnderGround (not yet).

A **config.cfg** file place in the same working directory is also needed. In this file the location of the different files and directories must be included in the following way:

```sh
{
  "aemet": {
    "path_res": "/home/user_name/.../AEMET/Results/",   # Where the final results will be saved
    "path_dat": "/home/user_name.../AEMET/",		        # Where the file that contains the weather stations to download is located
    "path_data": "/home/user_name/.../AEMET/Data/",     # Where the downloaded info will be placed
    "path_info": "/home/user_name/.../AEMET/Info/",     # Where the log file will placed
    "file_stations": "Estacions.dat"                    # The name of the file with the weather stations info (station_name,station_id)
  },
  "meteocat": {
    "path_res": "/home/user_name/.../Meteocat/Results/",
    "path_dat": "/home/user_name.../Meteocat/",
    "file_stations": "Estacions.dat"
  }
}
```

The **file with the list of weather stations** available from each site should include the following information:

- station_name,station_id



The **information is saved** in the following format (one file per weather station):

* [0]  ID_Estacio,
* [1]  Time_stamp [YYYYMMDDhhmmss],
* [2]  Velocitat_mitja [km/h],
* [3]  Direccio_velocitat_mitja [0º-360º],
* [4]  Velocitat_max [km/h],
* [5]  Direccio_velocitat_max [0º-360º],
* [6]  Temperatura [ºC],
* [7]  Humitat [0-100%],
* [8]  Radiacio [W/m²],
* [9]  Pressió [hPa],
* [10] Precipitació [mm]
* [11] Nubulositat [text]

