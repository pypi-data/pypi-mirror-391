import re
import pandas as pd
from typing import (
    Any,
    List,
    Dict,
    Tuple,
    Union,
    Optional
)
from dataclasses import dataclass
from collections import defaultdict
from vdutils.library.data import (
    SGG_SPLIT_LIST,
    LAST_NM_REFINE_MAP,
    LOAD_PATTERN_FOR_SLICE,
    JIBUN_PATTERN_FOR_SLICE,
    ETC_LAND_PATTERN_FOR_SPLIT
)
from vdutils.library import Log
from vdutils.data import (
    __sep__,
    __index__,
    __encoding__,
    _get_folder_names
)
from vdutils.convaddr import ConvAddr
from vdutils.resources import resource_filename


@dataclass
class GenPnu():


    def __init__(
        self,
        base_dt: Optional[str] = None
    ):

        if base_dt is not None:
            if not isinstance(base_dt, str):
                raise TypeError("type of object('base_dt') must be string")

            if not base_dt.isdigit():
                raise ValueError("object('base_dt') should be a string consisting of numbers")

            if len(base_dt) != 8:
                raise ValueError("object('base_dt') should be a string consisting of exactly 8(YYYYMMDD) digits")
        else: pass

        self.sep = __sep__
        self.index: bool = __index__
        self.encoding: str = __encoding__
        self.origin_base_dt: str = base_dt
        self.base_dt: Optional[str] = base_dt
        self.bjd_current_df: pd.DataFrame() = None
        self.bjd_current_nm_cd_dic = defaultdict(list)
        self.bjd_dic: Dict[str, Dict[str, str]] = {}
        self.bjd_nm_change_dic: Dict[str, str] = {
            "시도명": "sido_nm",
            "시군구명": "sgg_nm",
            "읍면동명": "emd_nm",
            "리명": "ri_nm",
        }
        self.logger = Log('GeneratePnu').stream_handler("INFO")
        self._get_base_dt()
        self._get_file_names()
        self._prepare()
        self.base_dt_print: str = f"{self.base_dt[:4]}-{self.base_dt[4:6]}-{self.base_dt[6:8]}"
        self.base_folder_path = resource_filename(
            "vdutils", 
            "data/bjd"
        )


    def _find_latest_base_dt(
        self,
        base_dts: List[str]
    ) -> str:

        """
        입력된 날짜(YYYYMMDD)와 법정동 데이터 시점 리스트와 비교하여 입력된 날짜보다 과거 시점 중 최신 시점을 반환
        """

        for date in base_dts:
            if date < self.base_dt:
                return date

        # 입력된 날짜보다 작은 날짜가 없을 경우
        self.logger.info("입력된 날짜보다 이전 시점의 법정동 데이터가 존재하지 않습니다. 보유한 데이터중 최신 데이터를 적용합니다.")
        return base_dts[0]


    def _get_base_dt(self):

        """
        입력된 날짜(YYYYMMDD)와 법정동 데이터 시점 리스트와 비교하여 입력된 날짜보다 과거 시점 중 최신 시점을 반환 \n
        입력된 날짜(YYYYMMDD)가 없으면 데이터 시점 리스트 중 최신 시점을 반환
        """

        base_dts = _get_folder_names(library_name="vdutils", base_folder_path="data/bjd")
        base_dts = sorted(base_dts, reverse=True)
        try:
            if self.base_dt is None:
                self.base_dt = base_dts[0]
            else:
                self.base_dt = self._find_latest_base_dt(base_dts=base_dts)
        finally:
            self.logger.info(f"[GenPnu] 적용 법정동 데이터 시점: {self.base_dt}")


    def _get_file_names(self):
        self.file_name_bjd_current = resource_filename(
            "vdutils", 
            f"data/bjd/{self.base_dt}/bjd_current.txt"
        )


    def _get_bjd_current_df(
        self,
        file_name_bjd_current,
        input_encoding,
        input_index,
        input_sep
    ):
        try:
            self.bjd_current_df: pd.DataFrame = pd.read_csv(
                file_name_bjd_current,
                sep=input_sep,
                engine='python',
                encoding=input_encoding,
                dtype={
                    '과거법정동코드': str,
                    '법정동코드': str
                }
            )
        except Exception as e:
            self.logger.error(f"Failed to read {file_name_bjd_current}")
            self.logger.error(e)


    def _create_bjd_current_nm_cd_dic(self):
        try:
            for idx, row in self.bjd_current_df.iterrows():
                bjd_nms = []
                for bjd_nm in ["시도명", "시군구명", "읍면동명", "리명"]:
                    if not pd.isna(row[bjd_nm]):
                        bjd_nms.append(row[bjd_nm])
                bjd_nms = " ".join(bjd_nms)
                self.bjd_current_nm_cd_dic[bjd_nms].append(
                    {
                        "bjd_cd": row["법정동코드"], 
                        "deleted_dt": None if pd.isna(row["삭제일자"]) else row["삭제일자"]
                    }
                )
        except Exception as e:
            self.logger.error(f"Failed to create bjd_current_nm_cd_dic")
            self.logger.error(e)


    def _create_bjd_dic(self):
        try:
            for idx, row in self.bjd_current_df.iterrows():
                bjd_cd: str = row["법정동코드"]
                full_bjd_nm: str = row["법정동명"]
                created_dt: str = row["생성일자"]
                deleted_dt: str = row["삭제일자"]
                bjd_datas: Dict[str, str] = {}
                for bjd_nm in ["시도명", "시군구명", "읍면동명", "리명"]:
                    if not pd.isna(row[bjd_nm]):
                        bjd_datas[self.bjd_nm_change_dic[bjd_nm]] = row[bjd_nm]
                    else:
                        bjd_datas[self.bjd_nm_change_dic[bjd_nm]] = None
                bjd_datas["full_bjd_nm"] = full_bjd_nm
                bjd_datas["created_dt"] = created_dt
                bjd_datas["deleted_dt"] = None if pd.isna(deleted_dt) else deleted_dt
                self.bjd_dic[bjd_cd] = bjd_datas
        except Exception as e:
            self.logger.error(f"Failed to create bjd_dic")
            self.logger.error(e)


    def _import_convaddr(self):
        try:
            self.convaddr = ConvAddr(base_dt=self.origin_base_dt)
            self.bjd_smallest_list = self.convaddr.bjd_smallest_list
            self.convert_pnu_dic = dict((bjd_nm, bjd_cd) for bjd_cd, bjd_nm in self.convaddr.bjd_current_dic.items() if bjd_cd != "법정동코드")
        except Exception as e:
            self.logger.error(f"Failed to import vdutils.convaddr module")
            self.logger.error(e)


    def _prepare(self):
        self._get_bjd_current_df(
            file_name_bjd_current=self.file_name_bjd_current,
            input_encoding=self.encoding,
            input_index=self.index,
            input_sep=self.sep,
        )
        self._create_bjd_current_nm_cd_dic()
        self._create_bjd_dic()
        self._import_convaddr()


    def get_bjd_cd(
        self,
        bjd_nm: str,
    ) -> Dict[str, Any]:

        """
        입력된 문자열(한글 법정동명)의 법정동 코드를 반환

        Args:
            bjd_nm (str): The input should be a string consisting of Korean administrative district names.

        Raises:
            TypeError: If the 'bjd_nm' object is not of type string.
            ValueError: If the 'bjd_nm' object is not consist of only Korean characters and numbers.

        Returns:
            Dict[str, Any]: 
                "error": bool,
                "bjd_cd": Optional[str],
                "deleted_dt": Optional[str],
                "base_dt": str,
                "msg": str
        """

        if not isinstance(bjd_nm, str):
            raise TypeError("type of object('bjd_nm') must be string")

        # 한자 표기가 포함된 괄호도 허용하도록 정규식 수정
        # 한자 범위: \u4e00-\u9fff (CJK Unified Ideographs)
        # if not re.match("^[가-힣0-9]+$", bjd_nm):
        if not re.match("^[가-힣0-9 ()\u4e00-\u9fff]+$", bjd_nm): # NOTE 한자 표기 괄호 허용
            raise ValueError("object('bjd_nm') should consist of only Korean characters, numbers, and Chinese characters in parentheses")

        not_a_valid_district_response: Dict[str, Any] = {
            "error": True,
            "bjd_cd": None, 
            "deleted_dt": None,
            "base_dt": self.base_dt_print,
            "msg": f"'{bjd_nm}' is not a valid legal district name"
        }
        try:
            bjd_nm = " ".join(bjd_nm.split())

            if bjd_nm in self.bjd_current_nm_cd_dic:
                bjd_cd_list = self.bjd_current_nm_cd_dic[bjd_nm]
                if len(bjd_cd_list) > 1:
                    bjd_cd = list(
                        filter(
                            lambda bjd_cd_data: not bjd_cd_data["deleted_dt"], bjd_cd_list
                        )
                    )[0]
                else:
                    bjd_cd = bjd_cd_list[0]

                return {
                    "error": False,
                    **bjd_cd, 
                    "base_dt": self.base_dt_print,
                    "msg": ""
                }

            else:
                if len(bjd_nm.split()) == 1:
                    return not_a_valid_district_response
                else:
                    sgg = bjd_nm.split()[1]
                    if sgg in SGG_SPLIT_LIST:
                        sgg_split_nm = f"{sgg[:2]}시 {sgg[2:]}"
                        bjd_nm = bjd_nm.replace(sgg, sgg_split_nm)
                        return self.get_bjd_cd(bjd_nm)

                    last_nm = bjd_nm.split()[-1]
                    if last_nm in LAST_NM_REFINE_MAP:
                        bjd_nm = bjd_nm.replace(last_nm, LAST_NM_REFINE_MAP[last_nm])
                        return self.get_bjd_cd(bjd_nm)

            return not_a_valid_district_response

        except:
            return not_a_valid_district_response


    def get_bjd_data(
        self,
        bjd_cd: str
    ) -> Dict[str, Any]:

        """
        입력된 문자열(숫자 10자리의 법정동코드)의 법정동 데이터(각 단위 법정동명, 생성일자, 삭제일자)를 반환

        Args:
            bjd_cd (str): The Korean district code string consisting of exactly 10 digits.

        Raises:
            TypeError: If the 'bjd_cd' object is not of type string.
            ValueError: If the 'bjd_cd' object does not consist of digits only.
            ValueError: If the 'bjd_cd' object does not consist of exactly 10 digits.

        Returns:
            Dict[str, Any]: {
                "error": bool,
                "sido_nm": Optional[str],
                "sgg_nm": Optional[str],
                "emd_nm": Optional[str],
                "ri_nm": Optional[str],
                "full_bjd_nm": Optional[str],
                "created_dt": Optional[str],
                "deleted_dt": Optional[str],
                "base_dt": str,
                "msg": str
            }
        """

        if not isinstance(bjd_cd, str):
            raise TypeError("type of object('bjd_cd') must be string")

        if not bjd_cd.isdigit():
            raise ValueError("object('bjd_cd') should be a string consisting of numbers")

        if len(bjd_cd) != 10:
            raise ValueError("object('bjd_cd') should be a string consisting of exactly 10 digits")

        not_a_valid_district_response: Dict[str, Any] = {
            "error": True,
            "sido_nm": None,
            "sgg_nm": None,
            "emd_nm": None,
            "ri_nm": None,
            "full_bjd_nm": None,
            "created_dt": None,
            "deleted_dt": None,
            "base_dt": self.base_dt_print,
            "msg": f"'{bjd_cd}' is not a valid legal district code"
        }
        try:
            if bjd_cd in self.bjd_dic:
                return {"error": False, **self.bjd_dic[bjd_cd], "base_dt": self.base_dt_print, "msg": ""}
            else:
                return not_a_valid_district_response
        except Exception as e:
            return {**not_a_valid_district_response, "msg": str(e)}


    @staticmethod
    def _validate_jibun(
        jibun: Optional[str]
    ) -> bool:

        """
        입력된 지번 문자열이 올바른 형식인지 정규식을 이용하여 검증하여 반환 \n
        단, 블록지번를 의미하는 음절이 포함되거나 '*' 가 포함될 경우 예외 적용하여 True 를 리턴

        Args:
            jibun (str): Validates the format of the given address.
                The address should include '산' and only contain digits except for '산' and '-'.
                The main and sub numbers should be separated by a hyphen, and both can have a maximum of 4 digits.
                Examples: 
                    With mountain and sub-number: 산 0000-0000
                    With mountain and no sub-number: 산 0000
                    Without mountain and with sub-number: 0000-0000
                    Without mountain and without sub-number: 0000

        Raises:
            ValueError: If the 'jibun' object is not of the specified format.

        Returns:
            dict: Validation result containing 'error' (bool) and 'msg' (str).
        """

        msg = "Invalid 'jibun' format. Please follow the specified format."
        """
        Invalid 'jibun' format. Please follow the specified format.

        The address should include '산' and only contain digits except for '산' and '-'.
        The main and sub numbers should be separated by a hyphen, and both can have a maximum of 4 digits.
        Examples:
            With mountain and sub-number: 산 0000-0000
            With mountain and no sub-number: 산 0000
            Without mountain and with sub-number: 0000-0000
            Without mountain and without sub-number: 0000
        """

        if pd.isna(jibun) \
        or jibun == ""  \
        or jibun is None  \
        or jibun[0] in ["B", "가", "지"]:
            return {"error": True, "msg": msg}
        if "*" in jibun:
            return {"error": True, "msg": msg}

        jibun = jibun.replace(" ", "")
        pattern = re.compile(r'^(산\s*)?\d{1,4}-\d{1,4}$|^(산\s*)?\d{1,4}$|^\d{1,4}-\d{1,4}$|^\d{1,4}$')

        if not bool(pattern.match(jibun)):
            return {"error": True, "msg": msg}

        return {"error": False, "msg": ""}


    @staticmethod
    def _get_mountain_cd(
        jibun: str
    ) -> Tuple[str, str]:

        """
        입력된 지번 문자열(지번 문자열 적합성 확인된 입력값)에서 '산' 여부 판단하여 산코드를 반환
        """

        if jibun[0] in ["산"]:
            mountain_cd = "2"
            jibun = jibun.replace("산", "")

        else:
            mountain_cd = "1"

        return jibun, mountain_cd


    @staticmethod
    def _get_jibun_datas(
        jibun: str
    ) -> Tuple[str, str, str]:

        """
        입력된 지번 문자열(지번 문자열 적합성 확인된 입력값)에서 본번과 부번을 분리하여 번, 지 코드를 반환
        """

        jibun_split = jibun.split("-")

        if len(jibun_split) == 2:
            bun, ji = [int(num) for num in jibun_split]
            bunji_cd = "%04d%04d" % (bun, ji)
            bun = str(bun)
            ji = str(ji)

        elif len(jibun_split) == 1:
            bun = int(jibun)
            bunji_cd = "%04d0000" % (bun)
            bun = str(bun)
            ji = "0"

        else:
            bunji_cd = "00000000"
            bun, ji = "0", "0"

        return bunji_cd, bun, ji


    @staticmethod
    def _validate_pnu(
        pnu: Optional[str]
    ) -> dict:
        """
        입력된 PNU 문자열이 올바른 형식인지 정규식을 이용하여 검증하여 반환

        Args:
            pnu (str): Validates the format of the given PNU.
                The PNU must be a 19-character string consisting only of digits.

        Raises:
            ValueError: If the 'pnu' object is not of the specified format.

        Returns:
            dict: Validation result containing 'error' (bool) and 'msg' (str).
        """

        msg = "Invalid 'pnu' format. Please follow the specified format."
        """
        Invalid 'pnu' format. Please follow the specified format.

        The PNU must be a 19-character string consisting only of digits.
        Example:
            1234567890123456789
        """

        if not pnu or not isinstance(pnu, str):
            return {"error": True, "msg": msg}

        pattern = re.compile(r'^\d{19}$')
        if not pattern.match(pnu):
            return {"error": True, "msg": msg}

        return {"error": False, "msg": ""}


    def _create_generate_pnu_result(
        self,
        error=True, 
        pnu=None,
        bjd_cd=None,
        mountain_cd=None,
        bunji_cd=None, 
        bjd_datas=None,
        bun=None,
        ji=None,
        msg=""
    ) -> Dict[str, Any]:

        """
        결과 딕셔너리를 생성하는 유틸리티 함수

        Returns:
            Dict[str, Any]: {
                "error": bool,
                "pnu": Optional[str],
                "bjd_cd": Optional[str],
                "mountain_cd": Optional[str],
                "bunji_cd": Optional[str],
                "bjd_datas": {
                    "error": bool,
                    "sido_nm": Optional[str],
                    "sgg_nm": Optional[str],
                    "emd_nm": Optional[str],
                    "ri_nm": Optional[str],
                    "full_bjd_nm": Optional[str],
                    "created_dt": Optional[str],
                    "deleted_dt": Optional[str],
                    "base_dt": str,
                    "msg": str,
                },
                "bun": Optional[str],
                "ji": Optional[str],
                "base_dt": str,
                "msg": str
            }
        """

        return {
            "error": error,
            "pnu": pnu,
            "bjd_cd": bjd_cd,
            "mountain_cd": mountain_cd,
            "bunji_cd": bunji_cd,
            "bjd_datas": bjd_datas or {
                "error": True,
                "sido_nm": None,
                "sgg_nm": None,
                "emd_nm": None,
                "ri_nm": None,
                "full_bjd_nm": None,
                "created_dt": None,
                "deleted_dt": None,
                "base_dt": self.base_dt_print,
                "msg": ""
            },
            "bun": bun,
            "ji": ji,
            "base_dt": self.base_dt_print,
            "msg": msg
        }


    def generate_pnu(
        self,
        bjd_cd: str,
        jibun: str # '산'을 포함한 지번
    ) -> Dict[str, Any]:

        """
        입력된 문자열(법정동 코드, 지번)을 필지관리번호(pnu)로 변환하여 반환

        Args:
            bjd_cd (str): The Korean district code string consisting of exactly 10 digits.
            jibun (str): Validates the format of the given address.
                The address should include '산' and only contain digits except for '산' and '-'.
                The main and sub numbers should be separated by a hyphen, and both can have a maximum of 4 digits.
                Examples:
                    With mountain and sub-number: 산 0000-0000
                    With mountain and no sub-number: 산 0000
                    Without mountain and with sub-number: 0000-0000
                    Without mountain and without sub-number: 0000

        Raises:
            TypeError: If the 'bjd_cd' object is not of type string.
            TypeError: If the 'jibun' object is not of type string.
            ValueError: If the 'bjd_cd' object does not consist of digits only.
            ValueError: If the 'bjd_cd' object does not consist of exactly 10 digits.

        Returns:
            Dict[str, Any]: {
                "error": bool,
                "pnu": Optional[str],
                "bjd_cd": Optional[str],
                "mountain_cd": Optional[str],
                "bunji_cd": Optional[str],
                "bjd_datas": {
                    "error": bool,
                    "sido_nm": Optional[str],
                    "sgg_nm": Optional[str],
                    "emd_nm": Optional[str],
                    "ri_nm": Optional[str],
                    "full_bjd_nm": Optional[str],
                    "created_dt": Optional[str],
                    "deleted_dt": Optional[str],
                    "base_dt": str,
                    "msg": str,
                },
                "bun": Optional[str],
                "ji": Optional[str],
                "base_dt": str,
                "msg": str
            }
        """

        if not isinstance(bjd_cd, str):
            raise TypeError("type of object('bjd_cd') must be string")

        if not isinstance(jibun, str):
            raise TypeError("type of object('jibun') must be string")

        if not bjd_cd.isdigit():
            raise ValueError("object('bjd_cd') should be a string consisting of numbers")

        if len(bjd_cd) != 10:
            raise ValueError("object('bjd_cd') should be a string consisting of exactly 10 digits")

        is_valid_jibun = self._validate_jibun(jibun)
        if is_valid_jibun.get("error") is True:
            return self._create_generate_pnu_result(
                error=True,
                msg=is_valid_jibun.get("msg")
            )

        try:
            bjd_datas = self.get_bjd_data(bjd_cd)
            if bjd_datas.get("error") is True:
                return self._create_generate_pnu_result(
                    error=True,
                    bjd_datas=bjd_datas,
                    msg=bjd_datas.get("msg")
                )

            else:
                jibun = jibun.replace(" ", "")
                jibun, mountain_cd = self._get_mountain_cd(jibun)
                bunji_cd, bun, ji = self._get_jibun_datas(jibun)
                is_valid_pnu = self._validate_pnu(f"{bjd_cd}{mountain_cd}{bunji_cd}")

                if is_valid_pnu.get("error") is True:
                    return self._create_generate_pnu_result(
                        error=True,
                        pnu=f"{bjd_cd}{mountain_cd}{bunji_cd}",
                        bjd_cd=bjd_cd,
                        mountain_cd=mountain_cd,
                        bunji_cd=bunji_cd,
                        bjd_datas=bjd_datas,
                        bun=bun,
                        ji=ji,
                        msg=is_valid_pnu.get("msg")
                    )

                else:
                    return self._create_generate_pnu_result(
                        error=False,
                        pnu=f"{bjd_cd}{mountain_cd}{bunji_cd}",
                        bjd_cd=bjd_cd,
                        mountain_cd=mountain_cd,
                        bunji_cd=bunji_cd,
                        bjd_datas=bjd_datas,
                        bun=bun,
                        ji=ji,
                        msg=""
                    )

        except Exception as e:
            self._create_generate_pnu_result(
                error=True,
                msg=str(e)
            )


    def generate_pnu_from_bjd_nm(
        self,
        bjd_nm: str,
        jibun: str # '산'을 포함한 지번
    ) -> Dict[str, Any]:

        """
        입력된 문자열(법정동명, 지번)을 필지관리번호(pnu)로 변환하여 반환

        Args:
            bjd_nm (str): The input should be a string consisting of Korean administrative district names.
            jibun (str): Validates the format of the given address.
                The address should include '산' and only contain digits except for '산' and '-'.
                The main and sub numbers should be separated by a hyphen, and both can have a maximum of 4 digits.
                Examples:
                    With mountain and sub-number: 산 0000-0000
                    With mountain and no sub-number: 산 0000
                    Without mountain and with sub-number: 0000-0000
                    Without mountain and without sub-number: 0000

        Raises:
            TypeError: If the 'bjd_nm' object is not of type string.
            TypeError: If the 'jibun' object is not of type string.
            ValueError: If the 'bjd_nm' object is not consist of only Korean characters and numbers.

        Returns:
            Dict[str, Any]: {
                "error": bool,
                "pnu": Optional[str],
                "bjd_cd": Optional[str],
                "mountain_cd": Optional[str],
                "bunji_cd": Optional[str],
                "bjd_datas": {
                    "error": bool,
                    "sido_nm": Optional[str],
                    "sgg_nm": Optional[str],
                    "emd_nm": Optional[str],
                    "ri_nm": Optional[str],
                    "full_bjd_nm": Optional[str],
                    "created_dt": Optional[str],
                    "deleted_dt": Optional[str],
                    "base_dt": str,
                    "msg": str,
                },
                "bun": Optional[str],
                "ji": Optional[str],
                "base_dt": str,
                "msg": str
            }
        """

        if not isinstance(bjd_nm, str):
            raise TypeError("type of object('bjd_nm') must be string")

        if not isinstance(jibun, str):
            raise TypeError("type of object('jibun') must be string")

        # 한자 표기가 포함된 괄호도 허용하도록 정규식 수정
        # 한자 범위: \u4e00-\u9fff (CJK Unified Ideographs)
        # if not re.match("^[가-힣0-9]+$", bjd_nm):
        if not re.match("^[가-힣0-9 ()\u4e00-\u9fff]+$", bjd_nm):
            raise ValueError("object('bjd_nm') should consist of only Korean characters, numbers, and Chinese characters in parentheses")

        try:
            res = self.get_bjd_cd(bjd_nm=bjd_nm)
            if res.get("error") is True:
                return self._create_generate_pnu_result(
                    error=res.get("error"),
                    msg=res.get("msg")
                )
            else:
                return self.generate_pnu(
                    bjd_cd=res.get("bjd_cd"),
                    jibun=jibun
                )
        except Exception as e:
            return self._create_generate_pnu_result(
                error=True,
                msg=str(e)
            )


    def _clean_bracket_and_content(
        self,
        string: str
    ) -> str:

        """
        주소문자열의 ([]) 와 같은 괄호 및 괄호안 문자 제거하는 기능
        """

        pattern = r'[\(\[].*?[\)\]]'
        return re.sub(pattern, '', string).rstrip()


    def _split_etc_main_address(
        self,
        main_address: str,
        detail_address: str
    ) -> Tuple[Optional[str], Optional[str]]:

        """
        주소문자열에서 주(main) 주소, 주 외(main etc) 주소, 상세(detail) 주소를 추출하여 반환
        """

        not_a_valid_district_response: Dict[str, Any] = {
            "error": True,
            "main_address": None, 
            "etc_main_address": None,
            "detail_address": None,
            "base_dt": self.base_dt_print,
            "msg": f"'{detail_address}' is failed to split main address and main etc address"
        }
        try:
            if re.sub(ETC_LAND_PATTERN_FOR_SPLIT, "", detail_address):
                clean_detail_address = re.sub(ETC_LAND_PATTERN_FOR_SPLIT, "", detail_address).strip()
                etc_main_address = detail_address.replace(clean_detail_address, "")
                return {
                    "error": False,
                    "main_address": main_address,
                    "etc_main_address": etc_main_address,
                    "detail_address": clean_detail_address,
                    "base_dt": self.base_dt_print,
                    "msg": ""
                }
            else:
                return {
                    "error": False,
                    "main_address": main_address,
                    "etc_main_address": None,
                    "detail_address": detail_address,
                    "base_dt": self.base_dt_print,
                    "msg": ""
                }
        except Exception as e:
            return {**not_a_valid_district_response, "msg": str(e)}


    def _split_main_and_detail_address(
        self,
        address: str
    ) -> Dict[str, Any]:

        """
        주소문자열에서 주(main) 주소, 주 외(main etc) 주소, 상세(detail) 주소를 추출하여 반환
        """

        not_a_valid_district_response: Dict[str, Any] = {
            "error": True,
            "main_address": None, 
            "etc_main_address": None,
            "detail_address": None,
            "base_dt": self.base_dt_print,
            "msg": f"'{address}' is failed to split main address and detail address"
        }
        try:
            cleaned_address = self._clean_bracket_and_content(string=address)
            match = re.search(LOAD_PATTERN_FOR_SLICE, cleaned_address)
            if match:
                return {**not_a_valid_district_response, "msg": f"'{address}' is load address"}

            match = re.search(JIBUN_PATTERN_FOR_SLICE, cleaned_address)
            if match:
                detail_address = address.split(match.group(0))[1].strip()
                main_address = address.replace(detail_address, "").strip()
                return self._split_etc_main_address(main_address=main_address, detail_address=detail_address)
            else:
                return not_a_valid_district_response
        except Exception as e:
            return {**not_a_valid_district_response, "msg": str(e)}


    def _is_not_in_smallest_bjd(
        self,
        rest_main_address: str
    ) -> bool:

        """
        입력된 지번 문자열(법정동명이 제외된 지번 문자열)에서 최소단위 법정동이 포함되어 있는지 확인하여 반환
        """

        try:
            check_word = rest_main_address.split()[0]
        except:
            check_word = rest_main_address
        for bjd in self.bjd_smallest_list:
            if check_word == bjd:
                return False
        return True


    def _extract_bjd_from_address(
        self,
        main_address: str
    ) -> Union[str, None]:

        """
        입력된 지번 문자열에서 번지 상세주소가 제외된 지번의 법정동 문자열을 추출하여 반환
        법정동 딕셔너리에서 입력된 지번 문자열내에 존재하는 법정동이 있는지 조회하고 존재할 경우,
        입력된 지번 문자열에서 매칭된 법정동을 잘라낸 나머지 문자열에 최소 단위 법정동명이 존재하는지 확인해서 최소 단위 법정동 레벨인지를 확인
        매칭된 법정동이 최소 단위 법정동이면 반환

        Args:
            addr (str): The input korean address string.

        Raises:
            TypeError: If the 'address' object is not of type string.

        Returns:
            Union[str, None]
        """

        if not isinstance(main_address, str):
            raise TypeError("type of object('address') must be string")

        try:
            for key in self.convert_pnu_dic.keys():
                if key in main_address and self.convert_pnu_dic[key][5:] != '00000':
                    rest_main_address = main_address.replace(key, '')
                    if main_address.split(key)[1][0] == ' ' \
                    and self._is_not_in_smallest_bjd(rest_main_address=rest_main_address):
                        return key
            return None

        except Exception as e:
            return None


    def generate_pnu_from_address(
        self,
        address: str,
    ) -> Dict[str, Any]:

        """
        입력된 문자열(주소)에서 법정동, 지번을 분리 필지관리번호(pnu)로 변환하여 반환

        Args:
            bjd_nm (str): The input should be a string consisting of Korean administrative district names.
            jibun (str): Validates the format of the given address.
                The address should include '산' and only contain digits except for '산' and '-'.
                The main and sub numbers should be separated by a hyphen, and both can have a maximum of 4 digits.
                Examples:
                    With mountain and sub-number: 산 0000-0000
                    With mountain and no sub-number: 산 0000
                    Without mountain and with sub-number: 0000-0000
                    Without mountain and without sub-number: 0000

        Raises:
            TypeError: If the 'bjd_nm' object is not of type string.
            TypeError: If the 'jibun' object is not of type string.
            ValueError: If the 'bjd_nm' object is not consist of only Korean characters and numbers.

        Returns:
            Dict[str, Any]: {
                "error": bool,
                "pnu": Optional[str],
                "bjd_cd": Optional[str],
                "mountain_cd": Optional[str],
                "bunji_cd": Optional[str],
                "bjd_datas": {
                    "error": bool,
                    "sido_nm": Optional[str],
                    "sgg_nm": Optional[str],
                    "emd_nm": Optional[str],
                    "ri_nm": Optional[str],
                    "full_bjd_nm": Optional[str],
                    "created_dt": Optional[str],
                    "deleted_dt": Optional[str],
                    "base_dt": str,
                    "msg": str,
                },
                "bun": Optional[str],
                "ji": Optional[str],
                "base_dt": str,
                "msg": str
            }
        """

        if not isinstance(address, str):
            raise TypeError("type of object('address') must be string")

        try:
            is_split_address = self._split_main_and_detail_address(address=address)
            if is_split_address.get("error") is True:
                return self._create_generate_pnu_result(
                    error=is_split_address.get("error"),
                    msg=is_split_address.get("msg")
                )

            else:
                main_address = is_split_address.get("main_address")
                bjd_nm = self._extract_bjd_from_address(main_address=main_address)
                if bjd_nm is None:
                    return self._create_generate_pnu_result(
                        error=True,
                        msg=f"Failed to extract bjd name from address: {address}"
                    )

                bjd_nm = bjd_nm.strip()
                jibun = main_address.replace(bjd_nm, "")
                if jibun is None: 
                    return self._create_generate_pnu_result(
                        error=True,
                        msg=f"Failed to extract valid jibun from address: {address}"
                    )

                jibun = jibun.strip()
                return self.generate_pnu_from_bjd_nm(bjd_nm=bjd_nm, jibun=jibun)

        except Exception as e:
            return self._create_generate_pnu_result(
                error=True,
                msg=str(e)
            )
