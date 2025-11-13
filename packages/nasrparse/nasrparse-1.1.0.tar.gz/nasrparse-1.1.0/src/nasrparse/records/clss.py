from nasrparse.records.cls import *
from nasrparse.records.table_base import process_table
from nasrparse.filenames.cls import *
from nasrparse.functions import check_file_exists, open_csv

from os import path
from sqlite3 import Cursor

import csv


class CLSs:
    __dir_path: str

    cls_arsp: list[CLS_ARSP]

    def __init__(self, dir_path: str):
        self.__dir_path = dir_path

        self.cls_arsp = []

    def parse(self) -> None:
        self.parse_cls_arsp()

    def parse_cls_arsp(self) -> None:
        file_path = path.join(self.__dir_path, CLS_ARSP_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {CLS_ARSP_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = CLS_ARSP(
                    eff_date=row.get("EFF_DATE"),
                    site_no=row.get("SITE_NO"),
                    site_type_code=row.get("SITE_TYPE_CODE"),
                    state_code=row.get("STATE_CODE"),
                    arpt_id=row.get("ARPT_ID"),
                    city=row.get("CITY"),
                    country_code=row.get("COUNTRY_CODE"),
                    class_b_airspace=row.get("CLASS_B_AIRSPACE"),
                    class_c_airspace=row.get("CLASS_C_AIRSPACE"),
                    class_d_airspace=row.get("CLASS_D_AIRSPACE"),
                    class_e_airspace=row.get("CLASS_E_AIRSPACE"),
                    airspace_hrs=row.get("AIRSPACE_HRS"),
                    remark=row.get("REMARK"),
                )
                self.cls_arsp.append(record)

    def to_dict(self) -> dict:
        return {
            **self.cls_arsp_to_dict(),
        }

    def to_db(self, db_cursor: Cursor) -> None:
        self.cls_arsp_to_db(db_cursor)

    def cls_arsp_to_dict(self) -> dict:
        return {"cls_arsp": [item.to_dict() for item in self.cls_arsp]}

    def cls_arsp_to_db(self, db_cursor: Cursor) -> None:
        if len(self.cls_arsp) > 0:
            print(f"               Processing {CLS_ARSP_FILE_NAME}")
            process_table(db_cursor, self.cls_arsp)
