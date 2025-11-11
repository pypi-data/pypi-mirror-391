import re
import hashlib
from datetime import date
from typing import (
    List,
    Union
)
from dataclasses import dataclass
from vdutils.library import Log


@dataclass
class Vid():


    def __init__(self):
        self.logger = Log('Vid').stream_handler("INFO")
        self.is_pnu_valid_regex = re.compile("^\d{19}$")


    @staticmethod
    def _remove_comma(value: str) -> str:
        return value.replace(",", "")


    @staticmethod
    def _format_float_string(float_str: str) -> str:
        if float_str:
            dot_split = float_str.split(".")
            if len(dot_split) == 1:
                return float_str
            elif len(dot_split) == 2:
                part_int, part_float = dot_split
                float_numbers = list(part_float)
                for i in range(len(part_float) - 1, -1, -1):
                    number = float_numbers[i]
                    if number != "0":
                        break
                    else:
                        float_numbers.pop()
                no_trailing_zero_float_part = "".join(float_numbers)
                if no_trailing_zero_float_part:
                    return ".".join([part_int, no_trailing_zero_float_part])
                else:
                    return part_int
            else:
                return float_str
        else:
            return ""


    def _format_float(
        self, 
        float_num: str
    ) -> str:
        return self._format_float_string(self._remove_comma(str(float_num)))


    def _is_number_valid(
        self, 
        number: Union[float, int, str, None]
    ) -> bool:
        try:
            ff = self._format_float(number)
            if (
                not ff
                or len(ff.split(".")) > 2
                or not re.compile("^\d*$").match(ff.replace(".", ""))
            ):
                return False
            else:
                return True
        except:
            return False


    def _is_pnu_valid(
        self, 
        pnu: str
    ):
        return self.is_pnu_valid_regex.match(pnu)


    @staticmethod
    def _is_contract_date_valid(
        contract_ymd:  Union[str, int, None]
    ) -> bool:
        if type(contract_ymd) != str:
            contract_ymd = str(contract_ymd)
        if len(contract_ymd) == 8 and re.compile("^\d{8}$").match(contract_ymd):
            try:
                d = date.fromisoformat(
                    f"{contract_ymd[:4]}-{contract_ymd[4:6]}-{contract_ymd[6:]}"
                )
                return True
            except:
                return False
        return False


    @staticmethod
    def _is_string_valid(value) -> bool:
        return isinstance(value, str)


    @staticmethod
    def _validate(validator, value, value_nm):
        if value and not validator(value):
            raise Exception(f"invalid {validator}, {value_nm}: {value}")


    @staticmethod
    def _get_hash_raw(data_str: str) -> str:
        return hashlib.sha256(data_str.encode("utf-8")).hexdigest()


    def generate_registration_vid(
        self,
        pnu: str,
        contract_ymd: Union[str, int, None],
        price: Union[float, int, None] = None,
        unit_ar: Union[float, int, str, None] = None,
        lot_ar: Union[float, int, str, None] = None,
        seller: Union[str, None] = None,
        buyer: Union[str, None] = None,
    ) -> List[Union[str, None]]:

        """
        주어진 입력값들을 문자열로 변환하여 SHA-256 해시값을 생성하여 반환\n 
        각 입력값들의 타입정의 및 형식이 명확하지 않아, TypeError, ValueError 를 정의하지 않고 모든 오류에 대해 동일한 예외용 응답만을 반환

        Args:
            pnu (str): Represents the Parcel Numbering Unit, a 19-digit numeric string (10 digits for the administrative district code + 1 digit for the mountain code + 8 digits for the plot number).
            contract_ymd (str): Transaction date in YYYYMMDD format, an 8-digit numeric string.
            price (Union[float, int, None]): Transaction price.
            unit_ar (Union[float, int, str, None]): Transaction unit area.
            lot_ar (Union[float, int, str, None]): Transaction land area.
            seller (Union[str, None]): Seller.
            buyer (Union[str, None]): Buyer.

        Returns: List[Union[str, None]]
        """

        except_response = [
            f"R_{pnu[:10] if self._is_pnu_valid(pnu) else 'pnu10dhead'}_{'hashstring'}_0000",
            None,
            None,
        ]
        try:
            self._validate(self._is_pnu_valid, pnu, "pnu")
            self._validate(self._is_contract_date_valid, contract_ymd, "contract_ymd")
            self._validate(self._is_number_valid, price, "price")
            if not unit_ar == "-":
                self._validate(self._is_number_valid, unit_ar, "unit_ar")
            if not lot_ar == "-":
                self._validate(self._is_number_valid, lot_ar, "lot_ar")
            self._validate(self._is_string_valid, seller, "seller")
            self._validate(self._is_string_valid, buyer, "buyer")

            data_str = "_".join(
                [
                    pnu,
                    contract_ymd,
                    self._format_float(price) if price else "",
                    self._format_float(unit_ar) if price else "",
                    self._format_float(lot_ar) if price else "",
                    seller or "",
                    buyer or "",
                ]
            )
            h = self._get_hash_raw(data_str)

            return [f"R_{pnu[:10]}_{h[:10]}_0000", h, data_str]

        except Exception as e:
            self.logger.info(f"{pnu}, {e}")
            return except_response
