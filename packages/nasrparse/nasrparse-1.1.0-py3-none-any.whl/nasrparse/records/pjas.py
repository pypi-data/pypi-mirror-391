from nasrparse.records.pja import *
from nasrparse.records.table_base import process_table
from nasrparse.filenames.pja import *
from nasrparse.functions import check_file_exists, open_csv

from os import path
from sqlite3 import Cursor

import csv


class PJAs:
    __dir_path: str

    pja_base: list[PJA_BASE]
    pja_con: list[PJA_CON]

    def __init__(self, dir_path: str):
        self.__dir_path = dir_path

        self.pja_base = []
        self.pja_con = []

    def parse(self) -> None:
        self.parse_pja_base()
        self.parse_pja_con()

    def parse_pja_base(self) -> None:
        file_path = path.join(self.__dir_path, PJA_BASE_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {PJA_BASE_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = PJA_BASE(
                    eff_date=row.get("EFF_DATE"),
                    pja_id=row.get("PJA_ID"),
                    nav_id=row.get("NAV_ID"),
                    nav_type=row.get("NAV_TYPE"),
                    radial=row.get("RADIAL"),
                    distance=row.get("DISTANCE"),
                    navaid_name=row.get("NAVAID_NAME"),
                    state_code=row.get("STATE_CODE"),
                    city=row.get("CITY"),
                    latitude=row.get("LATITUDE"),
                    lat_decimal=row.get("LAT_DECIMAL"),
                    longitude=row.get("LONGITUDE"),
                    long_decimal=row.get("LONG_DECIMAL"),
                    arpt_id=row.get("ARPT_ID"),
                    site_no=row.get("SITE_NO"),
                    site_type_code=row.get("SITE_TYPE_CODE"),
                    drop_zone_name=row.get("DROP_ZONE_NAME"),
                    max_altitude=row.get("MAX_ALTITUDE"),
                    max_altitude_type_code=row.get("MAX_ALTITUDE_TYPE_CODE"),
                    pja_radius=row.get("PJA_RADIUS"),
                    chart_request_flag=row.get("CHART_REQUEST_FLAG"),
                    publish_criteria=row.get("PUBLISH_CRITERIA"),
                    description=row.get("DESCRIPTION"),
                    time_of_use=row.get("TIME_OF_USE"),
                    fss_id=row.get("FSS_ID"),
                    fss_name=row.get("FSS_NAME"),
                    pja_use=row.get("PJA_USE"),
                    volume=row.get("VOLUME"),
                    pja_user=row.get("PJA_USER"),
                    remark=row.get("REMARK"),
                )
                self.pja_base.append(record)

    def parse_pja_con(self) -> None:
        file_path = path.join(self.__dir_path, PJA_CON_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {PJA_CON_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = PJA_CON(
                    eff_date=row.get("EFF_DATE"),
                    pja_id=row.get("PJA_ID"),
                    fac_id=row.get("FAC_ID"),
                    fac_name=row.get("FAC_NAME"),
                    loc_id=row.get("LOC_ID"),
                    commercial_freq=row.get("COMMERCIAL_FREQ"),
                    commercial_chart_flag=row.get("COMMERCIAL_CHART_FLAG"),
                    mil_freq=row.get("MIL_FREQ"),
                    mil_chart_flag=row.get("MIL_CHART_FLAG"),
                    sector=row.get("SECTOR"),
                    contact_freq_altitude=row.get("CONTACT_FREQ_ALTITUDE"),
                )
                self.pja_con.append(record)

    def to_dict(self) -> dict:
        return {
            **self.pja_base_to_dict(),
            **self.pja_con_to_dict(),
        }

    def to_db(self, db_cursor: Cursor) -> None:
        self.pja_base_to_db(db_cursor)
        self.pja_con_to_db(db_cursor)

    def pja_base_to_dict(self) -> dict:
        return {"pja_base": [item.to_dict() for item in self.pja_base]}

    def pja_con_to_dict(self) -> dict:
        return {"pja_con": [item.to_dict() for item in self.pja_con]}

    def pja_base_to_db(self, db_cursor: Cursor) -> None:
        if len(self.pja_base) > 0:
            print(f"               Processing {PJA_BASE_FILE_NAME}")
            process_table(db_cursor, self.pja_base)

    def pja_con_to_db(self, db_cursor: Cursor) -> None:
        if len(self.pja_con) > 0:
            print(f"               Processing {PJA_CON_FILE_NAME}")
            process_table(db_cursor, self.pja_con)
