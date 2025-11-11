import re
import pandas as pd
from typing import (
    List,
    Dict,
    Optional
)
from dataclasses import dataclass
from vdutils.resources import resource_filename
from vdutils.library import Log
from vdutils.library.data import ETC_LAND_PATTERN
from vdutils.data import (
    __sep__,
    __index__,
    __encoding__,
    _get_folder_names
)


@dataclass
class ConvAddr():


    def __init__(
        self,
        base_dt: Optional[str] = None,
        is_inherit: bool = False
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
        self.index = __index__
        self.encoding = __encoding__
        self.base_dt: str = base_dt
        self.is_inherit: bool = is_inherit
        self.bjd_current_dic: Dict[str, str] = None
        self.bjd_smallest_list: List[str] = None
        self.bjd_current_bjd_nm_list: List[str] = None
        self.multiple_word_sgg_list: List[str] = None
        self.current_sido_sgg_list: List[str] = None
        self.current_sido_list: List[str] = None
        self.current_sgg_list: List[str] = None
        self.current_emd_list: List[str] = None
        self.current_ri_list: List[str] = None
        self.bjd_changed_dic: Dict[str, str] = None
        self.bjd_changed_old_bjd_nm_list: List[str] = None
        self.logger = Log('ConvertAddress').stream_handler("INFO")
        self._get_base_dt()
        self._get_file_names()
        self._prepare()
        self.base_dt_print: str = f"{self.base_dt[:4]}-{self.base_dt[4:6]}-{self.base_dt[6:8]}"


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

        if self.is_inherit:
            return self.base_dt

        base_dts = _get_folder_names(library_name="vdutils", base_folder_path="data/bjd")
        base_dts = sorted(base_dts, reverse=True)
        try:
            if self.base_dt is None:
                self.base_dt = base_dts[0]
            else:
                self.base_dt = self._find_latest_base_dt(base_dts=base_dts)
        finally:
            self.logger.info(f"[ConvAddr] 적용 법정동 데이터 시점: {self.base_dt}")


    def _get_file_names(self):
        self.file_name_bjd = resource_filename(
            "vdutils", 
            f"data/bjd/{self.base_dt}/bjd.txt"
        )
        self.file_name_bjd_current = resource_filename(
            "vdutils", 
            f"data/bjd/{self.base_dt}/bjd_current.txt"
        )
        self.file_name_bjd_changed = resource_filename(
            "vdutils", 
            f"data/bjd/{self.base_dt}/bjd_changed.txt"
        )
        self.file_name_bjd_smallest = resource_filename(
            "vdutils", 
            f"data/bjd/{self.base_dt}/bjd_smallest.txt"
        )
        self.file_name_bjd_frequency_dictionary = resource_filename(
            "vdutils", 
            f"data/bjd/{self.base_dt}/bjd_frequency_dictionary.txt"
        )
        self.file_name_multiple_word_sgg_list = resource_filename(
            "vdutils", 
            f"data/bjd/{self.base_dt}/multiple_word_sgg_list.txt"
        )


    @staticmethod
    def _concat_sido_sgg(
        sido_nm: Optional[str],
        sgg_nm: Optional[str]
    ):
        if sido_nm is not None and sgg_nm is not None:
            return f'{sido_nm} {sgg_nm}'
        elif sido_nm is not None and sgg_nm is None:
            return sido_nm
        else:
            return None


    def _create_bjd_changed_dictionary(
        self,
        bjd_changed_df: pd.DataFrame
    ):
        bjd_changed_dictionary: Dict[str, str] = dict()
        for old_bjd_cd, old_bjd_nm, new_bjd_nm in zip(
            bjd_changed_df['법정동코드_변경전'],
            bjd_changed_df['법정동명_변경전'],
            bjd_changed_df['법정동명_변경후']
        ):
            if old_bjd_nm is not None \
            and new_bjd_nm is not None \
            and old_bjd_nm != new_bjd_nm \
            and old_bjd_nm not in self.bjd_current_bjd_nm_list \
            and str(old_bjd_cd)[5:] != '00000': # 시도, 시군구는 제외
                bjd_changed_dictionary[old_bjd_nm] = new_bjd_nm
        return bjd_changed_dictionary


    def _prepare(self):

        with open(self.file_name_bjd_current, 'r', encoding=self.encoding) as file_bjd_current:
            self.bjd_current_dic: Dict[str, str] = dict((line.split('\t')[2], line.split('\t')[9].replace('\n', '')) for line in file_bjd_current)

        with open(self.file_name_bjd_smallest, 'r', encoding=self.encoding) as file_bjd_smallest:
            self.bjd_smallest_list: List[str] = [line.strip() for line in file_bjd_smallest]

        with open(self.file_name_multiple_word_sgg_list, 'r', encoding=self.encoding) as file_multiple_word_sgg_list:
            self.multiple_word_sgg_list: List[str] = [line.strip() for line in file_multiple_word_sgg_list]

        bjd_df: pd.DataFrame = pd.read_csv(
            self.file_name_bjd,
            sep=self.sep,
            engine='python',
            encoding=self.encoding,
            dtype={
                '과거법정동코드': str,
                '법정동코드': str,
                '생성일자': object,
                '삭제일자': object,
                '시도명': str,
                '시군구명': str,
                '읍면동명': str,
                '리명': str
            })
        self.bjd_df = bjd_df
        self.sido_list: List[str] = list(sido for sido in bjd_df['시도명'].unique() if isinstance(sido, str))
        self.sgg_list: List[str] = list(sgg for sgg in bjd_df['시군구명'].unique() if isinstance(sgg, str))
        self.emd_list: List[str] = list(emd for emd in bjd_df['읍면동명'].unique() if isinstance(emd, str))
        self.ri_list: List[str] = list(ri for ri in bjd_df['리명'].unique() if isinstance(ri, str))

        bjd_current_df: pd.DataFrame = pd.read_csv(
            self.file_name_bjd_current,
            sep=self.sep,
            engine='python',
            encoding=self.encoding,
            dtype={
                '과거법정동코드': str,
                '법정동코드': str,
                '생성일자': object,
                '삭제일자': object,
                '시도명': str,
                '시군구명': str,
                '읍면동명': str,
                '리명': str
            }
        )
        self.bjd_current_bjd_nm_list: List[str] = list(bjd_nm for bjd_nm in bjd_current_df['법정동명'] if bjd_nm is not None)
        bjd_current_df['시도시군구명'] = bjd_current_df[['시도명', '시군구명']].apply(lambda x: self._concat_sido_sgg(*x), axis=1)
        self.current_sido_sgg_list: List[str] = list(sido_sgg for sido_sgg in bjd_current_df['시도시군구명'].unique() if isinstance(sido_sgg, str))
        self.current_sido_list: List[str] = list(sido for sido in bjd_current_df['시도명'].unique() if isinstance(sido, str))
        self.current_sgg_list: List[str] = list(sgg for sgg in bjd_current_df['시군구명'].unique() if isinstance(sgg, str))
        self.current_emd_list: List[str] = list(emd for emd in bjd_current_df['읍면동명'].unique() if isinstance(emd, str))
        self.current_ri_list: List[str] = list(ri for ri in bjd_current_df['리명'].unique() if isinstance(ri, str))
        self.bjd_current_df = bjd_current_df

        bjd_changed_df: pd.DataFrame = pd.read_csv(
            self.file_name_bjd_changed,
            sep=self.sep,
            engine='python',
            encoding=self.encoding,
            dtype={
                '과거법정동코드': str,
                '법정동코드': str,
                '생성일자_변경전': object,
                '삭제일자_변경전': object,
                '생성일자_변경후': object,
                '삭제일자_변경후': object,
                '법정동명_변경전': str,
                '법정동명_변경후': str
            })
        self.bjd_changed_df = bjd_changed_df
        sub_bjd_changed_df = bjd_changed_df.loc[
            (bjd_changed_df['법정동명_변경후'].isnull()==False) &
            (bjd_changed_df['법정동명_변경전'].isnull()==False)
        ]
        self.bjd_changed_dic: Dict[str, str] = self._create_bjd_changed_dictionary(sub_bjd_changed_df)
        self.bjd_changed_old_bjd_nm_list: List[str] = list(self.bjd_changed_dic.keys())


    @staticmethod
    def correct_simple_spacing(
        addr: str
    ) -> str:

        """
        입력된 문자열(한글 주소)의 연속된 공백을 단일 공백으로 정규화한 문자열로 반환

        Args:
            addr (str): The input korean address string.

        Raises:
            TypeError: If the 'addr' object is not of type string.

        Returns:
            str: A string that normalize multiple consecutive spaces in a string to a single space.
        """

        if not isinstance(addr, str):
            raise TypeError("type of object('addr') must be string")

        return re.sub(r'\s+', ' ', addr)


    @staticmethod
    def replace_etc_land_string(
        addr: str
    ):

        """
        입력된 문자열(한글 주소) 중 '외 필지'와 같은 다중 지번과 관련된 문자열 패턴 매칭하여 띄어쓰기 수정하여 반환

        Args:
            addr (str): The input korean address string.

        Raises:
            TypeError: If the 'addr' object is not of type string.

        Returns:
            str: Match patterns related to multiple land lots, such as '외 필지', in the input string (Korean address), and return the string with corrected spacing.
        """

        if not isinstance(addr, str):
            raise TypeError("type of object('addr') must be string")

        match = re.search(ETC_LAND_PATTERN, addr)
        if match:
            origin_string = match.group(0)
            replace_string = match.group(0).replace('외', ' 외')
            return addr.replace(origin_string, replace_string)
        else:
            return addr


    # 가장 작은 법정동명 뒤 번지가 띄어쓰기 없이 붙어있을 경우,
    # 가장 작은 법정동명에 포함된 숫자중 2자리수는 없음. 예 당산동1가, 을지로5가 등
    def correct_smallest_bjd_spacing(
        self,
        addr: str
    ) -> str:

        """
        입력된 문자열(한글 주소)의 가장 작은 법정동명과 번지 사이 빈공백을 단일 공백으로 정규화한 문자열로 반환

        Args:
            addr (str): The input korean address string.

        Raises:
            TypeError: If the 'addr' object is not of type string.
            ValueError: If the 'bjd_smallest_list' class constructor is None.

        Returns:
            str: A string that is the smallest administrative division name and address number space of the input string, with multiple spaces normalized to a single space.
        """

        if not isinstance(addr, str):
            raise TypeError("type of object('addr') must be string")

        if self.bjd_smallest_list is None:
            raise ValueError("bjd_smallest_list is None")

        for bjdnm in self.bjd_smallest_list:
            if bjdnm in addr and (addr.split(bjdnm)[1][:2]).replace('-', '').isdigit() == True:
                addr = addr.split(bjdnm)[0] + bjdnm + ' ' + addr.split(bjdnm)[1]
                return addr
        return addr


    @staticmethod
    def union_similar_changed_bjd(
        changed_bjd_list: List[str]
    ):

        """
        교체할 변경내역 법정동 리스트 중 완전히 포함관계인 경우는 제외하여 반환
        """

        if len(changed_bjd_list) > 0:
            new_bjd_list: List[str] = list()
            for bjd in changed_bjd_list:
                if not any(bjd in other_bjd for other_bjd in changed_bjd_list if other_bjd != bjd):
                    new_bjd_list.append(bjd)
            return new_bjd_list
        else:
            return changed_bjd_list


    def check_is_current_bjd(
        self,
        bjd_nm: str
    ) -> bool:

        """
        입력된 법정동명이 현재 법정동명 리스트에 포함되어있는지 확인하여 반환
        """

        if bjd_nm in self.bjd_current_bjd_nm_list:
            return True
        else:
            return False


    def correct_changed_bjd(
        self,
        addr: str,
        is_log: bool = True
    ) -> str:

        """
        입력된 문자열(한글 주소)에 변경전 법정동이 포함되어있으면 변경후 법정동명으로 교환하여 반환

        Args:
            addr (str): The input korean address string.

        Raises:
            TypeError: If the 'addr' object is not of type string.
            ValueError: If the 'bjd_changed_old_bjd_nm_list' class constructor is None.
            ValueError: If the 'bjd_changed_dic' class constructor is None.

        Returns:
            str: If the input string contains the previous administrative division name, eplace it with the modified administrative division name and return.
        """

        if not isinstance(addr, str):
            raise TypeError("type of object('addr') must be string")

        if not isinstance(is_log, bool):
            raise TypeError("type of object('is_log') must be bool")

        if self.bjd_changed_old_bjd_nm_list is None:
            raise ValueError("bjd_changed_old_bjd_nm_list is None")

        if self.bjd_changed_dic is None:
            raise ValueError("bjd_changed_dic is None")

        origin_addr: str = addr
        last_changed_bjd_nm: str = None
        max_iterations = 10  # 무한 루프 방지
        iteration = 0

        while iteration < max_iterations:
            changed_list: List[str] = list()
            for old_bjd_nm in self.bjd_changed_old_bjd_nm_list:
                if old_bjd_nm in addr:
                    changed_list.append(old_bjd_nm)

            changed_list = self.union_similar_changed_bjd(changed_list)
            if not changed_list:  # 더 이상 변경할 것이 없으면 종료
                break

            for changed_bjd_nm in changed_list:
                after_changed_bjd_nm = self.bjd_changed_dic[changed_bjd_nm]
                last_changed_bjd_nm = after_changed_bjd_nm
                addr = addr.replace(changed_bjd_nm, after_changed_bjd_nm)
                if is_log:
                    self.logger.info(f'해당 법정동명은 변경되었습니다. 변경전 : [ {changed_bjd_nm} ] 변경후 : [ {after_changed_bjd_nm} ]')

            iteration += 1

        if last_changed_bjd_nm is not None:
            if self.check_is_current_bjd(bjd_nm=last_changed_bjd_nm):
                if is_log:
                    self.logger.info(f'해당 법정동명은 현재 법정동명입니다.')
            else:
                if is_log:
                    self.logger.warning(f'해당 법정동명은 현재 법정동명이 아닙니다.')
        return addr


    def correct_bjd(
        self,
        addr: str,
        is_log: bool = True
    ) -> str:

        """
        입력된 문자열(한글 주소)의 법정동명 교정하여 반환

        Args:
            addr (str): The input korean address string.

        Raises:
            TypeError: If the 'addr' object is not of type string.

        Sub Functions:
            - correct_simple_spacing
            - correct_smallest_bjd_spacing
            - correct_changed_bjd

        Returns:
            Correct and return the input string by adjusting spaces in the main address and modifying the administrative division name.
        """

        if not isinstance(addr, str):
            raise TypeError("type of object('addr') must be string")

        if not isinstance(is_log, bool):
            raise TypeError("type of object('is_log') must be bool")

        addr = self.replace_etc_land_string(addr)
        addr = self.correct_simple_spacing(addr)
        addr = self.correct_smallest_bjd_spacing(addr)
        addr = self.correct_changed_bjd(addr, is_log)
        return addr