from nasrparse.records.frq import *
from nasrparse.records.table_base import process_table
from nasrparse.filenames.frq import *
from nasrparse.functions import check_file_exists, open_csv

from os import path
from sqlite3 import Cursor

import csv


class FRQs:
    __dir_path: str

    frq_base: list[FRQ_BASE]

    def __init__(self, dir_path: str):
        self.__dir_path = dir_path

        self.frq_base = []

    def parse(self) -> None:
        self.parse_frq_base()

    def parse_frq_base(self) -> None:
        file_path = path.join(self.__dir_path, FRQ_BASE_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {FRQ_BASE_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = FRQ_BASE(
                    eff_date=row.get("EFF_DATE"),
                    facility=row.get("FACILITY"),
                    fac_name=row.get("FAC_NAME"),
                    facility_type=row.get("FACILITY_TYPE"),
                    artcc_or_fss_id=row.get("ARTCC_OR_FSS_ID"),
                    cpdlc=row.get("CPDLC"),
                    tower_hrs=row.get("TOWER_HRS"),
                    serviced_facility=row.get("SERVICED_FACILITY"),
                    serviced_fac_name=row.get("SERVICED_FAC_NAME"),
                    serviced_site_type=row.get("SERVICED_SITE_TYPE"),
                    lat_decimal=row.get("LAT_DECIMAL"),
                    lon_decimal=row.get("LONG_DECIMAL"),
                    serviced_city=row.get("SERVICED_CITY"),
                    serviced_state=row.get("SERVICED_STATE"),
                    serviced_country=row.get("SERVICED_COUNTRY"),
                    tower_or_comm_call=row.get("TOWER_OR_COMM_CALL"),
                    primary_approach_radio_call=row.get("PRIMARY_APPROACH_RADIO_CALL"),
                    freq=row.get("FREQ"),
                    sectorization=row.get("SECTORIZATION"),
                    freq_use=row.get("FREQ_USE"),
                    remark=row.get("REMARK"),
                )
                self.frq_base.append(record)

    def to_dict(self) -> dict:
        return {
            **self.frq_base_to_dict(),
        }

    def to_db(self, db_cursor: Cursor) -> None:
        self.frq_base_to_db(db_cursor)

    def frq_base_to_dict(self) -> dict:
        return {"frq_base": [item.to_dict() for item in self.frq_base]}

    def frq_base_to_db(self, db_cursor: Cursor) -> None:
        if len(self.frq_base) > 0:
            print(f"               Processing {FRQ_BASE_FILE_NAME}")
            process_table(db_cursor, self.frq_base)
