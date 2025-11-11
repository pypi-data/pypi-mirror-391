import os
import sys
import unittest
import pandas as pd
from datetime import datetime
from typing import ( 
    List,
    Dict,
    Tuple,
    Optional
)
sys.path.append(os.getcwd())
from vdutils.genpnu import GenPnu


class TestClass(unittest.TestCase):

    @classmethod
    def setUp(cls):
        "Hook method for setting fixture before running tests in the class"
        cls.driver = 'test'
        cls.test_bjd_cd = '1168010500'
        cls.test_bjd_nm = '서울특별시 강남구 삼성동'
        cls.test_jibun = '1'
        cls.test_address = '서울특별시 강남구 삼성동 1'
        cls.test_base_dt = datetime.today().strftime('%Y%m%d')
        cls.instance = GenPnu(base_dt=cls.test_base_dt)


    @classmethod
    def tearDown(cls):
        "Hook method for deconstructing the class fixture after running all tests in the class"


    def test_class_initialization_type(self):
        """
        클래스 인스턴스 초기 생성자 타입 테스트 메소드

        - 클래스 인스턴스 초기 생성자 객체의 값의 타입이 지정된 타입과 일치하는지 확인하는 테스트
            - __init__.sep 객체 테스트
            - __init__.index 객체 테스트
            - __init__.encoding 객체 테스트
            - __init__.base_dt 객체 테스트
            - __init__.bjd_current_df 객체 테스트
            - __init__.bjd_current_nm_cd_dic 객체 테스트
            - __init__.bjd_dic 객체 테스트
            - __init__.bjd_nm_change_dic 객체 테스트
            - __init__.base_dt_print 객체 테스트
        """

        self.assertIsInstance(self.instance.sep, str)
        self.assertIs(self.instance.index, False) # default False
        self.assertIsInstance(self.instance.encoding, str)
        self.assertIsInstance(self.instance.base_dt, (str, type(None)))
        self.assertIsInstance(self.instance.bjd_current_df, pd.DataFrame)
        self.assertFalse(self.instance.bjd_current_df.empty) # pd.DataFrame() 형식이라 empty 확인
        self.assertIsInstance(self.instance.bjd_current_nm_cd_dic, dict)
        self.assertIsInstance(self.instance.bjd_dic, dict)
        self.assertTrue(all(isinstance(item, str) for item in self.instance.bjd_dic.keys()))
        self.assertTrue(all(isinstance(item, dict) for item in self.instance.bjd_dic.values()))
        self.assertIsInstance(self.instance.bjd_nm_change_dic, dict)
        self.assertTrue(all(isinstance(item, str) for item in self.instance.bjd_nm_change_dic.keys()))
        self.assertTrue(all(isinstance(item, str) for item in self.instance.bjd_nm_change_dic.values()))
        self.assertIsInstance(self.instance.base_dt_print, str)


    def test_class_initialization_not_empty(self):
        """
        클래스 인스턴스 초기 생성자 객체 테스트 메소드

        - 클래스 인스턴스 초기 생성자 객체의 값이 None이 아닌지(IsNotNone) 확인하는 테스트
            - __init__.sep 객체 테스트
            - __init__.index 객체 테스트
            - __init__.encoding 객체 테스트
            - __init__.base_dt 객체 테스트
            - __init__.bjd_current_df 객체 테스트
            - __init__.bjd_current_nm_cd_dic 객체 테스트
            - __init__.bjd_dic 객체 테스트
            - __init__.bjd_nm_change_dic 객체 테스트
            - __init__.base_dt_print 객체 테스트

        - 클래스 인스턴스 초기 생성자 객체의 Length가 0이 아닌지 확인하는 테스트
            - __init__.sep 객체 테스트
            - __init__.index 객체 테스트 (bool pass)
            - __init__.encoding 객체 테스트
            - __init__.base_dt 객체 테스트
            - __init__.bjd_current_df 객체 테스트
            - __init__.bjd_current_nm_cd_dic 객체 테스트
            - __init__.bjd_dic 객체 테스트
            - __init__.bjd_nm_change_dic 객체 테스트
            - __init__.base_dt_print 객체 테스트

        """

        self.assertIsNotNone(self.instance.sep)
        self.assertIsNotNone(self.instance.index)
        self.assertIsNotNone(self.instance.encoding)
        self.assertIsNotNone(self.instance.base_dt)
        self.assertIsNotNone(self.instance.bjd_current_df)
        self.assertIsNotNone(self.instance.bjd_current_nm_cd_dic)
        self.assertIsNotNone(self.instance.bjd_dic)
        self.assertIsNotNone(self.instance.bjd_nm_change_dic)
        self.assertIsNotNone(self.instance.base_dt_print)
        
        self.assertNotEqual(len(self.instance.sep), 0)
        # self.assertNotEqual(len(self.instance.index), 0) # bool 
        self.assertNotEqual(len(self.instance.encoding), 0)
        self.assertNotEqual(len(self.instance.base_dt), 0)
        self.assertNotEqual(len(self.instance.bjd_current_df), 0)
        self.assertNotEqual(len(self.instance.bjd_current_nm_cd_dic), 0)
        self.assertNotEqual(len(self.instance.bjd_dic), 0)
        self.assertNotEqual(len(self.instance.bjd_nm_change_dic), 0)
        self.assertNotEqual(len(self.instance.base_dt_print), 0)


    def test_runs(self):
        """
        단순 실행여부 판별하는 테스트 메소드

        - 클래스 인스턴스 함수 실행 확인하는 테스트
            - get_bjd_cd 함수 테스트
            - get_bjd_data 함수 테스트
            - generate_pnu 함수 테스트
            - generate_pnu_from_bjd_nm 함수 테스트
        """

        self.instance.get_bjd_cd(bjd_nm=self.test_bjd_nm)
        self.instance.get_bjd_data(bjd_cd=self.test_bjd_cd)
        self.instance.generate_pnu(bjd_cd=self.test_bjd_cd, jibun=self.test_jibun)
        self.instance.generate_pnu_from_bjd_nm(bjd_nm=self.test_bjd_nm, jibun=self.test_jibun)
        self.instance.generate_pnu_from_address(address=self.test_address)


    def test_get_bjd_cd(self):
        """
        get_bjd_cd 함수 테스트 메소드

        - get_bjd_cd 함수 예외처리 테스트
            - get_bjd_cd 함수 예외처리 테스트(TypeError 입력값이 문자열이 아닌 int type)
            - get_bjd_cd 함수 예외처리 테스트(TypeError 입력값이 문자열이 아닌 float type)
            - get_bjd_cd 함수 예외처리 테스트(TypeError 입력값이 문자열이 아닌 None type)
            - get_bjd_cd 함수 예외처리 테스트(TypeError 입력값이 문자열이 아닌 bool type)
            - get_bjd_cd 함수 예외처리 테스트(ValueError 입력값이 적절한 형식(숫자와 한글로만 이루어진 문자열)의 문자열이 아닌 알파벳 포함)
            - get_bjd_cd 함수 예외처리 테스트(ValueError 입력값이 적절한 형식(숫자와 한글로만 이루어진 문자열)의 문자열이 아닌 알파벳 문자열 포함)
            - get_bjd_cd 함수 예외처리 테스트(ValueError 입력값이 적절한 형식(숫자와 한글로만 이루어진 문자열)의 문자열이 아닌 한글 자음 포함)

        - get_bjd_cd 함수 리턴값 테스트(올바른 법정동 문자열 제공)
            - get_bjd_cd 함수 리턴값 타입 테스트
            - get_bjd_cd 함수 리턴값 error 타입 테스트
            - get_bjd_cd 함수 리턴값 bjd_cd 타입 테스트
            - get_bjd_cd 함수 리턴값 deleted_dt 타입 테스트 (None pass)
            - get_bjd_cd 함수 리턴값 base_dt 타입 테스트
            - get_bjd_cd 함수 리턴값 msg 타입 테스트
            - get_bjd_cd 함수 리턴값 error 값이 None 이 아닌지 테스트
            - get_bjd_cd 함수 리턴값 bjd_cd 값이 None 이 아닌지 테스트
            - get_bjd_cd 함수 리턴값 deleted_dt 값이 None 이 아닌지 테스트
            - get_bjd_cd 함수 리턴값 base_dt 값이 None 이 아닌지 테스트
            - get_bjd_cd 함수 리턴값 msg 값이 None 이 아닌지 테스트
            - get_bjd_cd 함수 리턴값 일치 테스트

        - get_bjd_cd 함수 리턴값 테스트(존재하지 않은 법정동 문자열 제공)
            - get_bjd_cd 함수 리턴값 타입 테스트
            - get_bjd_cd 함수 리턴값 error 타입 테스트
            - get_bjd_cd 함수 리턴값 bjd_cd 타입 테스트 (None pass)
            - get_bjd_cd 함수 리턴값 deleted_dt 타입 테스트 (None pass)
            - get_bjd_cd 함수 리턴값 base_dt 타입 테스트
            - get_bjd_cd 함수 리턴값 msg 타입 테스트
            - get_bjd_cd 함수 리턴값 error 값이 None 이 아닌지 테스트
            - get_bjd_cd 함수 리턴값 bjd_cd 값이 None 이 아닌지 테스트
            - get_bjd_cd 함수 리턴값 deleted_dt 값이 None 이 아닌지 테스트
            - get_bjd_cd 함수 리턴값 base_dt 값이 None 이 아닌지 테스트
            - get_bjd_cd 함수 리턴값 msg 값이 None 이 아닌지 테스트
            - get_bjd_cd 함수 리턴값 일치 테스트
        """

        with self.assertRaises(TypeError): self.instance.get_bjd_cd(bjd_nm=1)
        with self.assertRaises(TypeError): self.instance.get_bjd_cd(bjd_nm=0.1)
        with self.assertRaises(TypeError): self.instance.get_bjd_cd(bjd_nm=None)
        with self.assertRaises(TypeError): self.instance.get_bjd_cd(bjd_nm=False)
        with self.assertRaises(ValueError): self.instance.get_bjd_cd(bjd_nm='a 서울특별시 강남구 삼성동') # 알파벳 포함
        with self.assertRaises(ValueError): self.instance.get_bjd_cd(bjd_nm='seoulsi gangnamgu samsungdong') # 알파벳 포함
        with self.assertRaises(ValueError): self.instance.get_bjd_cd(bjd_nm='ㄱ 서울특별시 강남구 삼성동') # 불완전한 한글 문자열 포함

        res = self.instance.get_bjd_cd('서울특별시 강남구 삼성동') # 정상적인 법정동명 입력값
        self.assertIsInstance(res, dict)
        self.assertIsInstance(res.get('error'), bool)
        self.assertIsInstance(res.get('bjd_cd'), (str, type(None)))
        # self.assertTrue(res.get('deleted_dt'), Optional[str])
        self.assertIsInstance(res.get('base_dt'), str)
        self.assertIsInstance(res.get('msg'), str)
        self.assertIsNotNone(res.get('error'))
        self.assertIsNotNone(res.get('bjd_cd'))
        self.assertIsNone(res.get('deleted_dt')) # 현재 존재하는 법정동의 경우 deleted_dt == None
        self.assertIsNotNone(res.get('base_dt'))
        self.assertIsNotNone(res.get('msg'))
        self.assertEqual(res, {
            'error': False,
            'bjd_cd': '1168010500',
            'deleted_dt': None,
            'base_dt': self.instance.base_dt_print, # base_dt_print 는 업데이트 되므로 self.instance.base_dt_print 로 적용
            'msg': ''
        })

        res = self.instance.get_bjd_cd('부산광역시 강남구 삼성동') # 비정상적인 법정동명 입력값
        self.assertIsInstance(res, dict)
        self.assertIsInstance(res.get('error'), bool)
        # self.assertTrue(res.get('bjd_cd'), Optional[str])
        # self.assertTrue(res.get('deleted_dt'), Optional[str])
        self.assertIsInstance(res.get('base_dt'), str)
        self.assertIsInstance(res.get('msg'), str)
        self.assertIsNotNone(res.get('error'))
        self.assertIsNone(res.get('bjd_cd')) # 존재하지 않는 법정동의 경우, bjd_cd == None
        self.assertIsNone(res.get('deleted_dt')) # 존재하지 않는 법정동의 경우, deleted_dt == None
        self.assertIsNotNone(res.get('base_dt'))
        self.assertIsNotNone(res.get('msg'))
        self.assertEqual(res, {
            'error': True,
            'bjd_cd': None,
            'deleted_dt': None,
            'base_dt': self.instance.base_dt_print, # base_dt_print 는 업데이트 되므로 self.instance.base_dt_print 로 적용
            'msg': "'부산광역시 강남구 삼성동' is not a valid legal district name"
        })


    def test_get_bjd_data(self):
        """
        get_bjd_data 함수 테스트 메소드

        - get_bjd_data 함수 예외처리 테스트
            - get_bjd_data 함수 예외처리 테스트(TypeError 입력값이 문자열이 아닌 int type)
            - get_bjd_data 함수 예외처리 테스트(TypeError 입력값이 문자열이 아닌 float type)
            - get_bjd_data 함수 예외처리 테스트(TypeError 입력값이 문자열이 아닌 None type)
            - get_bjd_data 함수 예외처리 테스트(TypeError 입력값이 문자열이 아닌 bool type)
            - get_bjd_data 함수 예외처리 테스트(ValueError 입력값이 적절한 형식(10자리 숫자문자열)의 문자열이 아닌 한글 포함)
            - get_bjd_data 함수 예외처리 테스트(ValueError 입력값이 적절한 형식(10자리 숫자문자열)의 문자열이 아닌 알파벳 문자열)
            - get_bjd_data 함수 예외처리 테스트(ValueError 입력값이 적절한 형식(10자리 숫자문자열)의 문자열이 아닌 9자리 숫자문자열)
            - get_bjd_data 함수 예외처리 테스트(ValueError 입력값이 적절한 형식(10자리 숫자문자열)의 문자열이 아닌 11자리 숫자문자열)
            - get_bjd_data 함수 예외처리 테스트(ValueError 입력값이 적절한 형식(10자리 숫자문자열)의 문자열이 아닌 알파벳 포함)
            - get_bjd_data 함수 예외처리 테스트(ValueError 입력값이 적절한 형식(10자리 숫자문자열)의 문자열이 아닌 공백 포함)
            - get_bjd_data 함수 예외처리 테스트(ValueError 입력값이 적절한 형식(10자리 숫자문자열)의 문자열이 아닌 특수문자 포함)

        - get_bjd_data 함수 리턴값 테스트(올바른 법정동 문자열 제공)
            - get_bjd_data 함수 리턴값 타입 테스트
            - get_bjd_data 함수 리턴값 error 타입 테스트
            - get_bjd_data 함수 리턴값 sido_nm 타입 테스트
            - get_bjd_data 함수 리턴값 sgg_nm 타입 테스트
            - get_bjd_data 함수 리턴값 emd_nm 타입 테스트
            - get_bjd_data 함수 리턴값 ri_nm 타입 테스트 (None pass)
            - get_bjd_data 함수 리턴값 full_bjd_nm 타입 테스트
            - get_bjd_data 함수 리턴값 created_dt 타입 테스트
            - get_bjd_data 함수 리턴값 deleted_dt 타입 테스트 (None pass)
            - get_bjd_data 함수 리턴값 base_dt 타입 테스트
            - get_bjd_data 함수 리턴값 error 값이 None 이 아닌지 테스트
            - get_bjd_data 함수 리턴값 sido_nm 값이 None 이 아닌지 테스트
            - get_bjd_data 함수 리턴값 sgg_nm 값이 None 이 아닌지 테스트
            - get_bjd_data 함수 리턴값 emd_nm 값이 None 이 아닌지 테스트
            - get_bjd_data 함수 리턴값 ri_nm 값이 None 이 아닌지 테스트
            - get_bjd_data 함수 리턴값 full_bjd_nm 값이 None 이 아닌지 테스트
            - get_bjd_data 함수 리턴값 created_dt 값이 None 이 아닌지 테스트
            - get_bjd_data 함수 리턴값 deleted_dt 값이 None 이 아닌지 테스트
            - get_bjd_data 함수 리턴값 base_dt 값이 None 이 아닌지 테스트
            - get_bjd_data 함수 리턴값 일치 테스트

        - get_bjd_data 함수 리턴값 테스트(존재하지 않은 법정동 문자열 제공)
            - get_bjd_data 함수 리턴값 타입 테스트
            - get_bjd_data 함수 리턴값 error 타입 테스트
            - get_bjd_data 함수 리턴값 sido_nm 타입 테스트 (None pass)
            - get_bjd_data 함수 리턴값 sgg_nm 타입 테스트 (None pass)
            - get_bjd_data 함수 리턴값 emd_nm 타입 테스트 (None pass)
            - get_bjd_data 함수 리턴값 ri_nm 타입 테스트 (None pass)
            - get_bjd_data 함수 리턴값 full_bjd_nm 타입 테스트 (None pass)
            - get_bjd_data 함수 리턴값 created_dt 타입 테스트 (None pass)
            - get_bjd_data 함수 리턴값 deleted_dt 타입 테스트 (None pass)
            - get_bjd_data 함수 리턴값 base_dt 타입 테스트
            - get_bjd_data 함수 리턴값 error 값이 None 이 아닌지 테스트
            - get_bjd_data 함수 리턴값 sido_nm 값이 None 이 맞는지 테스트
            - get_bjd_data 함수 리턴값 sgg_nm 값이 None 이 맞는지 테스트
            - get_bjd_data 함수 리턴값 emd_nm 값이 None 이 맞는지 테스트
            - get_bjd_data 함수 리턴값 ri_nm 값이 None 이 맞는지 테스트
            - get_bjd_data 함수 리턴값 full_bjd_nm 값이 None 이 맞는지 테스트
            - get_bjd_data 함수 리턴값 created_dt 값이 None 이 맞는지 테스트
            - get_bjd_data 함수 리턴값 deleted_dt 값이 None 이 맞는지 테스트
            - get_bjd_data 함수 리턴값 base_dt 값이 None 이 아닌지 테스트
            - get_bjd_data 함수 리턴값 일치 테스트
        """

        with self.assertRaises(TypeError): self.instance.get_bjd_data(bjd_cd=1)
        with self.assertRaises(TypeError): self.instance.get_bjd_data(bjd_cd=0.1)
        with self.assertRaises(TypeError): self.instance.get_bjd_data(bjd_cd=None)
        with self.assertRaises(TypeError): self.instance.get_bjd_data(bjd_cd=False)
        with self.assertRaises(ValueError): self.instance.get_bjd_data(bjd_cd='서울특별시 강남구 삼성동') # 숫자 문자열이 아닌 문자열
        with self.assertRaises(ValueError): self.instance.get_bjd_data(bjd_cd='seoulsi gangnamgu samsungdong') # 숫자 문자열이 아닌 문자열
        with self.assertRaises(ValueError): self.instance.get_bjd_data(bjd_cd='123456789') # 10자리가 아닌 숫자 문자열
        with self.assertRaises(ValueError): self.instance.get_bjd_data(bjd_cd='12345678910') # 10자리가 아닌 숫자 문자열
        with self.assertRaises(ValueError): self.instance.get_bjd_data(bjd_cd='123456789A') # 10자리이지만 알파벳이 포함된 문자열
        with self.assertRaises(ValueError): self.instance.get_bjd_data(bjd_cd='123456789 ') # 10자리이지만 공백이 포함된 문자열
        with self.assertRaises(ValueError): self.instance.get_bjd_data(bjd_cd='123456789#') # 10자리이지만 특수문자가 포함된 문자열

        res = self.instance.get_bjd_data(bjd_cd='1168010500') # 정상적인 법정동코드 입력값
        self.assertIsInstance(res, dict)
        self.assertIsInstance(res.get('error'), bool)
        self.assertIsInstance(res.get('sido_nm'), (str, type(None)))
        self.assertIsInstance(res.get('sgg_nm'), (str, type(None)))
        self.assertIsInstance(res.get('emd_nm'), (str, type(None)))
        # self.assertTrue(res.get('ri_nm'), Optional[str])
        self.assertIsInstance(res.get('full_bjd_nm'), (str, type(None)))
        self.assertIsInstance(res.get('created_dt'), (str, type(None)))
        # self.assertTrue(res.get('deleted_dt'), Optional[str])
        self.assertIsInstance(res.get('base_dt'), str)
        self.assertIsNotNone(res.get('error'), bool)
        self.assertIsNotNone(res.get('sido_nm'), Optional[str])
        self.assertIsNotNone(res.get('sgg_nm'), Optional[str])
        self.assertIsNotNone(res.get('emd_nm'), Optional[str])
        self.assertIsNone(res.get('ri_nm'), Optional[str]) # 테스트 법정동코드 1168010500 에는 리가 없으므로 == None
        self.assertIsNotNone(res.get('full_bjd_nm'), Optional[str])
        self.assertIsNotNone(res.get('created_dt'), Optional[str])
        self.assertIsNone(res.get('deleted_dt'), Optional[str]) # 현재 존재하는 법정동의 경우 deleted_dt == None
        self.assertIsNotNone(res.get('base_dt'), str)
        self.assertEqual(res, {
            'error': False,
            'sido_nm': '서울특별시',
            'sgg_nm': '강남구',
            'emd_nm': '삼성동',
            'ri_nm': None,
            'full_bjd_nm': '서울특별시 강남구 삼성동',
            'created_dt': '1988-04-23',
            'deleted_dt': None,
            'base_dt': self.instance.base_dt_print, # base_dt_print 는 업데이트 되므로 self.instance.base_dt_print 로 적용
            'msg': ''
        })

        res = self.instance.get_bjd_data(bjd_cd='1234567890') # 비정상적인 법정동코드 입력값
        self.assertIsInstance(res, dict)
        self.assertIsInstance(res.get('error'), bool)
        # self.assertTrue(res.get('sido_nm'), Optional[str])
        # self.assertTrue(res.get('sgg_nm'), Optional[str])
        # self.assertTrue(res.get('emd_nm'), Optional[str])
        # self.assertTrue(res.get('ri_nm'), Optional[str])
        # self.assertTrue(res.get('full_bjd_nm'), Optional[str])
        # self.assertTrue(res.get('created_dt'), Optional[str])
        # self.assertTrue(res.get('deleted_dt'), Optional[str])
        self.assertIsInstance(res.get('base_dt'), str)
        self.assertIsNotNone(res.get('error'), bool)
        self.assertIsNone(res.get('sido_nm'), Optional[str]) # 비정상적인 법정동코드의 경우 None
        self.assertIsNone(res.get('sgg_nm'), Optional[str]) # 비정상적인 법정동코드의 경우 None
        self.assertIsNone(res.get('emd_nm'), Optional[str]) # 비정상적인 법정동코드의 경우 None
        self.assertIsNone(res.get('ri_nm'), Optional[str]) # 비정상적인 법정동코드의 경우 None
        self.assertIsNone(res.get('full_bjd_nm'), Optional[str]) # 비정상적인 법정동코드의 경우 None
        self.assertIsNone(res.get('created_dt'), Optional[str]) # 비정상적인 법정동코드의 경우 None
        self.assertIsNone(res.get('deleted_dt'), Optional[str]) # 현재 존재하는 법정동의 경우 deleted_dt == None
        self.assertIsNotNone(res.get('base_dt'), str)
        self.assertEqual(res, {
            'error': True,
            'sido_nm': None,
            'sgg_nm': None,
            'emd_nm': None,
            'ri_nm': None,
            'full_bjd_nm': None,
            'created_dt': None,
            'deleted_dt': None,
            'base_dt': self.instance.base_dt_print, # base_dt_print 는 업데이트 되므로 self.instance.base_dt_print 로 적용
            'msg': "'1234567890' is not a valid legal district code"
        })


    def sub_test_validate_jibun(
        self,
        jibun: str,
        result: bool
    ):
        """
        _validate_jibun 함수 테스트 서브 메소드
            - assertIsInstance() 테스트
            - assertIsNotNone() 테스트
            - assertEqual() 테스트
        """
        res = self.instance._validate_jibun(jibun)
        self.assertIsInstance(res.get("error"), bool)
        self.assertIsInstance(res.get("msg"), str)
        self.assertIsNotNone(res)
        self.assertIsNotNone(res.get("error"))
        self.assertIsNotNone(res.get("msg"))
        self.assertEqual(res.get("error"), result)


    def test_validate_jibun(self):
        """
        _validate_jibun 함수 테스트 메소드

        - _validate_jibun 함수 예외처리 테스트(올바르지 않은 지번 형식 문자열 제공)
            - _validate_jibun 함수 예외처리 테스트(ValueError 입력값이 적절한 형식의 문자열이 아닌 경우)
            - _validate_jibun 함수 jibun 입력값 적절한 형태 = re.compile(r'^(산\s*)?\d{1,4}-\d{1,4}$|^(산\s*)?\d{1,4}$|^\d{1,4}-\d{1,4}$|^\d{1,4}$')

        - _validate_jibun 함수 리턴값 테스트(올바른 지번 형식 문자열 제공)
        """

        self.sub_test_validate_jibun(jibun='산 00000', result=True)
        self.sub_test_validate_jibun(jibun='산 000000', result=True)
        self.sub_test_validate_jibun(jibun='산 0000000', result=True)
        self.sub_test_validate_jibun(jibun='산 00000000', result=True)
        self.sub_test_validate_jibun(jibun='산 000000000', result=True)
        self.sub_test_validate_jibun(jibun='산 0000000000', result=True)
        self.sub_test_validate_jibun(jibun='산 11111-2', result=True)
        self.sub_test_validate_jibun(jibun='산 33333-44', result=True)
        self.sub_test_validate_jibun(jibun='산 55555-666', result=True)
        self.sub_test_validate_jibun(jibun='산 77777-8888', result=True)
        self.sub_test_validate_jibun(jibun='산 99999-00000', result=True)
        self.sub_test_validate_jibun(jibun='산 7777-88888', result=True)
        self.sub_test_validate_jibun(jibun='산 555-66666', result=True)
        self.sub_test_validate_jibun(jibun='산 33-44444', result=True)
        self.sub_test_validate_jibun(jibun='산 1-22222', result=True)
        self.sub_test_validate_jibun(jibun='산00000', result=True)
        self.sub_test_validate_jibun(jibun='산000000', result=True)
        self.sub_test_validate_jibun(jibun='산0000000', result=True)
        self.sub_test_validate_jibun(jibun='산00000000', result=True)
        self.sub_test_validate_jibun(jibun='산000000000', result=True)
        self.sub_test_validate_jibun(jibun='산0000000000', result=True)
        self.sub_test_validate_jibun(jibun='산11111-2', result=True)
        self.sub_test_validate_jibun(jibun='산33333-44', result=True)
        self.sub_test_validate_jibun(jibun='산55555-666', result=True)
        self.sub_test_validate_jibun(jibun='산77777-8888', result=True)
        self.sub_test_validate_jibun(jibun='산99999-00000', result=True)
        self.sub_test_validate_jibun(jibun='산7777-88888', result=True)
        self.sub_test_validate_jibun(jibun='산555-66666', result=True)
        self.sub_test_validate_jibun(jibun='산33-44444', result=True)
        self.sub_test_validate_jibun(jibun='산1-22222', result=True)
        self.sub_test_validate_jibun(jibun='산-1000', result=True)
        self.sub_test_validate_jibun(jibun='산 -1000', result=True)
        self.sub_test_validate_jibun(jibun='산  -1000', result=True)
        self.sub_test_validate_jibun(jibun='산   -1000', result=True)
        self.sub_test_validate_jibun(jibun='산1000-', result=True)
        self.sub_test_validate_jibun(jibun='산 1000-', result=True)
        self.sub_test_validate_jibun(jibun='산  1000-', result=True)
        self.sub_test_validate_jibun(jibun='산   1000-', result=True)
        self.sub_test_validate_jibun(jibun='산 10000', result=True)
        self.sub_test_validate_jibun(jibun='a', result=True)
        self.sub_test_validate_jibun(jibun='a000', result=True)
        self.sub_test_validate_jibun(jibun='000a', result=True)
        self.sub_test_validate_jibun(jibun='a-1000', result=True)
        self.sub_test_validate_jibun(jibun='1000-a', result=True)
        self.sub_test_validate_jibun(jibun='ㄱ', result=True)
        self.sub_test_validate_jibun(jibun='ㄱ000', result=True)
        self.sub_test_validate_jibun(jibun='000ㄱ', result=True)
        self.sub_test_validate_jibun(jibun='ㄱ-1000', result=True)
        self.sub_test_validate_jibun(jibun='1000-ㄱ', result=True)
        self.sub_test_validate_jibun(jibun='나', result=True)
        self.sub_test_validate_jibun(jibun='나000', result=True)
        self.sub_test_validate_jibun(jibun='000나', result=True)
        self.sub_test_validate_jibun(jibun='나-1000', result=True)
        self.sub_test_validate_jibun(jibun='1000-나', result=True)
        self.sub_test_validate_jibun(jibun='선 1000-1000', result=True)
        self.sub_test_validate_jibun(jibun='순 1000-1000', result=True)
        self.sub_test_validate_jibun(jibun='상 1000-1000', result=True)
        self.sub_test_validate_jibun(jibun='선산 1000-1000', result=True)
        self.sub_test_validate_jibun(jibun='나산 1000-1000', result=True)
        self.sub_test_validate_jibun(jibun='산나 1000-1000', result=True)
        self.sub_test_validate_jibun(jibun='산산 1000-1000', result=True)
        self.sub_test_validate_jibun(jibun='산산산 1000-1000', result=True)


    def test_get_mountain_cd(self):
        """
        _get_mountain_cd 함수 테스트 메소드

        - _get_mountain_cd 함수 리턴값 테스트(올바른 지번 형식 문자열 제공)
        """

        res = self.instance._get_mountain_cd(jibun='산0000-0000')
        self.assertIsInstance(res, tuple)
        self.assertIsNotNone(res)
        self.assertEqual(res, ('0000-0000', '2'))

        res = self.instance._get_mountain_cd(jibun='0000-0000')
        self.assertIsInstance(res, tuple)
        self.assertIsNotNone(res)
        self.assertEqual(res, ('0000-0000', '1'))


    def sub_test_get_jibun_datas(
        self,
        jibun: str,
        result: Tuple[str]
    ):
        """
        _get_jibun_datas 함수 테스트 서브 메소드
            - assertIsInstance() 테스트(리턴값, tuple 개별 객체)
            - assertIsNotNone() 테스트(리턴값, tuple 개별 객체)
            - assertEqual() 테스트
        """
        res = self.instance._get_jibun_datas(jibun)
        self.assertIsInstance(res, tuple)
        self.assertIsNotNone(res)
        for item in res:
            self.assertIsNotNone(item)
            self.assertIsInstance(item, str) 
        self.assertEqual(res, result)


    def test_get_jibun_datas(self):
        """
        _get_jibun_datas 함수 테스트 메소드

        - _get_jibun_datas 함수 리턴값 테스트(올바른 지번 형식 문자열 제공)
        """

        self.sub_test_get_jibun_datas(jibun='0', result=('00000000', '0', '0'))
        self.sub_test_get_jibun_datas(jibun='0', result=('00000000', '0', '0'))
        self.sub_test_get_jibun_datas(jibun='0-0', result=('00000000', '0', '0'))
        self.sub_test_get_jibun_datas(jibun='0000', result=('00000000', '0', '0'))
        self.sub_test_get_jibun_datas(jibun='0000-0000', result=('00000000', '0', '0'))
        self.sub_test_get_jibun_datas(jibun='1', result=('00010000', '1', '0'))
        self.sub_test_get_jibun_datas(jibun='1-1', result=('00010001', '1', '1'))
        self.sub_test_get_jibun_datas(jibun='1111', result=('11110000', '1111', '0'))
        self.sub_test_get_jibun_datas(jibun='1111-1111', result=('11111111', '1111', '1111'))
        self.sub_test_get_jibun_datas(jibun='10', result=('00100000', '10', '0'))
        self.sub_test_get_jibun_datas(jibun='10-10', result=('00100010', '10', '10'))
        self.sub_test_get_jibun_datas(jibun='101', result=('01010000', '101', '0'))
        self.sub_test_get_jibun_datas(jibun='101-101', result=('01010101', '101', '101'))
        self.sub_test_get_jibun_datas(jibun='1010', result=('10100000', '1010', '0'))
        self.sub_test_get_jibun_datas(jibun='1010-1010', result=('10101010', '1010', '1010'))


    def sub_test_validate_pnu(
        self,
        pnu,
        result: dict
    ):
        """
        _validate_pnu 함수 테스트 서브 메소드
            - assertIsInstance() 테스트(리턴값, dict)
            - assertIsNotNone() 테스트(리턴값, dict 개별 객체)
            - assertEqual() 테스트
        """
        res = self.instance._validate_pnu(pnu)
        self.assertIsInstance(res, dict)
        self.assertIsNotNone(res)
        self.assertIsInstance(res.get("error"), bool)
        self.assertIsInstance(res.get("msg"), str)
        self.assertIsNotNone(res.get("error"))
        self.assertIsNotNone(res.get("msg"))
        self.assertEqual(res, result)


    def test_validate_pnu(self):
        """
        _validate_pnu 함수 테스트 메소드

        - _validate_pnu 함수 예외처리 테스트(올바르지 않은 지번 형식 문자열 제공)
            - _validate_pnu 함수 예외처리 테스트(ValueError 입력값이 적절한 형식의 문자열이 아닌 경우)
            - _validate_pnu 함수 pnu 입력값 적절한 형태 re.compile(r'^\d{19}$')

        - _validate_pnu 함수 리턴값 테스트(올바른 pnu 형식 문자열 제공)
        """

        self.sub_test_validate_pnu(
            pnu=1234567890123456789,
            result = {
                'error': True,
                'msg': "Invalid 'pnu' format. Please follow the specified format."
            }
        )
        self.sub_test_validate_pnu(
            pnu='12345678901234567890',
            result = {
                'error': True,
                'msg': "Invalid 'pnu' format. Please follow the specified format."
            }
        )
        self.sub_test_validate_pnu(
            pnu='1234567890123456789a',
            result = {
                'error': True,
                'msg': "Invalid 'pnu' format. Please follow the specified format."
            }
        )
        self.sub_test_validate_pnu(
            pnu='1234567890123456789',
            result = {
                'error': False,
                'msg': ''
            }
        )


    def sub_test_clean_bracket_and_content(
        self,
        string: str,
        result: str
    ):
        """
        _clean_bracket_and_content 함수 테스트 서브 메소드
            - assertIsInstance() 테스트(리턴값, str)
            - assertIsNotNone() 테스트(리턴값)
            - assertEqual() 테스트
        """

        res = self.instance._clean_bracket_and_content(string)
        self.assertIsInstance(res, str)
        self.assertIsNotNone(res)
        self.assertEqual(res, result)


    def test_clean_bracket_and_content(self):
        """
        _clean_bracket_and_content 함수 테스트 메소드
        """

        self.sub_test_clean_bracket_and_content(string='서울특별시 강남구 삼성동 1 (삼성동)', result='서울특별시 강남구 삼성동 1')
        self.sub_test_clean_bracket_and_content(string='서울특별시 강남구 삼성동 1 ()', result='서울특별시 강남구 삼성동 1')
        self.sub_test_clean_bracket_and_content(string='서울특별시 강남구 삼성동 1 [삼성동]', result='서울특별시 강남구 삼성동 1')
        self.sub_test_clean_bracket_and_content(string='서울특별시 강남구 삼성동 1 []', result='서울특별시 강남구 삼성동 1')


    def sub_test_split_main_and_detail_address(
        self,
        address: str,
        result: dict
    ):
        """
        _split_main_and_detail_address 함수 테스트 서브 메소드
            - assertIsInstance() 테스트(리턴값, dict)
            - assertIsNotNone() 테스트(리턴값, dict 개별 객체)
            - assertEqual() 테스트
        """
        res = self.instance._split_main_and_detail_address(address)
        self.assertIsInstance(res, dict)
        self.assertIsInstance(res.get("error"), bool)
        self.assertIsInstance(res.get("msg"), str)
        self.assertIsNotNone(res)
        self.assertIsNotNone(res.get("error"))
        self.assertIsNotNone(res.get("msg"))
        self.assertEqual(res, result)


    def test_split_main_and_detail_address(self):
        """
        _split_main_and_detail_address 함수 테스트 메소드
        """

        self.sub_test_split_main_and_detail_address(
            address='서울특별시 강남구 삼성동 1 에이빌딩 비동 씨호',
            result={
                'error': False,
                'main_address': '서울특별시 강남구 삼성동 1',
                'etc_main_address': '',
                'detail_address': '에이빌딩 비동 씨호',
                'base_dt': self.instance.base_dt_print, # base_dt_print 는 업데이트 되므로 self.instance.base_dt_print 로 적용
                'msg': ''
            }
        )
        self.sub_test_split_main_and_detail_address(
            address='서울특별시 강남구 삼성동 1-1 에이빌딩 비동 씨호',
            result={
                'error': False,
                'main_address': '서울특별시 강남구 삼성동 1-1',
                'etc_main_address': '',
                'detail_address': '에이빌딩 비동 씨호',
                'base_dt': self.instance.base_dt_print, # base_dt_print 는 업데이트 되므로 self.instance.base_dt_print 로 적용
                'msg': ''
            }
        )
        self.sub_test_split_main_and_detail_address(
            address='서울특별시 강남구 삼성동 1 외 1필지 에이빌딩 비동 씨호',
            result={
                'error': False,
                'main_address': '서울특별시 강남구 삼성동 1',
                'etc_main_address': '외 1필지 ',
                'detail_address': '에이빌딩 비동 씨호',
                'base_dt': self.instance.base_dt_print, # base_dt_print 는 업데이트 되므로 self.instance.base_dt_print 로 적용
                'msg': ''
            }
        )


    def sub_test_extract_bjd_from_address(
        self,
        main_address: str,
        result: str
    ):
        """
        _extract_bjd_from_address 함수 테스트 서브 메소드
            - assertIsInstance() 테스트(리턴값, str)
            - assertIsNotNone() 테스트(리턴값)
            - assertEqual() 테스트
        """
        res = self.instance._extract_bjd_from_address(main_address)
        self.assertIsInstance(res, str)
        self.assertIsNotNone(res)
        self.assertEqual(res, result)


    def test_extract_bjd_from_address(self):
        """
        _extract_bjd_from_address 함수 테스트 메소드
        """

        self.sub_test_extract_bjd_from_address(main_address='서울특별시 강남구 삼성동 1', result='서울특별시 강남구 삼성동')
        self.sub_test_extract_bjd_from_address(main_address='서울특별시 강남구 삼성동 1-1', result='서울특별시 강남구 삼성동')
        self.sub_test_extract_bjd_from_address(main_address='서울특별시 강남구 삼성동 산 1', result='서울특별시 강남구 삼성동')
        self.sub_test_extract_bjd_from_address(main_address='서울특별시 강남구 삼성동 산 1-1', result='서울특별시 강남구 삼성동')
        self.sub_test_extract_bjd_from_address(main_address='서울특별시 강남구 삼성동 산1', result='서울특별시 강남구 삼성동')
        self.sub_test_extract_bjd_from_address(main_address='서울특별시 강남구 삼성동 산1-1', result='서울특별시 강남구 삼성동')


    def sub_test_generate_pnu(
        self,
        bjd_cd,
        jibun,
        result: bool
    ):
        """
        _generate_pnu 함수 테스트 서브 메소드
            - assertIsInstance() 테스트
            - assertIsNotNone() 테스트
            - assertEqual() 테스트
        """
        res = self.instance.generate_pnu(bjd_cd, jibun)
        self.assertIsInstance(res.get("error"), bool)
        self.assertIsInstance(res.get("msg"), str)
        self.assertIsNotNone(res)
        self.assertIsNotNone(res.get("error"))
        self.assertIsNotNone(res.get("msg"))
        self.assertEqual(res.get("error"), result)


    def test_generate_pnu(self):
        """
        generate_pnu 함수 테스트 메소드

        - generate_pnu 함수 예외처리 테스트
            - generate_pnu 함수 예외처리 테스트(TypeError 입력값(bjd_cd or jibun)이 문자열이 아닌 int type)
            - generate_pnu 함수 예외처리 테스트(TypeError 입력값(bjd_cd or jibun)이 문자열이 아닌 float type)
            - generate_pnu 함수 예외처리 테스트(TypeError 입력값(bjd_cd or jibun)이 문자열이 아닌 None type)
            - generate_pnu 함수 예외처리 테스트(TypeError 입력값(bjd_cd or jibun)이 문자열이 아닌 bool type)
            - generate_pnu 함수 예외처리 테스트(ValueError 입력값(bjd_cd)이 적절한 형식(10자리 숫자문자열)의 문자열이 아닌 경우들)
            - generate_pnu 함수 예외처리 테스트(ValueError 입력값(jibun)이 적절한 형식의 문자열이 아닌 경우들)

        - generate_pnu 함수 리턴값 테스트(올바른 법정동 문자열 및 지번 제공)
            - generate_pnu 함수 리턴값 타입 테스트
            - generate_pnu 함수 리턴값 error 타입 테스트
            - generate_pnu 함수 리턴값 pnu 타입 테스트
            - generate_pnu 함수 리턴값 bjd_cd 타입 테스트
            - generate_pnu 함수 리턴값 mountain_cd 타입 테스트
            - generate_pnu 함수 리턴값 bunji_cd 타입 테스트
            - generate_pnu 함수 리턴값 bjd_datas 타입 테스트
            - generate_pnu 함수 리턴값 bun 타입 테스트
            - generate_pnu 함수 리턴값 ji 타입 테스트
            - generate_pnu 함수 리턴값 msg 타입 테스트
            - generate_pnu 함수 리턴값 base_dt 타입 테스트
            - generate_pnu 함수 리턴값 error 값이 None 이 아닌지 테스트
            - generate_pnu 함수 리턴값 pnu 값이 None 이 아닌지 테스트
            - generate_pnu 함수 리턴값 bjd_cd 값이 None 이 아닌지 테스트
            - generate_pnu 함수 리턴값 mountain_cd 값이 None 이 아닌지 테스트
            - generate_pnu 함수 리턴값 bunji_cd 값이 None 이 아닌지 테스트
            - generate_pnu 함수 리턴값 bjd_datas 값이 None 이 아닌지 테스트
            - generate_pnu 함수 리턴값 bun 값이 None 이 아닌지 테스트
            - generate_pnu 함수 리턴값 ji 값이 None 이 아닌지 테스트
            - generate_pnu 함수 리턴값 msg 값이 None 이 아닌지 테스트
            - generate_pnu 함수 리턴값 base_dt 값이 None 이 아닌지 테스트
            - generate_pnu 함수 리턴값 일치 테스트

        - generate_pnu 함수 리턴값 테스트(형식은 맞지만 존재하지 않는 법정동 문자열 및 정상적인 지번 제공)
            - generate_pnu 함수 리턴값 타입 테스트
            - generate_pnu 함수 리턴값 error 타입 테스트
            - generate_pnu 함수 리턴값 pnu 타입 테스트
            - generate_pnu 함수 리턴값 bjd_cd 타입 테스트
            - generate_pnu 함수 리턴값 mountain_cd 타입 테스트
            - generate_pnu 함수 리턴값 bunji_cd 타입 테스트
            - generate_pnu 함수 리턴값 bjd_datas 타입 테스트
            - generate_pnu 함수 리턴값 bun 타입 테스트
            - generate_pnu 함수 리턴값 ji 타입 테스트
            - generate_pnu 함수 리턴값 msg 타입 테스트
            - generate_pnu 함수 리턴값 base_dt 타입 테스트
            - generate_pnu 함수 리턴값 error 값이 None 이 아닌지 테스트
            - generate_pnu 함수 리턴값 pnu 값이 None 이 아닌지 테스트
            - generate_pnu 함수 리턴값 bjd_cd 값이 None 이 아닌지 테스트
            - generate_pnu 함수 리턴값 mountain_cd 값이 None 이 아닌지 테스트
            - generate_pnu 함수 리턴값 bunji_cd 값이 None 이 아닌지 테스트
            - generate_pnu 함수 리턴값 bjd_datas 값이 None 이 아닌지 테스트
            - generate_pnu 함수 리턴값 bun 값이 None 이 아닌지 테스트
            - generate_pnu 함수 리턴값 ji 값이 None 이 아닌지 테스트
            - generate_pnu 함수 리턴값 msg 값이 None 이 아닌지 테스트
            - generate_pnu 함수 리턴값 base_dt 값이 None 이 아닌지 테스트
            - generate_pnu 함수 리턴값 일치 테스트
        """

        with self.assertRaises(TypeError): self.instance.generate_pnu(bjd_cd=0, jibun='')
        with self.assertRaises(TypeError): self.instance.generate_pnu(bjd_cd=0.1, jibun='')
        with self.assertRaises(TypeError): self.instance.generate_pnu(bjd_cd=None, jibun='')
        with self.assertRaises(TypeError): self.instance.generate_pnu(bjd_cd=True, jibun='')
        with self.assertRaises(TypeError): self.instance.generate_pnu(bjd_cd=False, jibun='')
        with self.assertRaises(TypeError): self.instance.generate_pnu(bjd_cd='', jibun=0)
        with self.assertRaises(TypeError): self.instance.generate_pnu(bjd_cd='', jibun=0.1)
        with self.assertRaises(TypeError): self.instance.generate_pnu(bjd_cd='', jibun=None)
        with self.assertRaises(TypeError): self.instance.generate_pnu(bjd_cd='', jibun=True)
        with self.assertRaises(TypeError): self.instance.generate_pnu(bjd_cd='', jibun=False)

        with self.assertRaises(ValueError): self.instance.generate_pnu(bjd_cd='서울특별시 강남구 삼성동', jibun='0000-0000') # 숫자 문자열이 아닌 문자열
        with self.assertRaises(ValueError): self.instance.generate_pnu(bjd_cd='seoulsi gangnamgu samsungdong', jibun='0000-0000') # 숫자 문자열이 아닌 문자열
        with self.assertRaises(ValueError): self.instance.generate_pnu(bjd_cd='123456789', jibun='0000-0000') # 10자리가 아닌 숫자 문자열
        with self.assertRaises(ValueError): self.instance.generate_pnu(bjd_cd='12345678910', jibun='0000-0000') # 10자리가 아닌 숫자 문자열
        with self.assertRaises(ValueError): self.instance.generate_pnu(bjd_cd='123456789A', jibun='0000-0000') # 10자리이지만 알파벳이 포함된 문자열
        with self.assertRaises(ValueError): self.instance.generate_pnu(bjd_cd='123456789', jibun='0000-0000') # 10자리이지만 공백이 포함된 문자열
        with self.assertRaises(ValueError): self.instance.generate_pnu(bjd_cd='123456789', jibun='0000-0000') # 10자리이지만 특수문자가 포함된 문자열

        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='산 00000', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='산 000000', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='산 0000000', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='산 00000000', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='산 000000000', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='산 0000000000', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='산 11111-2', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='산 33333-44', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='산 55555-666', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='산 77777-8888', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='산 99999-00000', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='산 7777-88888', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='산 555-66666', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='산 33-44444', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='산 1-22222', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='산00000', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='산000000', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='산0000000', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='산00000000', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='산000000000', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='산0000000000', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='산11111-2', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='산33333-44', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='산55555-666', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='산77777-8888', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='산99999-00000', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='산7777-88888', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='산555-66666', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='산33-44444', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='산1-22222', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='산-1000', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='산 -1000', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='산  -1000', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='산   -1000', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='산1000-', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='산 1000-', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='산  1000-', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='산   1000-', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='산 10000', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='a', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='a000', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='000a', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='a-1000', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='1000-a', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='ㄱ', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='ㄱ000', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='000ㄱ', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='ㄱ-1000', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='1000-ㄱ', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='나', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='나000', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='000나', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='나-1000', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='1000-나', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='선 1000-1000', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='순 1000-1000', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='상 1000-1000', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='선산 1000-1000', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='나산 1000-1000', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='산나 1000-1000', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='산산 1000-1000', result=True)
        self.sub_test_generate_pnu(bjd_cd='1168010500', jibun='산산산 1000-1000', result=True)

        res = self.instance.generate_pnu(bjd_cd='1168010500', jibun='1-1') # 정상적인 법정동코드 및 지번 입력값
        self.assertIsInstance(res, dict)
        self.assertIsInstance(res.get('error'), bool)
        self.assertIsInstance(res.get('pnu'), str)
        self.assertIsInstance(res.get('bjd_cd'), str)
        self.assertIsInstance(res.get('mountain_cd'), str)
        self.assertIsInstance(res.get('bunji_cd'), str)
        self.assertIsInstance(res.get('bjd_datas'), dict)
        self.assertIsInstance(res.get('bun'), str)
        self.assertIsInstance(res.get('ji'), str)
        self.assertIsInstance(res.get('msg'), str)
        self.assertIsInstance(res.get('base_dt'), str)
        self.assertIsNotNone(res.get('error'))
        self.assertIsNotNone(res.get('pnu'))
        self.assertIsNotNone(res.get('bjd_cd'))
        self.assertIsNotNone(res.get('mountain_cd'))
        self.assertIsNotNone(res.get('bunji_cd'))
        self.assertIsNotNone(res.get('bjd_datas'))
        self.assertIsNotNone(res.get('bun'))
        self.assertIsNotNone(res.get('ji'))
        self.assertIsNotNone(res.get('base_dt'))
        self.assertIsNotNone(res.get('msg'))
        self.assertEqual(res, {
            'error': False,
            'pnu': '1168010500100010001',
            'bjd_cd': '1168010500',
            'mountain_cd': '1',
            'bunji_cd': '00010001',
            'bjd_datas': {
                'error': False,
                'sido_nm': '서울특별시',
                'sgg_nm': '강남구',
                'emd_nm': '삼성동',
                'ri_nm': None,
                'full_bjd_nm': '서울특별시 강남구 삼성동',
                'created_dt': '1988-04-23',
                'deleted_dt': None,
                'base_dt': self.instance.base_dt_print, # base_dt_print 는 업데이트 되므로 self.instance.base_dt_print 로 적용
                'msg': ''
            },
            'bun': '1',
            'ji': '1',
            'base_dt': self.instance.base_dt_print, # base_dt_print 는 업데이트 되므로 self.instance.base_dt_print 로 적용
            'msg': '',
        })

        res = self.instance.generate_pnu(bjd_cd='1234567890', jibun='1-1') # 형식은 맞지만 존재하지않는 법정동코드 및 정상적인 지번 입력값
        self.assertIsInstance(res, dict)
        self.assertIsInstance(res.get('error'), bool)
        # self.assertIsInstance(res.get('pnu'), None)
        # self.assertIsInstance(res.get('bjd_cd'), None)
        # self.assertIsInstance(res.get('mountain_cd'), None)
        # self.assertIsInstance(res.get('bunji_cd'), None)
        self.assertIsInstance(res.get('bjd_datas'), dict)
        # self.assertIsInstance(res.get('bun'), None)
        # self.assertIsInstance(res.get('ji'), None)
        self.assertIsInstance(res.get('msg'), str)
        self.assertIsInstance(res.get('base_dt'), str)
        self.assertIsNotNone(res.get('error'))
        self.assertIsNone(res.get('pnu'))
        self.assertIsNone(res.get('bjd_cd'))
        self.assertIsNone(res.get('mountain_cd'))
        self.assertIsNone(res.get('bunji_cd'))
        self.assertIsNotNone(res.get('bjd_datas'))
        self.assertIsNone(res.get('bun'))
        self.assertIsNone(res.get('ji'))
        self.assertIsNotNone(res.get('base_dt'))
        self.assertIsNotNone(res.get('msg'))
        self.assertEqual(res, {
            'error': True,
            'pnu': None,
            'bjd_cd': None,
            'mountain_cd': None,
            'bunji_cd': None,
            'bjd_datas': {
                'error': True,
                'sido_nm': None,
                'sgg_nm': None,
                'emd_nm': None,
                'ri_nm': None,
                'full_bjd_nm': None,
                'created_dt': None,
                'deleted_dt': None,
                'base_dt': self.instance.base_dt_print, # base_dt_print 는 업데이트 되므로 self.instance.base_dt_print 로 적용
                'msg': "'1234567890' is not a valid legal district code"
            },
            'bun': None,
            'ji': None,
            'base_dt': self.instance.base_dt_print, # base_dt_print 는 업데이트 되므로 self.instance.base_dt_print 로 적용
            'msg': "'1234567890' is not a valid legal district code",
        })


    def sub_test_generate_pnu_from_bjd_nm(
        self,
        bjd_nm,
        jibun,
        result: bool
    ):
        """
        _generate_pnu 함수 테스트 서브 메소드
            - assertIsInstance() 테스트
            - assertIsNotNone() 테스트
            - assertEqual() 테스트
        """
        res = self.instance.generate_pnu_from_bjd_nm(bjd_nm, jibun)
        self.assertIsInstance(res.get("error"), bool)
        self.assertIsInstance(res.get("msg"), str)
        self.assertIsNotNone(res)
        self.assertIsNotNone(res.get("error"))
        self.assertIsNotNone(res.get("msg"))
        self.assertEqual(res.get("error"), result)


    def test_generate_pnu_from_bjd_nm(self):
        """
        generate_pnu_from_bjd_nm 함수 테스트 메소드

        - generate_pnu_from_bjd_nm 함수 예외처리 테스트
            - generate_pnu_from_bjd_nm 함수 예외처리 테스트(TypeError 입력값(bjd_cd or jibun)이 문자열이 아닌 int type)
            - generate_pnu_from_bjd_nm 함수 예외처리 테스트(TypeError 입력값(bjd_cd or jibun)이 문자열이 아닌 float type)
            - generate_pnu_from_bjd_nm 함수 예외처리 테스트(TypeError 입력값(bjd_cd or jibun)이 문자열이 아닌 None type)
            - generate_pnu_from_bjd_nm 함수 예외처리 테스트(TypeError 입력값(bjd_cd or jibun)이 문자열이 아닌 bool type)
            - generate_pnu_from_bjd_nm 함수 예외처리 테스트(ValueError 입력값(bjd_cd)이 적절한 형식(10자리 숫자문자열)의 문자열이 아닌 경우들)
            - generate_pnu_from_bjd_nm 함수 예외처리 테스트(ValueError 입력값(jibun)이 적절한 형식의 문자열이 아닌 경우들)

        - generate_pnu_from_bjd_nm 함수 리턴값 테스트(올바른 법정동 문자열 및 지번 제공)
            - generate_pnu_from_bjd_nm 함수 리턴값 타입 테스트
            - generate_pnu_from_bjd_nm 함수 리턴값 error 타입 테스트
            - generate_pnu_from_bjd_nm 함수 리턴값 pnu 타입 테스트
            - generate_pnu_from_bjd_nm 함수 리턴값 bjd_cd 타입 테스트
            - generate_pnu_from_bjd_nm 함수 리턴값 mountain_cd 타입 테스트
            - generate_pnu_from_bjd_nm 함수 리턴값 bunji_cd 타입 테스트
            - generate_pnu_from_bjd_nm 함수 리턴값 bjd_datas 타입 테스트
            - generate_pnu_from_bjd_nm 함수 리턴값 bun 타입 테스트
            - generate_pnu_from_bjd_nm 함수 리턴값 ji 타입 테스트
            - generate_pnu_from_bjd_nm 함수 리턴값 msg 타입 테스트
            - generate_pnu_from_bjd_nm 함수 리턴값 base_dt 타입 테스트
            - generate_pnu_from_bjd_nm 함수 리턴값 error 값이 None 이 아닌지 테스트
            - generate_pnu_from_bjd_nm 함수 리턴값 pnu 값이 None 이 아닌지 테스트
            - generate_pnu_from_bjd_nm 함수 리턴값 bjd_cd 값이 None 이 아닌지 테스트
            - generate_pnu_from_bjd_nm 함수 리턴값 mountain_cd 값이 None 이 아닌지 테스트
            - generate_pnu_from_bjd_nm 함수 리턴값 bunji_cd 값이 None 이 아닌지 테스트
            - generate_pnu_from_bjd_nm 함수 리턴값 bjd_datas 값이 None 이 아닌지 테스트
            - generate_pnu_from_bjd_nm 함수 리턴값 bun 값이 None 이 아닌지 테스트
            - generate_pnu_from_bjd_nm 함수 리턴값 ji 값이 None 이 아닌지 테스트
            - generate_pnu_from_bjd_nm 함수 리턴값 msg 값이 None 이 아닌지 테스트
            - generate_pnu_from_bjd_nm 함수 리턴값 base_dt 값이 None 이 아닌지 테스트
            - generate_pnu_from_bjd_nm 함수 리턴값 일치 테스트

        - generate_pnu_from_bjd_nm 함수 리턴값 테스트(형식은 맞지만 존재하지 않는 법정동 문자열 및 정상적인 지번 제공)
            - generate_pnu_from_bjd_nm 함수 리턴값 타입 테스트
            - generate_pnu_from_bjd_nm 함수 리턴값 error 타입 테스트
            - generate_pnu_from_bjd_nm 함수 리턴값 pnu 타입 테스트
            - generate_pnu_from_bjd_nm 함수 리턴값 bjd_cd 타입 테스트
            - generate_pnu_from_bjd_nm 함수 리턴값 mountain_cd 타입 테스트
            - generate_pnu_from_bjd_nm 함수 리턴값 bunji_cd 타입 테스트
            - generate_pnu_from_bjd_nm 함수 리턴값 bjd_datas 타입 테스트
            - generate_pnu_from_bjd_nm 함수 리턴값 bun 타입 테스트
            - generate_pnu_from_bjd_nm 함수 리턴값 ji 타입 테스트
            - generate_pnu_from_bjd_nm 함수 리턴값 msg 타입 테스트
            - generate_pnu_from_bjd_nm 함수 리턴값 base_dt 타입 테스트
            - generate_pnu_from_bjd_nm 함수 리턴값 error 값이 None 이 아닌지 테스트
            - generate_pnu_from_bjd_nm 함수 리턴값 pnu 값이 None 이 맞는지 테스트
            - generate_pnu_from_bjd_nm 함수 리턴값 bjd_cd 값이 None 이 맞는지 테스트
            - generate_pnu_from_bjd_nm 함수 리턴값 mountain_cd 값이 None 이 맞는지 테스트
            - generate_pnu_from_bjd_nm 함수 리턴값 bunji_cd 값이 None 이 맞는지 테스트
            - generate_pnu_from_bjd_nm 함수 리턴값 bjd_datas 값이 None 이 맞는지 테스트
            - generate_pnu_from_bjd_nm 함수 리턴값 bun 값이 None 이 맞는지 테스트
            - generate_pnu_from_bjd_nm 함수 리턴값 ji 값이 None 이 맞는지 테스트
            - generate_pnu_from_bjd_nm 함수 리턴값 msg 값이 None 이 아닌지 테스트
            - generate_pnu_from_bjd_nm 함수 리턴값 base_dt 값이 None 이 아닌지 테스트
            - generate_pnu_from_bjd_nm 함수 리턴값 일치 테스트
        """

        with self.assertRaises(TypeError): self.instance.generate_pnu_from_bjd_nm(bjd_nm=0, jibun='')
        with self.assertRaises(TypeError): self.instance.generate_pnu_from_bjd_nm(bjd_nm=0.1, jibun='')
        with self.assertRaises(TypeError): self.instance.generate_pnu_from_bjd_nm(bjd_nm=None, jibun='')
        with self.assertRaises(TypeError): self.instance.generate_pnu_from_bjd_nm(bjd_nm=True, jibun='')
        with self.assertRaises(TypeError): self.instance.generate_pnu_from_bjd_nm(bjd_nm=False, jibun='')
        with self.assertRaises(TypeError): self.instance.generate_pnu_from_bjd_nm(bjd_nm='', jibun=0)
        with self.assertRaises(TypeError): self.instance.generate_pnu_from_bjd_nm(bjd_nm='', jibun=0.1)
        with self.assertRaises(TypeError): self.instance.generate_pnu_from_bjd_nm(bjd_nm='', jibun=None)
        with self.assertRaises(TypeError): self.instance.generate_pnu_from_bjd_nm(bjd_nm='', jibun=True)
        with self.assertRaises(TypeError): self.instance.generate_pnu_from_bjd_nm(bjd_nm='', jibun=False)

        with self.assertRaises(ValueError): self.instance.generate_pnu_from_bjd_nm(bjd_nm='a 서울특별시 강남구 삼성동', jibun='0000-0000') # 알파벳 포함
        with self.assertRaises(ValueError): self.instance.generate_pnu_from_bjd_nm(bjd_nm='seoulsi gangnamgu samsungdong', jibun='0000-0000') # 알파벳 포함
        with self.assertRaises(ValueError): self.instance.generate_pnu_from_bjd_nm(bjd_nm='ㄱ 서울특별시 강남구 삼성동', jibun='0000-0000') # 불완전한 한글 문자열 포함

        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='산 00000', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='산 000000', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='산 0000000', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='산 00000000', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='산 000000000', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='산 0000000000', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='산 11111-2', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='산 33333-44', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='산 55555-666', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='산 77777-8888', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='산 99999-00000', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='산 7777-88888', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='산 555-66666', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='산 33-44444', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='산 1-22222', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='산00000', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='산000000', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='산0000000', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='산00000000', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='산000000000', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='산0000000000', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='산11111-2', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='산33333-44', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='산55555-666', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='산77777-8888', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='산99999-00000', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='산7777-88888', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='산555-66666', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='산33-44444', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='산1-22222', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='산-1000', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='산 -1000', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='산  -1000', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='산   -1000', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='산1000-', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='산 1000-', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='산  1000-', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='산   1000-', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='산 10000', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='a', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='a000', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='000a', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='a-1000', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='1000-a', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='ㄱ', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='ㄱ000', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='000ㄱ', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='ㄱ-1000', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='1000-ㄱ', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='나', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='나000', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='000나', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='나-1000', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='1000-나', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='선 1000-1000', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='순 1000-1000', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='상 1000-1000', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='선산 1000-1000', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='나산 1000-1000', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='산나 1000-1000', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='산산 1000-1000', result=True)
        self.sub_test_generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='산산산 1000-1000', result=True)

        res = self.instance.generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성동', jibun='1-1') # 정상적인 법정동코드 및 지번 입력값
        self.assertIsInstance(res, dict)
        self.assertIsInstance(res.get('error'), bool)
        self.assertIsInstance(res.get('pnu'), str)
        self.assertIsInstance(res.get('bjd_cd'), str)
        self.assertIsInstance(res.get('mountain_cd'), str)
        self.assertIsInstance(res.get('bunji_cd'), str)
        self.assertIsInstance(res.get('bjd_datas'), dict)
        self.assertIsInstance(res.get('bun'), str)
        self.assertIsInstance(res.get('ji'), str)
        self.assertIsInstance(res.get('msg'), str)
        self.assertIsInstance(res.get('base_dt'), str)
        self.assertIsNotNone(res.get('error'))
        self.assertIsNotNone(res.get('pnu'))
        self.assertIsNotNone(res.get('bjd_cd'))
        self.assertIsNotNone(res.get('mountain_cd'))
        self.assertIsNotNone(res.get('bunji_cd'))
        self.assertIsNotNone(res.get('bjd_datas'))
        self.assertIsNotNone(res.get('bun'))
        self.assertIsNotNone(res.get('ji'))
        self.assertIsNotNone(res.get('base_dt'))
        self.assertIsNotNone(res.get('msg'))
        self.assertEqual(res, {
            'error': False,
            'pnu': '1168010500100010001',
            'bjd_cd': '1168010500',
            'mountain_cd': '1',
            'bunji_cd': '00010001',
            'bjd_datas': {
                'error': False,
                'sido_nm': '서울특별시',
                'sgg_nm': '강남구',
                'emd_nm': '삼성동',
                'ri_nm': None,
                'full_bjd_nm': '서울특별시 강남구 삼성동',
                'created_dt': '1988-04-23',
                'deleted_dt': None,
                'base_dt': self.instance.base_dt_print, # base_dt_print 는 업데이트 되므로 self.instance.base_dt_print 로 적용
                'msg': ''
            },
            'bun': '1',
            'ji': '1',
            'msg': '',
            'base_dt': self.instance.base_dt_print, # base_dt_print 는 업데이트 되므로 self.instance.base_dt_print 로 적용
        })

        res = self.instance.generate_pnu_from_bjd_nm(bjd_nm='서울특별시 강남구 삼성1동', jibun='1-1') # 정상적인 법정동코드 및 지번 입력값
        self.assertIsInstance(res, dict)
        self.assertIsInstance(res.get('error'), bool)
        # self.assertIsInstance(res.get('pnu'), str)
        # self.assertIsInstance(res.get('bjd_cd'), str)
        # self.assertIsInstance(res.get('mountain_cd'), str)
        # self.assertIsInstance(res.get('bunji_cd'), str)
        self.assertIsInstance(res.get('bjd_datas'), dict)
        # self.assertIsInstance(res.get('bun'), str)
        # self.assertIsInstance(res.get('ji'), str)
        self.assertIsInstance(res.get('msg'), str)
        self.assertIsInstance(res.get('base_dt'), str)
        self.assertIsNotNone(res.get('error'))
        self.assertIsNone(res.get('pnu'))
        self.assertIsNone(res.get('bjd_cd'))
        self.assertIsNone(res.get('mountain_cd'))
        self.assertIsNone(res.get('bunji_cd'))
        self.assertIsNotNone(res.get('bjd_datas'))
        self.assertIsNone(res.get('bun'))
        self.assertIsNone(res.get('ji'))
        self.assertIsNotNone(res.get('msg'))
        self.assertIsNotNone(res.get('base_dt'))
        self.assertEqual(res, {
            'error': True,
            'pnu': None,
            'bjd_cd': None,
            'mountain_cd': None,
            'bunji_cd': None,
            'bjd_datas': {
                'error': True,
                'sido_nm': None,
                'sgg_nm': None,
                'emd_nm': None,
                'ri_nm': None,
                'full_bjd_nm': None,
                'created_dt': None,
                'deleted_dt': None,
                'base_dt': self.instance.base_dt_print, # base_dt_print 는 업데이트 되므로 self.instance.base_dt_print 로 적용
                'msg': ''},
            'bun': None,
            'ji': None,
            'base_dt': self.instance.base_dt_print, # base_dt_print 는 업데이트 되므로 self.instance.base_dt_print 로 적용
            'msg': "'서울특별시 강남구 삼성1동' is not a valid legal district name",
        })


    def sub_test_generate_pnu_from_address(
        self,
        address,
        result: bool
    ):
        """
        _generate_pnu 함수 테스트 서브 메소드
            - assertIsInstance() 테스트
            - assertIsNotNone() 테스트
            - assertEqual() 테스트
        """
        res = self.instance.generate_pnu_from_address(address)
        self.assertIsInstance(res.get("error"), bool)
        self.assertIsInstance(res.get("msg"), str)
        self.assertIsNotNone(res)
        self.assertIsNotNone(res.get("error"))
        self.assertIsNotNone(res.get("msg"))
        self.assertEqual(res.get("error"), result)


    def test_generate_pnu_from_address(self):
        """
        generate_pnu_from_address 함수 테스트 메소드

        - generate_pnu_from_address 함수 예외처리 테스트
            - generate_pnu_from_address 함수 예외처리 테스트(TypeError 입력값(address)이 문자열이 아닌 int type)
            - generate_pnu_from_address 함수 예외처리 테스트(TypeError 입력값(address)이 문자열이 아닌 float type)
            - generate_pnu_from_address 함수 예외처리 테스트(TypeError 입력값(address)이 문자열이 아닌 None type)
            - generate_pnu_from_address 함수 예외처리 테스트(TypeError 입력값(address)이 문자열이 아닌 bool type)

        - generate_pnu_from_address 함수 리턴값 테스트(올바른 법정동 문자열 및 지번 제공)
            - generate_pnu_from_address 함수 리턴값 타입 테스트
            - generate_pnu_from_address 함수 리턴값 error 타입 테스트
            - generate_pnu_from_address 함수 리턴값 pnu 타입 테스트
            - generate_pnu_from_address 함수 리턴값 bjd_cd 타입 테스트
            - generate_pnu_from_address 함수 리턴값 mountain_cd 타입 테스트
            - generate_pnu_from_address 함수 리턴값 bunji_cd 타입 테스트
            - generate_pnu_from_address 함수 리턴값 bjd_datas 타입 테스트
            - generate_pnu_from_address 함수 리턴값 bun 타입 테스트
            - generate_pnu_from_address 함수 리턴값 ji 타입 테스트
            - generate_pnu_from_address 함수 리턴값 msg 타입 테스트
            - generate_pnu_from_address 함수 리턴값 base_dt 타입 테스트
            - generate_pnu_from_address 함수 리턴값 error 값이 None 이 아닌지 테스트
            - generate_pnu_from_address 함수 리턴값 pnu 값이 None 이 아닌지 테스트
            - generate_pnu_from_address 함수 리턴값 bjd_cd 값이 None 이 아닌지 테스트
            - generate_pnu_from_address 함수 리턴값 mountain_cd 값이 None 이 아닌지 테스트
            - generate_pnu_from_address 함수 리턴값 bunji_cd 값이 None 이 아닌지 테스트
            - generate_pnu_from_address 함수 리턴값 bjd_datas 값이 None 이 아닌지 테스트
            - generate_pnu_from_address 함수 리턴값 bun 값이 None 이 아닌지 테스트
            - generate_pnu_from_address 함수 리턴값 ji 값이 None 이 아닌지 테스트
            - generate_pnu_from_address 함수 리턴값 msg 값이 None 이 아닌지 테스트
            - generate_pnu_from_address 함수 리턴값 base_dt 값이 None 이 아닌지 테스트
            - generate_pnu_from_address 함수 리턴값 일치 테스트

        - generate_pnu_from_address 함수 리턴값 테스트(형식은 맞지만 존재하지 않는 법정동 문자열 및 정상적인 지번 제공)
            - generate_pnu_from_address 함수 리턴값 타입 테스트
            - generate_pnu_from_address 함수 리턴값 error 타입 테스트
            - generate_pnu_from_address 함수 리턴값 pnu 타입 테스트
            - generate_pnu_from_address 함수 리턴값 bjd_cd 타입 테스트
            - generate_pnu_from_address 함수 리턴값 mountain_cd 타입 테스트
            - generate_pnu_from_address 함수 리턴값 bunji_cd 타입 테스트
            - generate_pnu_from_address 함수 리턴값 bjd_datas 타입 테스트
            - generate_pnu_from_address 함수 리턴값 bun 타입 테스트
            - generate_pnu_from_address 함수 리턴값 ji 타입 테스트
            - generate_pnu_from_address 함수 리턴값 msg 타입 테스트
            - generate_pnu_from_address 함수 리턴값 base_dt 타입 테스트
            - generate_pnu_from_address 함수 리턴값 error 값이 None 이 아닌지 테스트
            - generate_pnu_from_address 함수 리턴값 pnu 값이 None 이 맞는지 테스트
            - generate_pnu_from_address 함수 리턴값 bjd_cd 값이 None 이 맞는지 테스트
            - generate_pnu_from_address 함수 리턴값 mountain_cd 값이 None 이 맞는지 테스트
            - generate_pnu_from_address 함수 리턴값 bunji_cd 값이 None 이 맞는지 테스트
            - generate_pnu_from_address 함수 리턴값 bjd_datas 값이 None 이 맞는지 테스트
            - generate_pnu_from_address 함수 리턴값 bun 값이 None 이 맞는지 테스트
            - generate_pnu_from_address 함수 리턴값 ji 값이 None 이 맞는지 테스트
            - generate_pnu_from_address 함수 리턴값 msg 값이 None 이 아닌지 테스트
            - generate_pnu_from_address 함수 리턴값 base_dt 값이 None 이 아닌지 테스트
            - generate_pnu_from_address 함수 리턴값 일치 테스트
        """

        with self.assertRaises(TypeError): self.instance.generate_pnu_from_address(address=0)
        with self.assertRaises(TypeError): self.instance.generate_pnu_from_address(address=0.1)
        with self.assertRaises(TypeError): self.instance.generate_pnu_from_address(address=None)
        with self.assertRaises(TypeError): self.instance.generate_pnu_from_address(address=True)
        with self.assertRaises(TypeError): self.instance.generate_pnu_from_address(address=False)

        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 산 00000', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 산 000000', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 산 0000000', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 산 00000000', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 산 000000000', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 산 0000000000', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 산 11111-2', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 산 33333-44', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 산 55555-666', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 산 77777-8888', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 산 99999-00000', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 산 7777-88888', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 산 555-66666', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 산 33-44444', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 산 1-22222', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 산00000', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 산000000', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 산0000000', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 산00000000', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 산000000000', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 산0000000000', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 산11111-2', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 산33333-44', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 산55555-666', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 산77777-8888', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 산99999-00000', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 산7777-88888', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 산555-66666', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 산33-44444', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 산1-22222', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 산-1000', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 산 -1000', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 산  -1000', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 산   -1000', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 산1000-', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 산 1000-', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 산  1000-', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 산   1000-', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 산 10000', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 a', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 a000', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 000a', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 a-1000', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 1000-a', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 ㄱ', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 ㄱ000', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 000ㄱ', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 ㄱ-1000', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 1000-ㄱ', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 나', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 나000', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 000나', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 나-1000', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 1000-나', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 선 1000-1000', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 순 1000-1000', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 상 1000-1000', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 선산 1000-1000', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 나산 1000-1000', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 산나 1000-1000', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 산산 1000-1000', result=True)
        self.sub_test_generate_pnu_from_address(address='서울특별시 강남구 삼성동 산산산 1000-1000', result=True)

        res = self.instance.generate_pnu_from_address(address='서울특별시 강남구 삼성동 1-1') # 정상적인 법정동코드 및 지번 입력값
        self.assertIsInstance(res, dict)
        self.assertIsInstance(res.get('error'), bool)
        self.assertIsInstance(res.get('pnu'), str)
        self.assertIsInstance(res.get('bjd_cd'), str)
        self.assertIsInstance(res.get('mountain_cd'), str)
        self.assertIsInstance(res.get('bunji_cd'), str)
        self.assertIsInstance(res.get('bjd_datas'), dict)
        self.assertIsInstance(res.get('bun'), str)
        self.assertIsInstance(res.get('ji'), str)
        self.assertIsInstance(res.get('msg'), str)
        self.assertIsInstance(res.get('base_dt'), str)
        self.assertIsNotNone(res.get('error'))
        self.assertIsNotNone(res.get('pnu'))
        self.assertIsNotNone(res.get('bjd_cd'))
        self.assertIsNotNone(res.get('mountain_cd'))
        self.assertIsNotNone(res.get('bunji_cd'))
        self.assertIsNotNone(res.get('bjd_datas'))
        self.assertIsNotNone(res.get('bun'))
        self.assertIsNotNone(res.get('ji'))
        self.assertIsNotNone(res.get('base_dt'))
        self.assertIsNotNone(res.get('msg'))
        self.assertEqual(res, {
            'error': False,
            'pnu': '1168010500100010001',
            'bjd_cd': '1168010500',
            'mountain_cd': '1',
            'bunji_cd': '00010001',
            'bjd_datas': {
                'error': False,
                'sido_nm': '서울특별시',
                'sgg_nm': '강남구',
                'emd_nm': '삼성동',
                'ri_nm': None,
                'full_bjd_nm': '서울특별시 강남구 삼성동',
                'created_dt': '1988-04-23',
                'deleted_dt': None,
                'base_dt': self.instance.base_dt_print, # base_dt_print 는 업데이트 되므로 self.instance.base_dt_print 로 적용
                'msg': ''
            },
            'bun': '1',
            'ji': '1',
            'msg': '',
            'base_dt': self.instance.base_dt_print, # base_dt_print 는 업데이트 되므로 self.instance.base_dt_print 로 적용
        })

        res = self.instance.generate_pnu_from_address(address='서울특별시 강남구 삼성1동 1-1') # 정상적인 법정동코드 및 지번 입력값
        self.assertIsInstance(res, dict)
        self.assertIsInstance(res.get('error'), bool)
        # self.assertIsInstance(res.get('pnu'), str)
        # self.assertIsInstance(res.get('bjd_cd'), str)
        # self.assertIsInstance(res.get('mountain_cd'), str)
        # self.assertIsInstance(res.get('bunji_cd'), str)
        self.assertIsInstance(res.get('bjd_datas'), dict)
        # self.assertIsInstance(res.get('bun'), str)
        # self.assertIsInstance(res.get('ji'), str)
        self.assertIsInstance(res.get('msg'), str)
        self.assertIsInstance(res.get('base_dt'), str)
        self.assertIsNotNone(res.get('error'))
        self.assertIsNone(res.get('pnu'))
        self.assertIsNone(res.get('bjd_cd'))
        self.assertIsNone(res.get('mountain_cd'))
        self.assertIsNone(res.get('bunji_cd'))
        self.assertIsNotNone(res.get('bjd_datas'))
        self.assertIsNone(res.get('bun'))
        self.assertIsNone(res.get('ji'))
        self.assertIsNotNone(res.get('msg'))
        self.assertIsNotNone(res.get('base_dt'))
        self.assertEqual(res, {
            'error': True,
            'pnu': None,
            'bjd_cd': None,
            'mountain_cd': None,
            'bunji_cd': None,
            'bjd_datas': {
                'error': True,
                'sido_nm': None,
                'sgg_nm': None,
                'emd_nm': None,
                'ri_nm': None,
                'full_bjd_nm': None,
                'created_dt': None,
                'deleted_dt': None,
                'base_dt': self.instance.base_dt_print, # base_dt_print 는 업데이트 되므로 self.instance.base_dt_print 로 적용
                'msg': ''},
            'bun': None,
            'ji': None,
            'base_dt': self.instance.base_dt_print, # base_dt_print 는 업데이트 되므로 self.instance.base_dt_print 로 적용
            'msg': 'Failed to extract bjd name from address: 서울특별시 강남구 삼성1동 1-1',
        })


if __name__ == "__main__":
    unittest.main()