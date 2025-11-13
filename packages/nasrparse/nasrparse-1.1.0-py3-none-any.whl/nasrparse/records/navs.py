from nasrparse.records.nav import *
from nasrparse.records.table_base import process_table
from nasrparse.filenames.nav import *
from nasrparse.functions import check_file_exists, open_csv

from os import path
from sqlite3 import Cursor

import csv


class NAVs:
    __dir_path: str

    nav_base: list[NAV_BASE]
    nav_rmk: list[NAV_RMK]
    nav_ckpt: list[NAV_CKPT]

    def __init__(self, dir_path: str):
        self.__dir_path = dir_path

        self.nav_base = []
        self.nav_rmk = []
        self.nav_ckpt = []

    def parse(self) -> None:
        self.parse_nav_base()
        self.parse_nav_rmk()
        self.parse_nav_ckpt()

    def parse_nav_base(self) -> None:
        file_path = path.join(self.__dir_path, NAV_BASE_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {NAV_BASE_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = NAV_BASE(
                    eff_date=row.get("EFF_DATE"),
                    nav_id=row.get("NAV_ID"),
                    nav_type=row.get("NAV_TYPE"),
                    state_code=row.get("STATE_CODE"),
                    city=row.get("CITY"),
                    country_code=row.get("COUNTRY_CODE"),
                    nav_status=row.get("NAV_STATUS"),
                    name=row.get("NAME"),
                    state_name=row.get("STATE_NAME"),
                    region_code=row.get("REGION_CODE"),
                    country_name=row.get("COUNTRY_NAME"),
                    fan_marker=row.get("FAN_MARKER"),
                    owner=row.get("OWNER"),
                    operator=row.get("OPERATOR"),
                    nas_use_flag=row.get("NAS_USE_FLAG"),
                    public_use_flag=row.get("PUBLIC_USE_FLAG"),
                    ndb_class_code=row.get("NDB_CLASS_CODE"),
                    oper_hours=row.get("OPER_HOURS"),
                    high_alt_artcc_id=row.get("HIGH_ALT_ARTCC_ID"),
                    high_artcc_name=row.get("HIGH_ARTCC_NAME"),
                    low_alt_artcc_id=row.get("LOW_ALT_ARTCC_ID"),
                    low_artcc_name=row.get("LOW_ARTCC_NAME"),
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
                    survey_accuracy_code=row.get("SURVEY_ACCURACY_CODE"),
                    tacan_dme_status=row.get("TACAN_DME_STATUS"),
                    tacan_dme_lat_deg=row.get("TACAN_DME_LAT_DEG"),
                    tacan_dme_lat_min=row.get("TACAN_DME_LAT_MIN"),
                    tacan_dme_lat_sec=row.get("TACAN_DME_LAT_SEC"),
                    tacan_dme_lat_hemis=row.get("TACAN_DME_LAT_HEMIS"),
                    tacan_dme_lat_decimal=row.get("TACAN_DME_LAT_DECIMAL"),
                    tacan_dme_lon_deg=row.get("TACAN_DME_LONG_DEG"),
                    tacan_dme_lon_min=row.get("TACAN_DME_LONG_MIN"),
                    tacan_dme_lon_sec=row.get("TACAN_DME_LONG_SEC"),
                    tacan_dme_lon_hemis=row.get("TACAN_DME_LONG_HEMIS"),
                    tacan_dme_lon_decimal=row.get("TACAN_DME_LONG_DECIMAL"),
                    elev=row.get("ELEV"),
                    mag_varn=row.get("MAG_VARN"),
                    mag_varn_hemis=row.get("MAG_VARN_HEMIS"),
                    mag_varn_year=row.get("MAG_VARN_YEAR"),
                    simul_voice_flag=row.get("SIMUL_VOICE_FLAG"),
                    pwr_output=row.get("PWR_OUTPUT"),
                    auto_voice_id_flag=row.get("AUTO_VOICE_ID_FLAG"),
                    mnt_cat_code=row.get("MNT_CAT_CODE"),
                    voice_call=row.get("VOICE_CALL"),
                    chan=row.get("CHAN"),
                    freq=row.get("FREQ"),
                    mkr_ident=row.get("MKR_IDENT"),
                    mkr_shape=row.get("MKR_SHAPE"),
                    mkr_brg=row.get("MKR_BRG"),
                    alt_code=row.get("ALT_CODE"),
                    dme_ssv=row.get("DME_SSV"),
                    low_nav_on_high_chart_flag=row.get("LOW_NAV_ON_HIGH_CHART_FLAG"),
                    z_mkr_flag=row.get("Z_MKR_FLAG"),
                    fss_id=row.get("FSS_ID"),
                    fss_name=row.get("FSS_NAME"),
                    fss_hours=row.get("FSS_HOURS"),
                    notam_id=row.get("NOTAM_ID"),
                    quad_ident=row.get("QUAD_IDENT"),
                    pitch_flag=row.get("PITCH_FLAG"),
                    catch_flag=row.get("CATCH_FLAG"),
                    sua_atcaa_flag=row.get("SUA_ATCAA_FLAG"),
                    restriction_flag=row.get("RESTRICTION_FLAG"),
                    hiwas_flag=row.get("HIWAS_FLAG"),
                )
                self.nav_base.append(record)

    def parse_nav_rmk(self) -> None:
        file_path = path.join(self.__dir_path, NAV_RMK_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {NAV_RMK_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = NAV_RMK(
                    eff_date=row.get("EFF_DATE"),
                    nav_id=row.get("NAV_ID"),
                    nav_type=row.get("NAV_TYPE"),
                    state_code=row.get("STATE_CODE"),
                    city=row.get("CITY"),
                    country_code=row.get("COUNTRY_CODE"),
                    tab_name=row.get("TAB_NAME"),
                    ref_col_name=row.get("REF_COL_NAME"),
                    ref_col_seq_no=row.get("REF_COL_SEQ_NO"),
                    remark=row.get("REMARK"),
                )
                self.nav_rmk.append(record)

    def parse_nav_ckpt(self) -> None:
        file_path = path.join(self.__dir_path, NAV_CKPT_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {NAV_CKPT_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = NAV_CKPT(
                    eff_date=row.get("EFF_DATE"),
                    nav_id=row.get("NAV_ID"),
                    nav_type=row.get("NAV_TYPE"),
                    state_code=row.get("STATE_CODE"),
                    city=row.get("CITY"),
                    country_code=row.get("COUNTRY_CODE"),
                    altitude=row.get("ALTITUDE"),
                    brg=row.get("BRG"),
                    air_gnd_code=row.get("AIR_GND_CODE"),
                    chk_desc=row.get("CHK_DESC"),
                    arpt_id=row.get("ARPT_ID"),
                    state_chk_code=row.get("STATE_CHK_CODE"),
                )
                self.nav_ckpt.append(record)

    def to_dict(self) -> dict:
        return {
            **self.nav_base_to_dict(),
            **self.nav_rmk_to_dict(),
            **self.nav_ckpt_to_dict(),
        }

    def to_db(self, db_cursor: Cursor) -> None:
        self.nav_base_to_db(db_cursor)
        self.nav_rmk_to_db(db_cursor)
        self.nav_ckpt_to_db(db_cursor)

    def nav_base_to_dict(self) -> dict:
        return {"nav_base": [item.to_dict() for item in self.nav_base]}

    def nav_rmk_to_dict(self) -> dict:
        return {"nav_rmk": [item.to_dict() for item in self.nav_rmk]}

    def nav_ckpt_to_dict(self) -> dict:
        return {"nav_ckpt": [item.to_dict() for item in self.nav_ckpt]}

    def nav_base_to_db(self, db_cursor: Cursor) -> None:
        if len(self.nav_base) > 0:
            print(f"               Processing {NAV_BASE_FILE_NAME}")
            process_table(db_cursor, self.nav_base)

    def nav_rmk_to_db(self, db_cursor: Cursor) -> None:
        if len(self.nav_rmk) > 0:
            print(f"               Processing {NAV_RMK_FILE_NAME}")
            process_table(db_cursor, self.nav_rmk)

    def nav_ckpt_to_db(self, db_cursor: Cursor) -> None:
        if len(self.nav_ckpt) > 0:
            print(f"               Processing {NAV_CKPT_FILE_NAME}")
            process_table(db_cursor, self.nav_ckpt)
