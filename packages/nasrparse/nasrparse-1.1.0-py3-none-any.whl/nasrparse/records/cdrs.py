from nasrparse.records.cdr import *
from nasrparse.records.table_base import process_table
from nasrparse.filenames.cdr import *
from nasrparse.functions import check_file_exists, open_csv

from os import path
from sqlite3 import Cursor

import csv


class CDRs:
    __dir_path: str

    cdr_base: list[CDR_BASE]

    def __init__(self, dir_path: str):
        self.__dir_path = dir_path

        self.cdr_base = []

    def parse(self) -> None:
        self.parse_cdr_base()

    def parse_cdr_base(self) -> None:
        file_path = path.join(self.__dir_path, CDR_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path, "utf-8-sig") as f:
            print(f"               Parsing {CDR_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = CDR_BASE(
                    rcode=row.get("RCode"),
                    orig=row.get("Orig"),
                    dest=row.get("Dest"),
                    depfix=row.get("DepFix"),
                    route_string=row.get("Route String"),
                    dcntr=row.get("DCNTR"),
                    acntr=row.get("ACNTR"),
                    tcntrs=row.get("TCNTRs"),
                    coordreq=row.get("CoordReq"),
                    play=row.get("Play"),
                    naveqp=row.get("NavEqp"),
                    length=row.get("Length"),
                )
                self.cdr_base.append(record)

    def to_dict(self) -> dict:
        return {
            **self.cdr_base_to_dict(),
        }

    def to_db(self, db_cursor: Cursor) -> None:
        self.cdr_base_to_db(db_cursor)

    def cdr_base_to_dict(self) -> dict:
        return {"cdr_base": [item.to_dict() for item in self.cdr_base]}

    def cdr_base_to_db(self, db_cursor: Cursor) -> None:
        if len(self.cdr_base) > 0:
            print(f"               Processing {CDR_FILE_NAME}")
            process_table(db_cursor, self.cdr_base)
