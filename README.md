# weather_data

This file includes 3 main functions to allow the downloading and the treatment of the weather data available in three different sources. The sources are AEMET, METEOCAT, and WUnderGround (not yet).

A config.cfg file place in the same working directory is also needed. In this file the location of the different files and directories must be included in the following way:





The information is saved in the following format (one file per weather station):

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

