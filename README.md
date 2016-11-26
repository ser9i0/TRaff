# TRaff

This personal project is aimed to predict traffic intensity in Madrid (Spain) by getting almost-real-time traffic intensity values for several different streets and applying regression models to it, together with some others relevant variables such as datetime (hour, day of the week, season, etc.), weather (rainy, sunny, etc.) among others.

### Data source
Data are being downloaded from Madrid's official open data platform.

The source name is [Tráfico: Intensidad del tráfico en tiempo real (valores)](http://datos.madrid.es/portal/site/egob/menuitem.c05c1f754a33a9fbe4b2e4b284f1a5a0/?vgnextoid=02f2c23866b93410VgnVCM1000000b205a0aRCRD&vgnextchannel=374512b9ace9f310VgnVCM100000171f5a0aRCRD)

In summary, every 5 minutes a XML file is updated with the last traffic intensity values for about 3500-4000 different points distributed throughout the city.
