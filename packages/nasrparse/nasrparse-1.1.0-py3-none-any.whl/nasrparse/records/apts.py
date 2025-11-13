from nasrparse.records.apt import *
from nasrparse.records.table_base import process_table
from nasrparse.filenames.apt import *
from nasrparse.functions import check_file_exists, open_csv

from os import path
from sqlite3 import Cursor

import csv


class APTs:
    __dir_path: str

    apt_ars: list[APT_ARS]
    apt_att: list[APT_ATT]
    apt_base: list[APT_BASE]
    apt_con: list[APT_CON]
    apt_rmk: list[APT_RMK]
    apt_rwy: list[APT_RWY]
    apt_rwy_end: list[APT_RWY_END]

    def __init__(self, dir_path: str):
        self.__dir_path = dir_path

        self.apt_ars = []
        self.apt_att = []
        self.apt_base = []
        self.apt_con = []
        self.apt_rmk = []
        self.apt_rwy = []
        self.apt_rwy_end = []

    def parse(self) -> None:
        self.parse_apt_ars()
        self.parse_apt_att()
        self.parse_apt_base()
        self.parse_apt_con()
        self.parse_apt_rmk()
        self.parse_apt_rwy()
        self.parse_apt_rwy_end()

    def parse_apt_ars(self) -> None:
        file_path = path.join(self.__dir_path, APT_ARS_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {APT_ARS_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = APT_ARS(
                    eff_date=row.get("EFF_DATE"),
                    site_no=row.get("SITE_NO"),
                    site_type_code=row.get("SITE_TYPE_CODE"),
                    state_code=row.get("STATE_CODE"),
                    arpt_id=row.get("ARPT_ID"),
                    city=row.get("CITY"),
                    country_code=row.get("COUNTRY_CODE"),
                    rwy_id=row.get("RWY_ID"),
                    rwy_end_id=row.get("RWY_END_ID"),
                    arrest_device_code=row.get("ARREST_DEVICE_CODE"),
                )
                self.apt_ars.append(record)

    def parse_apt_att(self) -> None:
        file_path = path.join(self.__dir_path, APT_ATT_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {APT_ATT_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = APT_ATT(
                    eff_date=row.get("EFF_DATE"),
                    site_no=row.get("SITE_NO"),
                    site_type_code=row.get("SITE_TYPE_CODE"),
                    state_code=row.get("STATE_CODE"),
                    arpt_id=row.get("ARPT_ID"),
                    city=row.get("CITY"),
                    country_code=row.get("COUNTRY_CODE"),
                    sked_seq_no=row.get("SKED_SEQ_NO"),
                    month=row.get("MONTH"),
                    day=row.get("DAY"),
                    hour=row.get("HOUR"),
                )
                self.apt_att.append(record)

    def parse_apt_base(self) -> None:
        file_path = path.join(self.__dir_path, APT_BASE_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {APT_BASE_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = APT_BASE(
                    eff_date=row.get("EFF_DATE"),
                    site_no=row.get("SITE_NO"),
                    site_type_code=row.get("SITE_TYPE_CODE"),
                    state_code=row.get("STATE_CODE"),
                    arpt_id=row.get("ARPT_ID"),
                    city=row.get("CITY"),
                    country_code=row.get("COUNTRY_CODE"),
                    region_code=row.get("REGION_CODE"),
                    ado_code=row.get("ADO_CODE"),
                    state_name=row.get("STATE_NAME"),
                    county_name=row.get("COUNTY_NAME"),
                    county_assoc_state=row.get("COUNTY_ASSOC_STATE"),
                    arpt_name=row.get("ARPT_NAME"),
                    ownership_type_code=row.get("OWNERSHIP_TYPE_CODE"),
                    facility_use_code=row.get("FACILITY_USE_CODE"),
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
                    survey_method_code=row.get("SURVEY_METHOD_CODE"),
                    elev=row.get("ELEV"),
                    elev_method_code=row.get("ELEV_METHOD_CODE"),
                    mag_varn=row.get("MAG_VARN"),
                    mag_hemis=row.get("MAG_HEMIS"),
                    mag_varn_year=row.get("MAG_VARN_YEAR"),
                    tpa=row.get("TPA"),
                    chart_name=row.get("CHART_NAME"),
                    dist_city_to_airport=row.get("DIST_CITY_TO_AIRPORT"),
                    direction_code=row.get("DIRECTION_CODE"),
                    acreage=row.get("ACREAGE"),
                    resp_artcc_id=row.get("RESP_ARTCC_ID"),
                    computer_id=row.get("COMPUTER_ID"),
                    artcc_name=row.get("ARTCC_NAME"),
                    fss_on_arpt_flag=row.get("FSS_ON_ARPT_FLAG"),
                    fss_id=row.get("FSS_ID"),
                    fss_name=row.get("FSS_NAME"),
                    phone_no=row.get("PHONE_NO"),
                    toll_free_no=row.get("TOLL_FREE_NO"),
                    alt_fss_id=row.get("ALT_FSS_ID"),
                    alt_fss_name=row.get("ALT_FSS_NAME"),
                    alt_toll_free_no=row.get("ALT_TOLL_FREE_NO"),
                    notam_id=row.get("NOTAM_ID"),
                    notam_flag=row.get("NOTAM_FLAG"),
                    activation_date=row.get("ACTIVATION_DATE"),
                    arpt_status=row.get("ARPT_STATUS"),
                    far_139_type_code=row.get("FAR_139_TYPE_CODE"),
                    far_139_carrier_ser_code=row.get("FAR_139_CARRIER_SER_CODE"),
                    arff_cert_type_date=row.get("ARFF_CERT_TYPE_DATE"),
                    nasp_code=row.get("NASP_CODE"),
                    asp_anlys_dtrm_code=row.get("ASP_ANLYS_DTRM_CODE"),
                    cust_flag=row.get("CUST_FLAG"),
                    lndg_rights_flag=row.get("LNDG_RIGHTS_FLAG"),
                    joint_use_flag=row.get("JOINT_USE_FLAG"),
                    mil_lndg_flag=row.get("MIL_LNDG_FLAG"),
                    inspect_method_code=row.get("INSPECT_METHOD_CODE"),
                    inspector_code=row.get("INSPECTOR_CODE"),
                    last_inspection=row.get("LAST_INSPECTION"),
                    last_info_response=row.get("LAST_INFO_RESPONSE"),
                    fuel_types=row.get("FUEL_TYPES"),
                    airframe_repair_ser_code=row.get("AIRFRAME_REPAIR_SER_CODE"),
                    pwr_plant_repair_ser=row.get("PWR_PLANT_REPAIR_SER"),
                    bottled_oxy_type=row.get("BOTTLED_OXY_TYPE"),
                    bulk_oxy_type=row.get("BULK_OXY_TYPE"),
                    lgt_sked=row.get("LGT_SKED"),
                    bcn_lgt_sked=row.get("BCN_LGT_SKED"),
                    twr_type_code=row.get("TWR_TYPE_CODE"),
                    seg_circle_mkr_flag=row.get("SEG_CIRCLE_MKR_FLAG"),
                    bcn_lens_color=row.get("BCN_LENS_COLOR"),
                    lndg_fee_flag=row.get("LNDG_FEE_FLAG"),
                    medical_use_flag=row.get("MEDICAL_USE_FLAG"),
                    arpt_psn_source=row.get("ARPT_PSN_SOURCE"),
                    position_src_date=row.get("POSITION_SRC_DATE"),
                    arpt_elev_source=row.get("ARPT_ELEV_SOURCE"),
                    elevation_src_date=row.get("ELEVATION_SRC_DATE"),
                    contr_fuel_avbl=row.get("CONTR_FUEL_AVBL"),
                    trns_strg_buoy_flag=row.get("TRNS_STRG_BUOY_FLAG"),
                    trns_strg_hgr_flag=row.get("TRNS_STRG_HGR_FLAG"),
                    trns_strg_tie_flag=row.get("TRNS_STRG_TIE_FLAG"),
                    other_services=row.get("OTHER_SERVICES"),
                    wind_indcr_flag=row.get("WIND_INDCR_FLAG"),
                    icao_id=row.get("ICAO_ID"),
                    min_op_network=row.get("MIN_OP_NETWORK"),
                    user_fee_flag=row.get("USER_FEE_FLAG"),
                    cta=row.get("CTA"),
                )
                self.apt_base.append(record)

    def parse_apt_con(self) -> None:
        file_path = path.join(self.__dir_path, APT_CON_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {APT_CON_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = APT_CON(
                    eff_date=row.get("EFF_DATE"),
                    site_no=row.get("SITE_NO"),
                    site_type_code=row.get("SITE_TYPE_CODE"),
                    state_code=row.get("STATE_CODE"),
                    arpt_id=row.get("ARPT_ID"),
                    city=row.get("CITY"),
                    country_code=row.get("COUNTRY_CODE"),
                    title=row.get("TITLE"),
                    name=row.get("NAME"),
                    address1=row.get("ADDRESS1"),
                    address2=row.get("ADDRESS2"),
                    title_city=row.get("TITLE_CITY"),
                    state=row.get("STATE"),
                    zip_code=row.get("ZIP_CODE"),
                    zip_plus_four=row.get("ZIP_PLUS_FOUR"),
                    phone_no=row.get("PHONE_NO"),
                )
                self.apt_con.append(record)

    def parse_apt_rmk(self) -> None:
        file_path = path.join(self.__dir_path, APT_RMK_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {APT_RMK_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = APT_RMK(
                    eff_date=row.get("EFF_DATE"),
                    site_no=row.get("SITE_NO"),
                    site_type_code=row.get("SITE_TYPE_CODE"),
                    state_code=row.get("STATE_CODE"),
                    arpt_id=row.get("ARPT_ID"),
                    city=row.get("CITY"),
                    country_code=row.get("COUNTRY_CODE"),
                    legacy_element_number=row.get("LEGACY_ELEMENT_NUMBER"),
                    tab_name=row.get("TAB_NAME"),
                    ref_col_name=row.get("REF_COL_NAME"),
                    element=row.get("ELEMENT"),
                    ref_col_seq_no=row.get("REF_COL_SEQ_NO"),
                    remark=row.get("REMARK"),
                )
                self.apt_rmk.append(record)

    def parse_apt_rwy(self) -> None:
        file_path = path.join(self.__dir_path, APT_RWY_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {APT_RWY_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = APT_RWY(
                    eff_date=row.get("EFF_DATE"),
                    site_no=row.get("SITE_NO"),
                    site_type_code=row.get("SITE_TYPE_CODE"),
                    state_code=row.get("STATE_CODE"),
                    arpt_id=row.get("ARPT_ID"),
                    city=row.get("CITY"),
                    country_code=row.get("COUNTRY_CODE"),
                    rwy_id=row.get("RWY_ID"),
                    rwy_len=row.get("RWY_LEN"),
                    rwy_width=row.get("RWY_WIDTH"),
                    surface_type_code=row.get("SURFACE_TYPE_CODE"),
                    cond=row.get("COND"),
                    treatment_code=row.get("TREATMENT_CODE"),
                    pcn=row.get("PCN"),
                    pavement_type_code=row.get("PAVEMENT_TYPE_CODE"),
                    subgrade_strength_code=row.get("SUBGRADE_STRENGTH_CODE"),
                    tire_pres_code=row.get("TIRE_PRES_CODE"),
                    dtrm_method_code=row.get("DTRM_METHOD_CODE"),
                    rwy_lgt_code=row.get("RWY_LGT_CODE"),
                    rwy_len_source=row.get("RWY_LEN_SOURCE"),
                    length_source_date=row.get("LENGTH_SOURCE_DATE"),
                    gross_wt_sw=row.get("GROSS_WT_SW"),
                    gross_wt_dw=row.get("GROSS_WT_DW"),
                    gross_wt_dtw=row.get("GROSS_WT_DTW"),
                    gross_wt_ddtw=row.get("GROSS_WT_DDTW"),
                )
                self.apt_rwy.append(record)

    def parse_apt_rwy_end(self) -> None:
        file_path = path.join(self.__dir_path, APT_RWY_END_FILE_NAME)
        if not check_file_exists(file_path):
            return
        with open_csv(file_path) as f:
            print(f"               Parsing {APT_RWY_END_FILE_NAME}")
            reader = csv.DictReader(f)

            for row in reader:
                record = APT_RWY_END(
                    eff_date=row.get("EFF_DATE"),
                    site_no=row.get("SITE_NO"),
                    site_type_code=row.get("SITE_TYPE_CODE"),
                    state_code=row.get("STATE_CODE"),
                    arpt_id=row.get("ARPT_ID"),
                    city=row.get("CITY"),
                    country_code=row.get("COUNTRY_CODE"),
                    rwy_id=row.get("RWY_ID"),
                    rwy_end_id=row.get("RWY_END_ID"),
                    true_alignment=row.get("TRUE_ALIGNMENT"),
                    ils_type=row.get("ILS_TYPE"),
                    right_hand_traffic_pat_flag=row.get("RIGHT_HAND_TRAFFIC_PAT_FLAG"),
                    rwy_marking_type_code=row.get("RWY_MARKING_TYPE_CODE"),
                    rwy_marking_cond=row.get("RWY_MARKING_COND"),
                    rwy_end_lat_deg=row.get("RWY_END_LAT_DEG"),
                    rwy_end_lat_min=row.get("RWY_END_LAT_MIN"),
                    rwy_end_lat_sec=row.get("RWY_END_LAT_SEC"),
                    rwy_end_lat_hemis=row.get("RWY_END_LAT_HEMIS"),
                    lat_decimal=row.get("LAT_DECIMAL"),
                    rwy_end_lon_deg=row.get("RWY_END_LONG_DEG"),
                    rwy_end_lon_min=row.get("RWY_END_LONG_MIN"),
                    rwy_end_lon_sec=row.get("RWY_END_LONG_SEC"),
                    rwy_end_lon_hemis=row.get("RWY_END_LONG_HEMIS"),
                    lon_decimal=row.get("LONG_DECIMAL"),
                    rwy_end_elev=row.get("RWY_END_ELEV"),
                    thr_crossing_hgt=row.get("THR_CROSSING_HGT"),
                    visual_glide_path_angle=row.get("VISUAL_GLIDE_PATH_ANGLE"),
                    displaced_thr_lat_deg=row.get("DISPLACED_THR_LAT_DEG"),
                    displaced_thr_lat_min=row.get("DISPLACED_THR_LAT_MIN"),
                    displaced_thr_lat_sec=row.get("DISPLACED_THR_LAT_SEC"),
                    displaced_thr_lat_hemis=row.get("DISPLACED_THR_LAT_HEMIS"),
                    lat_displaced_thr_decimal=row.get("LAT_DISPLACED_THR_DECIMAL"),
                    displaced_thr_lon_deg=row.get("DISPLACED_THR_LONG_DEG"),
                    displaced_thr_lon_min=row.get("DISPLACED_THR_LONG_MIN"),
                    displaced_thr_lon_sec=row.get("DISPLACED_THR_LONG_SEC"),
                    displaced_thr_lon_hemis=row.get("DISPLACED_THR_LONG_HEMIS"),
                    lon_displaced_thr_decimal=row.get("LONG_DISPLACED_THR_DECIMAL"),
                    displaced_thr_elev=row.get("DISPLACED_THR_ELEV"),
                    displaced_thr_len=row.get("DISPLACED_THR_LEN"),
                    tdz_elev=row.get("TDZ_ELEV"),
                    vgsi_code=row.get("VGSI_CODE"),
                    rwy_visual_range_equip_code=row.get("RWY_VISUAL_RANGE_EQUIP_CODE"),
                    rwy_vsby_value_equip_flag=row.get("RWY_VSBY_VALUE_EQUIP_FLAG"),
                    apch_lgt_system_code=row.get("APCH_LGT_SYSTEM_CODE"),
                    rwy_end_lgts_flag=row.get("RWY_END_LGTS_FLAG"),
                    cntrln_lgts_avbl_flag=row.get("CNTRLN_LGTS_AVBL_FLAG"),
                    tdz_lgt_avbl_flag=row.get("TDZ_LGT_AVBL_FLAG"),
                    obstn_type=row.get("OBSTN_TYPE"),
                    obstn_mrkd_code=row.get("OBSTN_MRKD_CODE"),
                    far_part_77_code=row.get("FAR_PART_77_CODE"),
                    obstn_clnc_slope=row.get("OBSTN_CLNC_SLOPE"),
                    obstn_hgt=row.get("OBSTN_HGT"),
                    dist_from_thr=row.get("DIST_FROM_THR"),
                    cntrln_offset=row.get("CNTRLN_OFFSET"),
                    cntrln_dir_code=row.get("CNTRLN_DIR_CODE"),
                    rwy_grad=row.get("RWY_GRAD"),
                    rwy_grad_direction=row.get("RWY_GRAD_DIRECTION"),
                    rwy_end_psn_source=row.get("RWY_END_PSN_SOURCE"),
                    rwy_end_psn_date=row.get("RWY_END_PSN_DATE"),
                    rwy_end_elev_source=row.get("RWY_END_ELEV_SOURCE"),
                    rwy_end_elev_date=row.get("RWY_END_ELEV_DATE"),
                    dspl_thr_psn_source=row.get("DSPL_THR_PSN_SOURCE"),
                    rwy_end_dspl_thr_psn_date=row.get("RWY_END_DSPL_THR_PSN_DATE"),
                    dspl_thr_elev_source=row.get("DSPL_THR_ELEV_SOURCE"),
                    rwy_end_dspl_thr_elev_date=row.get("RWY_END_DSPL_THR_ELEV_DATE"),
                    tdz_elev_source=row.get("TDZ_ELEV_SOURCE"),
                    rwy_end_tdz_elev_date=row.get("RWY_END_TDZ_ELEV_DATE"),
                    tkof_run_avbl=row.get("TKOF_RUN_AVBL"),
                    tkof_dist_avbl=row.get("TKOF_DIST_AVBL"),
                    aclt_stop_dist_avbl=row.get("ACLT_STOP_DIST_AVBL"),
                    lndg_dist_avbl=row.get("LNDG_DIST_AVBL"),
                    lahso_ald=row.get("LAHSO_ALD"),
                    rwy_end_intersect_lahso=row.get("RWY_END_INTERSECT_LAHSO"),
                    lahso_desc=row.get("LAHSO_DESC"),
                    lahso_lat=row.get("LAHSO_LAT"),
                    lat_lahso_decimal=row.get("LAT_LAHSO_DECIMAL"),
                    lahso_lon=row.get("LAHSO_LONG"),
                    lon_lahso_decimal=row.get("LONG_LAHSO_DECIMAL"),
                    lahso_psn_source=row.get("LAHSO_PSN_SOURCE"),
                    rwy_end_lahso_psn_date=row.get("RWY_END_LAHSO_PSN_DATE"),
                )
                self.apt_rwy_end.append(record)

    def to_dict(self) -> dict:
        return {
            **self.apt_ars_to_dict(),
            **self.apt_att_to_dict(),
            **self.apt_base_to_dict(),
            **self.apt_con_to_dict(),
            **self.apt_rmk_to_dict(),
            **self.apt_rwy_to_dict(),
            **self.apt_rwy_end_to_dict(),
        }

    def to_db(self, db_cursor: Cursor) -> None:
        self.apt_ars_to_db(db_cursor)
        self.apt_att_to_db(db_cursor)
        self.apt_base_to_db(db_cursor)
        self.apt_con_to_db(db_cursor)
        self.apt_rmk_to_db(db_cursor)
        self.apt_rwy_to_db(db_cursor)
        self.apt_rwy_end_to_db(db_cursor)

    def apt_ars_to_dict(self) -> dict:
        return {"apt_ars": [item.to_dict() for item in self.apt_ars]}

    def apt_att_to_dict(self) -> dict:
        return {"apt_att": [item.to_dict() for item in self.apt_att]}

    def apt_base_to_dict(self) -> dict:
        return {"apt_base": [item.to_dict() for item in self.apt_base]}

    def apt_con_to_dict(self) -> dict:
        return {"apt_con": [item.to_dict() for item in self.apt_con]}

    def apt_rmk_to_dict(self) -> dict:
        return {"apt_rmk": [item.to_dict() for item in self.apt_rmk]}

    def apt_rwy_to_dict(self) -> dict:
        return {"apt_rwy": [item.to_dict() for item in self.apt_rwy]}

    def apt_rwy_end_to_dict(self) -> dict:
        return {"apt_rwy_end": [item.to_dict() for item in self.apt_rwy_end]}

    def apt_ars_to_db(self, db_cursor: Cursor) -> None:
        if len(self.apt_ars) > 0:
            print(f"               Processing {APT_ARS_FILE_NAME}")
            process_table(db_cursor, self.apt_ars)

    def apt_att_to_db(self, db_cursor: Cursor) -> None:
        if len(self.apt_att) > 0:
            print(f"               Processing {APT_ATT_FILE_NAME}")
            process_table(db_cursor, self.apt_att)

    def apt_base_to_db(self, db_cursor: Cursor) -> None:
        if len(self.apt_base) > 0:
            print(f"               Processing {APT_BASE_FILE_NAME}")
            process_table(db_cursor, self.apt_base)

    def apt_con_to_db(self, db_cursor: Cursor) -> None:
        if len(self.apt_con) > 0:
            print(f"               Processing {APT_CON_FILE_NAME}")
            process_table(db_cursor, self.apt_con)

    def apt_rmk_to_db(self, db_cursor: Cursor) -> None:
        if len(self.apt_rmk) > 0:
            print(f"               Processing {APT_RMK_FILE_NAME}")
            process_table(db_cursor, self.apt_rmk)

    def apt_rwy_to_db(self, db_cursor: Cursor) -> None:
        if len(self.apt_rwy) > 0:
            print(f"               Processing {APT_RWY_FILE_NAME}")
            process_table(db_cursor, self.apt_rwy)

    def apt_rwy_end_to_db(self, db_cursor: Cursor) -> None:
        if len(self.apt_rwy_end) > 0:
            print(f"               Processing {APT_RWY_END_FILE_NAME}")
            process_table(db_cursor, self.apt_rwy_end)
