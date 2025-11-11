import os
import sys
import unittest
import logging
from typing import Pattern
sys.path.append(os.getcwd())
from vdutils.vid import Vid


class TestClass(unittest.TestCase):

    @classmethod
    def setUp(cls):
        "Hook method for setting fixture before running tests in the class"
        cls.driver = 'test'
        cls.instance = Vid()


    @classmethod
    def tearDown(cls):
        "Hook method for deconstructing the class fixture after running all tests in the class"


    def test_class_initialization_type(self):
        """
        클래스 인스턴스 초기 생성자 타입 테스트 메소드

        - 클래스 인스턴스 초기 생성자 객체의 값의 타입이 지정된 타입과 일치하는지 확인하는 테스트
            - __init__.logger 객체 테스트
            - __init__.is_pnu_valid_regex 객체 테스트
        """

        self.assertIsInstance(self.instance.logger, logging.Logger)
        self.assertIsInstance(self.instance.is_pnu_valid_regex, Pattern) # default False


    def test_class_initialization_not_empty(self):
        """
        클래스 인스턴스 초기 생성자 객체 테스트 메소드

        - 클래스 인스턴스 초기 생성자 객체의 값이 None이 아닌지(IsNotNone) 확인하는 테스트
            - __init__.logger 객체 테스트
            - __init__.is_pnu_valid_regex 객체 테스트

        - 클래스 인스턴스 초기 생성자 객체의 Length가 0이 아닌지 확인하는 테스트
            - __init__.logger 객체 테스트 (logging.Logger pass)
            - __init__.is_pnu_valid_regex 객체 테스트 (pattern pass)
        """

        self.assertIsNotNone(self.instance.logger)
        self.assertIsNotNone(self.instance.is_pnu_valid_regex)

        # self.assertNotEqual(len(self.instance.logger), 0)
        # self.assertNotEqual(len(self.instance.is_pnu_valid_regex), 0)


    def test_generate_registration_vid(self):
        """
        generate_registration_vid 함수 테스트 메소드

        - generate_registration_vid 함수 리턴값 테스트(올바른 입력값 제공)
            - generate_registration_vid 함수 리턴값 타입 테스트
            - generate_registration_vid 함수 리턴값 None 이 아닌지 테스트
            - generate_registration_vid 함수 리턴값 리스트 첫번째 객체값 타입 테스트
            - generate_registration_vid 함수 리턴값 리스트 첫번째 객체값 None 이 아닌지 테스트
            - generate_registration_vid 함수 리턴값 리스트 두번째 객체값 타입 테스트
            - generate_registration_vid 함수 리턴값 리스트 두번째 객체값 None 이 아닌지 테스트
            - generate_registration_vid 함수 리턴값 리스트 세번째 객체값 타입 테스트
            - generate_registration_vid 함수 리턴값 리스트 세번째 객체값 None 이 아닌지 테스트
            - generate_registration_vid 함수 리턴값 일치 테스트

        - generate_registration_vid 함수 리턴값 테스트(올바르지 않은 입력값 제공)
            - generate_registration_vid 함수 리턴값 타입 테스트
            - generate_registration_vid 함수 리턴값 None 이 아닌지 테스트
            - generate_registration_vid 함수 리턴값 리스트 첫번째 객체값 타입 테스트
            - generate_registration_vid 함수 리턴값 리스트 첫번째 객체값 None 이 아닌지 테스트
            - generate_registration_vid 함수 리턴값 리스트 두번째 객체값 타입 테스트 (None pass)
            - generate_registration_vid 함수 리턴값 리스트 두번째 객체값 None 이 맞는지 테스트
            - generate_registration_vid 함수 리턴값 리스트 세번째 객체값 타입 테스트 (None pass)
            - generate_registration_vid 함수 리턴값 리스트 세번째 객체값 None 이 맞는지 테스트
            - generate_registration_vid 함수 리턴값 일치 테스트
        """

        res = self.instance.generate_registration_vid(
            pnu='1234567890123456789',
            contract_ymd='20240101',
            price=100,
            unit_ar=100.1,
            lot_ar=100.1,
            seller='seller',
            buyer='buyer',
        )
        self.assertIsInstance(res, list)
        self.assertIsNotNone(res)
        self.assertIsInstance(res[0], str)
        self.assertIsNotNone(res[0])
        self.assertIsInstance(res[1], str)
        self.assertIsNotNone(res[1])
        self.assertIsInstance(res[2], str)
        self.assertIsNotNone(res[2])
        self.assertEqual(res, [
            'R_1234567890_581e28e445_0000',
            '581e28e4457103048784572e858c5ed1297cf8747169a8454e98a19233036f55',
            '1234567890123456789_20240101_100_100.1_100.1_seller_buyer'
        ])

        res = self.instance.generate_registration_vid(
            pnu='1234567890123456789',
            contract_ymd='20240101',
            price='100',
            unit_ar='100.1',
            lot_ar='100.1',
            seller='seller',
            buyer='buyer',
        )
        self.assertIsInstance(res, list)
        self.assertIsNotNone(res)
        self.assertIsInstance(res[0], str)
        self.assertIsNotNone(res[0])
        self.assertIsInstance(res[1], str)
        self.assertIsNotNone(res[1])
        self.assertIsInstance(res[2], str)
        self.assertIsNotNone(res[2])
        self.assertEqual(res, [
            'R_1234567890_581e28e445_0000',
            '581e28e4457103048784572e858c5ed1297cf8747169a8454e98a19233036f55',
            '1234567890123456789_20240101_100_100.1_100.1_seller_buyer'
        ])

        res = self.instance.generate_registration_vid(
            pnu='12345678901234567890', # 19자리 형식에 맞지 않는 잘못된 입력값 제공
            contract_ymd='20240101',
            price=100,
            unit_ar=100.1,
            lot_ar=100.1,
            seller='seller',
            buyer='buyer',
        )
        self.assertIsInstance(res, list)
        self.assertIsNotNone(res)
        self.assertIsInstance(res[0], str)
        self.assertIsNotNone(res[0])
        # self.assertIsInstance(res[1], None) # (None pass)
        self.assertIsNone(res[1])
        # self.assertIsInstance(res[2], None) # (None pass)
        self.assertIsNone(res[2])
        self.assertEqual(res, [
            'R_pnu10dhead_hashstring_0000',
            None,
            None
        ])

        res = self.instance.generate_registration_vid(
            pnu='1234567890123456789',
            contract_ymd='2024-01-01',  # YYYYMMDD 형식에 맞지 않는 잘못된 입력값 제공
            price=100,
            unit_ar=100.1,
            lot_ar=100.1,
            seller='seller',
            buyer='buyer',
        )
        self.assertIsInstance(res, list)
        self.assertIsNotNone(res)
        self.assertIsInstance(res[0], str)
        self.assertIsNotNone(res[0])
        # self.assertIsInstance(res[1], None) # (None pass)
        self.assertIsNone(res[1])
        # self.assertIsInstance(res[2], None) # (None pass)
        self.assertIsNone(res[2])
        self.assertEqual(res, [
            'R_1234567890_hashstring_0000',
            None,
            None
        ])

        res = self.instance.generate_registration_vid(
            pnu='1234567890123456789',
            contract_ymd='20240101',
            price=-100, # 음수 잘못된 입력값 제공
            unit_ar=100.1,
            lot_ar=100.1,
            seller='seller',
            buyer='buyer',
        )
        self.assertIsInstance(res, list)
        self.assertIsNotNone(res)
        self.assertIsInstance(res[0], str)
        self.assertIsNotNone(res[0])
        # self.assertIsInstance(res[1], None) # (None pass)
        self.assertIsNone(res[1])
        # self.assertIsInstance(res[2], None) # (None pass)
        self.assertIsNone(res[2])
        self.assertEqual(res, [
            'R_1234567890_hashstring_0000',
            None,
            None
        ])

        res = self.instance.generate_registration_vid(
            pnu='1234567890123456789',
            contract_ymd='20240101',
            price=100,
            unit_ar='a', # 숫자 혹은 숫자문자열이 아닌 문자열 입력값 제공
            lot_ar=100.1,
            seller='seller',
            buyer='buyer',
        )
        self.assertIsInstance(res, list)
        self.assertIsNotNone(res)
        self.assertIsInstance(res[0], str)
        self.assertIsNotNone(res[0])
        # self.assertIsInstance(res[1], None) # (None pass)
        self.assertIsNone(res[1])
        # self.assertIsInstance(res[2], None) # (None pass)
        self.assertIsNone(res[2])
        self.assertEqual(res, [
            'R_1234567890_hashstring_0000',
            None,
            None
        ])

        res = self.instance.generate_registration_vid(
            pnu='1234567890123456789',
            contract_ymd='20240101',
            price=100,
            unit_ar=100.1,
            lot_ar=100.1,
            seller=1, # 문자열 아닌 숫자 입력값 제공
            buyer='buyer',
        )
        self.assertIsInstance(res, list)
        self.assertIsNotNone(res)
        self.assertIsInstance(res[0], str)
        self.assertIsNotNone(res[0])
        # self.assertIsInstance(res[1], None) # (None pass)
        self.assertIsNone(res[1])
        # self.assertIsInstance(res[2], None) # (None pass)
        self.assertIsNone(res[2])
        self.assertEqual(res, [
            'R_1234567890_hashstring_0000',
            None,
            None
        ])


if __name__ == "__main__":
    unittest.main()