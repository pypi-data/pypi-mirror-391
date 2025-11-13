import datetime
from typing import Any, Optional
import requests
from fastapi import HTTPException


class GroundObservation:
    @staticmethod
    def get_synoptic_data(
        dt: datetime.datetime,
        station_id: str,
        auth_key: str,
    ) -> dict[str, Any]:
        """
        Get ground observation synoptic data.

        Parameters
        ----------
        dt : datetime.datetime
            Datetime to query.
        station_id : str
            Station ID.
        auth_key : str
            Authentication key.

        Returns
        -------
        dict[str, Any]
            Synoptic data.
        """

        response = requests.get(
            "https://apihub.kma.go.kr/api/typ01/url/kma_sfcdd.php",
            params={
                "tm": dt.strftime("%Y%m%d"),
                "stn": station_id,
                "disp": "1",
                "help": "0",
                "authKey": auth_key,
            },
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json()["result"]["message"],
            )

        data = response.text.splitlines()

        if len(data) < 7:
            raise HTTPException(
                status_code=404,
                detail="입력한 관측일 혹은 관측 지점에 데이터가 없습니다.",
            )

        data = data[-2].split(",")

        record = {
            "dt": datetime.datetime.strptime(data[0], "%Y%m%d"),
            "station_id": data[1],
            "wind_speed_average": float(data[2]),
            "wind_run": int(data[3]),
            "wind_direction_max": data[4],
            "wind_speed_max": float(data[5]),
            "wind_speed_max_dt": data[6],
            "wind_direction_instantaneous": data[7],
            "wind_speed_instantaneous": float(data[8]),
            "wind_speed_instantaneous_dt": data[9],
            "temperature_average": float(data[10]),
            "temperature_max": float(data[11]),
            "temperature_max_dt": data[12],
            "temperature_min": float(data[13]),
            "temperature_min_dt": data[14],
            "temperature_dew_point": float(data[15]),
            "temperature_ground": float(data[16]),
            "temperature_grass": float(data[17]),
            "humidity_average": float(data[18]),
            "humidity_min": float(data[19]),
            "humidity_min_dt": data[20],
            "water_vapor_pressure": float(data[21]),
            "evaporation_small": float(data[22]),
            "evaporation_large": float(data[23]),
            "fog_duration": float(data[24]),
            "atmospheric_pressure": float(data[25]),
            "atmospheric_pressure_sea_level": float(data[26]),
            "atmospheric_pressure_sea_level_max": float(data[27]),
            "atmospheric_pressure_sea_level_max_dt": data[28],
            "atmospheric_pressure_sea_level_min": float(data[29]),
            "atmospheric_pressure_sea_level_min_dt": data[30],
            "cloud_amount": float(data[31]),
            "sunshine": float(data[32]),
            "sunshine_duration": float(data[33]),
            "sunshine_campbell": float(data[34]),
            "solar_insolation": float(data[35]),
            "solar_insolation_60m_max": float(data[36]),
            "solar_insolation_60m_max_dt": data[37],
            "rainfall": float(data[38]),
            "rainfall_99": float(data[39]),
            "rainfall_duration": float(data[40]),
            "rainfall_60m_max": float(data[41]),
            "rainfall_60m_max_dt": data[42],
            "rainfall_10m_max": float(data[43]),
            "rainfall_10m_max_dt": data[44],
            "rainfall_intensity_max": float(data[45]),
            "rainfall_intensity_max_dt": data[46],
            "snow_depth_new": float(data[47]),
            "snow_depth_new_dt": data[48],
            "snow_depth_max": float(data[49]),
            "snow_depth_max_dt": data[50],
            "temperature_earth_05": float(data[51]),
            "temperature_earth_10": float(data[52]),
            "temperature_earth_15": float(data[53]),
            "temperature_earth_30": float(data[54]),
            "temperature_earth_50": float(data[55]),
        }

        for key, value in record.items():
            if key.endswith("_dt"):
                if "-" in value:
                    record[key] = None

                else:
                    value = value.rjust(4, "0")

                    record[key] = datetime.datetime(
                        record["dt"].year,
                        record["dt"].month,
                        record["dt"].day,
                        int(value[:2]) % 24,
                        int(value[2:]),
                    )

            elif isinstance(value, int):
                if value == -9:
                    record[key] = 0

            elif isinstance(value, float):
                if value == -9.0:
                    record[key] = 0.0

            elif isinstance(value, str):
                record[key] = value.strip()

        return record

    @staticmethod
    def get_station_data(
        auth_key: str,
        dt: Optional[datetime.datetime] = None,
    ) -> list[dict[str, Any]]:
        """
        Get ground observation station data.

        Parameters
        ----------
        auth_key : str
            Authentication key.
        dt : Optional[datetime.datetime]
            Datetime to query.

        Returns
        -------
        list[dict[str, Any]]
            Station data.
        """

        response = requests.get(
            "https://apihub.kma.go.kr/api/typ01/url/stn_inf.php",
            params={
                "inf": "SFC",
                "tm": dt.strftime("%Y%m%d%H%M%S") if dt is not None else None,
                "authKey": auth_key,
            },
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json()["result"]["message"],
            )

        data = response.text.splitlines()

        data = [elem.split() for elem in data[3:-2]]

        data = [
            {
                "station_id": elem[0],
                "longitude": elem[1],
                "latitude": elem[2],
                "altitude": elem[4],
                "altitude_barometer": elem[5],
                "altitude_thermometer": elem[6],
                "altitude_anemometer": elem[7],
                "altitude_rain_gauge": elem[8],
                "station_name": elem[10],
                "station_name_eng": elem[11],
                "management_facility_id": elem[12],
                "administrative_district_id": elem[13],
            }
            for elem in data
        ]

        return data
