from nasrparse.records.wxl import *
from nasrparse.records.table_base import process_table
from nasrparse.filenames.wxl import *
from nasrparse.functions import check_file_exists, open_csv

from os import path
from sqlite3 import Cursor

import csv


class WXLs:
    __dir_path: str

    wxl_base: list[WXL_BASE]
    wxl_svc: list[WXL_SVC]

    def __init__(self, dir_path: str):
        self.__dir_path = dir_path

        self.wxl_base = []
        self.wxl_svc = []

    def parse(self) -> None:
        self.parse_wxl_base()
        self.parse_wxl_svc()

    def parse_wxl_base(self) -> None:
        file_path = path.join(self.__dir_path, WXL_BASE_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {WXL_BASE_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = WXL_BASE(
                    eff_date=row.get("EFF_DATE"),
                    wea_id=row.get("WEA_ID"),
                    city=row.get("CITY"),
                    state_code=row.get("STATE_CODE"),
                    country_code=row.get("COUNTRY_CODE"),
                    lat_deg=row.get("LAT_DEG"),
                    lat_min=row.get("LAT_MIN"),
                    lat_sec=row.get("LAT_SEC"),
                    lat_hemis=row.get("LAT_HEMIS"),
                    lat_decimal=row.get("LAT_DECIMAL"),
                    lon_deg=row.get("LONG_DEG"),
                    lon_min=row.get("LONG_MIN"),
                    lon_sec=row.get("LONG_SEC"),
                    lon_hemis=row.get("LONG_HEMIS"),
                    lon_decimal=row.get("LONG_DECIMAL"),
                    elev=row.get("ELEV"),
                    survey_method_code=row.get("SURVEY_METHOD_CODE"),
                )
                self.wxl_base.append(record)

    def parse_wxl_svc(self) -> None:
        file_path = path.join(self.__dir_path, WXL_SVC_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {WXL_SVC_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = WXL_SVC(
                    eff_date=row.get("EFF_DATE"),
                    wea_id=row.get("WEA_ID"),
                    city=row.get("CITY"),
                    state_code=row.get("STATE_CODE"),
                    country_code=row.get("COUNTRY_CODE"),
                    wea_svc_type_code=row.get("WEA_SVC_TYPE_CODE"),
                    wea_affect_area=row.get("WEA_AFFECT_AREA"),
                )
                self.wxl_svc.append(record)

    def to_dict(self) -> dict:
        return {
            **self.wxl_base_to_dict(),
            **self.wxl_svc_to_dict(),
        }

    def to_db(self, db_cursor: Cursor) -> None:
        self.wxl_base_to_db(db_cursor)
        self.wxl_svc_to_db(db_cursor)

    def wxl_base_to_dict(self) -> dict:
        return {"wxl_base": [item.to_dict() for item in self.wxl_base]}

    def wxl_svc_to_dict(self) -> dict:
        return {"wxl_svc": [item.to_dict() for item in self.wxl_svc]}

    def wxl_base_to_db(self, db_cursor: Cursor) -> None:
        if len(self.wxl_base) > 0:
            print(f"               Processing {WXL_BASE_FILE_NAME}")
            process_table(db_cursor, self.wxl_base)

    def wxl_svc_to_db(self, db_cursor: Cursor) -> None:
        if len(self.wxl_svc) > 0:
            print(f"               Processing {WXL_SVC_FILE_NAME}")
            process_table(db_cursor, self.wxl_svc)
