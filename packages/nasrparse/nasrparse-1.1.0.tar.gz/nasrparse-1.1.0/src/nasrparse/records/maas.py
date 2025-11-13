from nasrparse.records.maa import *
from nasrparse.records.table_base import process_table
from nasrparse.filenames.maa import *
from nasrparse.functions import check_file_exists, open_csv

from os import path
from sqlite3 import Cursor

import csv


class MAAs:
    __dir_path: str

    maa_base: list[MAA_BASE]
    maa_con: list[MAA_CON]
    maa_rmk: list[MAA_RMK]
    maa_shp: list[MAA_SHP]

    def __init__(self, dir_path: str):
        self.__dir_path = dir_path

        self.maa_base = []
        self.maa_con = []
        self.maa_rmk = []
        self.maa_shp = []

    def parse(self) -> None:
        self.parse_maa_base()
        self.parse_maa_con()
        self.parse_maa_rmk()
        self.parse_maa_shp()

    def parse_maa_base(self) -> None:
        file_path = path.join(self.__dir_path, MAA_BASE_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {MAA_BASE_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = MAA_BASE(
                    eff_date=row.get("EFF_DATE"),
                    maa_id=row.get("MAA_ID"),
                    maa_type_name=row.get("MAA_TYPE_NAME"),
                    nav_id=row.get("NAV_ID"),
                    nav_type=row.get("NAV_TYPE"),
                    nav_radial=row.get("NAV_RADIAL"),
                    nav_distance=row.get("NAV_DISTANCE"),
                    state_code=row.get("STATE_CODE"),
                    city=row.get("CITY"),
                    latitude=row.get("LATITUDE"),
                    longitude=row.get("LONGITUDE"),
                    arpt_ids=row.get("ARPT_IDS"),
                    nearest_arpt=row.get("NEAREST_ARPT"),
                    nearest_arpt_dist=row.get("NEAREST_ARPT_DIST"),
                    nearest_arpt_dir=row.get("NEAREST_ARPT_DIR"),
                    maa_name=row.get("MAA_NAME"),
                    max_alt=row.get("MAX_ALT"),
                    min_alt=row.get("MIN_ALT"),
                    maa_radius=row.get("MAA_RADIUS"),
                    description=row.get("DESCRIPTION"),
                    maa_use=row.get("MAA_USE"),
                    check_notams=row.get("CHECK_NOTAMS"),
                    time_of_use=row.get("TIME_OF_USE"),
                    user_group_name=row.get("USER_GROUP_NAME"),
                )
                self.maa_base.append(record)

    def parse_maa_con(self) -> None:
        file_path = path.join(self.__dir_path, MAA_CON_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {MAA_CON_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = MAA_CON(
                    eff_date=row.get("EFF_DATE"),
                    maa_id=row.get("MAA_ID"),
                    freq_seq=row.get("FREQ_SEQ"),
                    fac_id=row.get("FAC_ID"),
                    fac_name=row.get("FAC_NAME"),
                    commercial_freq=row.get("COMMERCIAL_FREQ"),
                    commercial_chart_flag=row.get("COMMERCIAL_CHART_FLAG"),
                    mil_freq=row.get("MIL_FREQ"),
                    mil_chart_flag=row.get("MIL_CHART_FLAG"),
                )
                self.maa_con.append(record)

    def parse_maa_rmk(self) -> None:
        file_path = path.join(self.__dir_path, MAA_RMK_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {MAA_RMK_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = MAA_RMK(
                    eff_date=row.get("EFF_DATE"),
                    maa_id=row.get("MAA_ID"),
                    tab_name=row.get("TAB_NAME"),
                    ref_col_name=row.get("REF_COL_NAME"),
                    ref_col_seq_no=row.get("REF_COL_SEQ_NO"),
                    remark=row.get("REMARK"),
                )
                self.maa_rmk.append(record)

    def parse_maa_shp(self) -> None:
        file_path = path.join(self.__dir_path, MAA_SHP_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {MAA_SHP_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = MAA_SHP(
                    eff_date=row.get("EFF_DATE"),
                    maa_id=row.get("MAA_ID"),
                    point_seq=row.get("POINT_SEQ"),
                    latitude=row.get("LATITUDE"),
                    longitude=row.get("LONGITUDE"),
                )
                self.maa_shp.append(record)

    def to_dict(self) -> dict:
        return {
            **self.maa_base_to_dict(),
            **self.maa_con_to_dict(),
            **self.maa_rmk_to_dict(),
            **self.maa_shp_to_dict(),
        }

    def to_db(self, db_cursor: Cursor) -> None:
        self.maa_base_to_db(db_cursor)
        self.maa_con_to_db(db_cursor)
        self.maa_rmk_to_db(db_cursor)
        self.maa_shp_to_db(db_cursor)

    def maa_base_to_dict(self) -> dict:
        return {"maa_base": [item.to_dict() for item in self.maa_base]}

    def maa_con_to_dict(self) -> dict:
        return {"maa_con": [item.to_dict() for item in self.maa_con]}

    def maa_rmk_to_dict(self) -> dict:
        return {"maa_rmk": [item.to_dict() for item in self.maa_rmk]}

    def maa_shp_to_dict(self) -> dict:
        return {"maa_shp": [item.to_dict() for item in self.maa_shp]}

    def maa_base_to_db(self, db_cursor: Cursor) -> None:
        if len(self.maa_base) > 0:
            print(f"               Processing {MAA_BASE_FILE_NAME}")
            process_table(db_cursor, self.maa_base)

    def maa_con_to_db(self, db_cursor: Cursor) -> None:
        if len(self.maa_con) > 0:
            print(f"               Processing {MAA_CON_FILE_NAME}")
            process_table(db_cursor, self.maa_con)

    def maa_rmk_to_db(self, db_cursor: Cursor) -> None:
        if len(self.maa_rmk) > 0:
            print(f"               Processing {MAA_RMK_FILE_NAME}")
            process_table(db_cursor, self.maa_rmk)

    def maa_shp_to_db(self, db_cursor: Cursor) -> None:
        if len(self.maa_shp) > 0:
            print(f"               Processing {MAA_SHP_FILE_NAME}")
            process_table(db_cursor, self.maa_shp)
