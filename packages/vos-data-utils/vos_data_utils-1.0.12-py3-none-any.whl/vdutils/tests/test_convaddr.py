import os
import sys
import unittest
from typing import ( 
    List,
    Dict
)
sys.path.append(os.getcwd())
from vdutils.convaddr import ConvAddr


class TestClass(unittest.TestCase):

    @classmethod
    def setUp(cls):
        "Hook method for setting fixture before running tests in the class"
        cls.driver = 'test'
        cls.instance = ConvAddr()
        cls.addr_1 = '서울시 강남구 삼성동 1'


    @classmethod
    def tearDown(cls):
        "Hook method for deconstructing the class fixture after running all tests in the class"


    def test_class_initialization_type(self):
        """클래스 인스턴스 초기 생성자 타입 테스트 메소드"""

        self.assertIsInstance(self.instance.bjd_current_dic, dict)
        self.assertTrue(all(isinstance(item, str) for item in self.instance.bjd_current_dic.keys()))
        self.assertTrue(all(isinstance(item, str) for item in self.instance.bjd_current_dic.values()))
        self.assertIsInstance(self.instance.bjd_smallest_list, list)
        self.assertTrue(all(isinstance(item, str) for item in self.instance.bjd_smallest_list))
        self.assertIsInstance(self.instance.bjd_current_bjd_nm_list, list)
        self.assertTrue(all(isinstance(item, str) for item in self.instance.bjd_current_bjd_nm_list))
        self.assertIsInstance(self.instance.current_sido_sgg_list, list)
        self.assertTrue(all(isinstance(item, str) for item in self.instance.current_sido_sgg_list))
        self.assertIsInstance(self.instance.current_sido_list, list)
        self.assertTrue(all(isinstance(item, str) for item in self.instance.current_sido_list))
        self.assertIsInstance(self.instance.current_sgg_list, list)
        self.assertTrue(all(isinstance(item, str) for item in self.instance.current_sgg_list))
        self.assertIsInstance(self.instance.current_emd_list, list)
        self.assertTrue(all(isinstance(item, str) for item in self.instance.current_emd_list))
        self.assertIsInstance(self.instance.current_ri_list, list)
        self.assertTrue(all(isinstance(item, str) for item in self.instance.current_ri_list))
        self.assertIsInstance(self.instance.bjd_changed_dic, dict)
        self.assertTrue(all(isinstance(item, str) for item in self.instance.bjd_changed_dic.keys()))
        self.assertTrue(all(isinstance(item, str) for item in self.instance.bjd_changed_dic.values()))
        self.assertIsInstance(self.instance.bjd_changed_old_bjd_nm_list, list)
        self.assertTrue(all(isinstance(item, str) for item in self.instance.bjd_changed_old_bjd_nm_list))


    def test_class_initialization_not_empty(self):
        """클래스 인스턴스 초기 생성자 객체 테스트 메소드"""

        self.assertNotEqual(len(self.instance.bjd_changed_old_bjd_nm_list), 0)
        self.assertNotEqual(len(self.instance.bjd_smallest_list), 0)
        self.assertNotEqual(len(self.instance.bjd_current_bjd_nm_list), 0)
        self.assertNotEqual(len(self.instance.current_sido_sgg_list), 0)
        self.assertNotEqual(len(self.instance.current_sido_list), 0)
        self.assertNotEqual(len(self.instance.current_sgg_list), 0)
        self.assertNotEqual(len(self.instance.current_emd_list), 0)
        self.assertNotEqual(len(self.instance.current_ri_list), 0)
        self.assertNotEqual(len(self.instance.bjd_changed_dic), 0)
        self.assertNotEqual(len(self.instance.bjd_changed_old_bjd_nm_list), 0)


    def test_runs(self):
        """단순 실행여부 판별하는 테스트 메소드"""

        self.instance.replace_etc_land_string(addr=self.addr_1)
        self.instance.correct_simple_spacing(addr=self.addr_1)
        self.instance.correct_smallest_bjd_spacing(addr=self.addr_1)
        self.instance.correct_changed_bjd(addr=self.addr_1, is_log=True)
        self.instance.correct_bjd(addr=self.addr_1, is_log=True)


    def test_replace_etc_land_string(self):
        """replace_etc_land_string 함수 테스트 메소드"""

        with self.assertRaises(TypeError):
            self.instance.replace_etc_land_string(0)

        with self.assertRaises(TypeError):
            self.instance.replace_etc_land_string(None)

        with self.assertRaises(TypeError):
            self.instance.replace_etc_land_string(False)

        res = self.instance.replace_etc_land_string('서울시 강남구 삼성동 1외')
        self.assertIsInstance(res, str)
        self.assertEqual(res, '서울시 강남구 삼성동 1 외')

        res = self.instance.replace_etc_land_string('서울시 강남구 삼성동 1외1')
        self.assertIsInstance(res, str)
        self.assertEqual(res, '서울시 강남구 삼성동 1 외1')

        res = self.instance.replace_etc_land_string('서울시 강남구 삼성동 1외 1')
        self.assertIsInstance(res, str)
        self.assertEqual(res, '서울시 강남구 삼성동 1 외 1')

        res = self.instance.replace_etc_land_string('서울시 강남구 삼성동 1외1필지')
        self.assertIsInstance(res, str)
        self.assertEqual(res, '서울시 강남구 삼성동 1 외1필지')

        res = self.instance.replace_etc_land_string('서울시 강남구 삼성동 1외 1필지')
        self.assertIsInstance(res, str)
        self.assertEqual(res, '서울시 강남구 삼성동 1 외 1필지')


    def test_correct_simple_spacing(self):
        """correct_simple_spacing 함수 테스트 메소드"""

        with self.assertRaises(TypeError):
            self.instance.correct_simple_spacing(0)

        with self.assertRaises(TypeError):
            self.instance.correct_simple_spacing(None)

        with self.assertRaises(TypeError):
            self.instance.correct_simple_spacing(False)

        res = self.instance.correct_simple_spacing('서울시 강남구  삼성동 1')
        self.assertIsInstance(res, str)
        self.assertEqual(res, '서울시 강남구 삼성동 1')


    def test_correct_smallest_bjd_spacing(self):
        """correct_smallest_bjd_spacing 함수 테스트 메소드"""

        with self.assertRaises(TypeError):
            self.instance.correct_smallest_bjd_spacing(0)

        with self.assertRaises(TypeError):
            self.instance.correct_smallest_bjd_spacing(None)

        with self.assertRaises(TypeError):
            self.instance.correct_smallest_bjd_spacing(False)

        res = self.instance.correct_smallest_bjd_spacing('서울시 강남구 삼성동1')
        self.assertIsInstance(res, str)
        self.assertEqual(res, '서울시 강남구 삼성동 1')


    def test_correct_changed_bjd(self):
        """correct_changed_bjd 함수 테스트 메소드"""

        with self.assertRaises(TypeError):
            self.instance.correct_changed_bjd(0)

        with self.assertRaises(TypeError):
            self.instance.correct_changed_bjd(None)

        with self.assertRaises(TypeError):
            self.instance.correct_changed_bjd(False)

        with self.assertRaises(TypeError):
            self.instance.correct_changed_bjd(addr=self.addr_1, is_log=0)

        with self.assertRaises(TypeError):
            self.instance.correct_changed_bjd(addr=self.addr_1, is_log=None)

        with self.assertRaises(TypeError):
            self.instance.correct_changed_bjd(addr=self.addr_1, is_log='False')

        res = self.instance.correct_changed_bjd(
            addr='서울시 강남구 삼성동 1',
            is_log=True
        )
        self.assertIsInstance(res, str)
        self.assertEqual(res, '서울시 강남구 삼성동 1')

        res = self.instance.correct_changed_bjd(
            addr='강원도 춘천시 서면 현암리',
            is_log=True
        )
        self.assertIsInstance(res, str)
        self.assertEqual(res, '강원특별자치도 춘천시 서면 현암리')

        res = self.instance.correct_changed_bjd(
            addr='강원도 춘천시 서면 현암리 1-1',
            is_log=True
        )
        self.assertIsInstance(res, str)
        self.assertEqual(res, '강원특별자치도 춘천시 서면 현암리 1-1')

        # 20240101 법정동 변경사항 반영 테스트 추가
        res = self.instance.correct_changed_bjd(
            addr='경기도 부천시 소사본동 1',
            is_log=True
        )
        self.assertIsInstance(res, str)
        self.assertEqual(res, '경기도 부천시 소사구 소사본동 1')

        # 20240118 법정동 변경사항 반영 테스트 추가
        res = self.instance.correct_changed_bjd(
            addr='전라북도 전주시 완산구 중화산동1가 1',
            is_log=True
        )
        self.assertIsInstance(res, str)
        self.assertEqual(res, '전북특별자치도 전주시 완산구 중화산동1가 1')

        # 20240201 법정동 변경사항 반영 테스트 추가
        res = self.instance.correct_changed_bjd(
            addr='경상북도 예천군 호명면 송곡리 1',
            is_log=True
        )
        self.assertIsInstance(res, str)
        self.assertEqual(res, '경상북도 예천군 호명읍 송곡리 1')

        # 20240801 법정동 변경사항 반영 테스트 추가
        res = self.instance.correct_changed_bjd(
            addr='경상북도 성주군 금수면 무학리 산1',
            is_log=True
        )
        self.assertIsInstance(res, str)
        self.assertEqual(res, '경상북도 성주군 금수강산면 무학리 산1')

        # 20250513 법정동 변경사항 반영 테스트 추가
        res = self.instance.correct_changed_bjd(
            addr='경기도 화성시 서신면 사곳리 산 1-1',
            is_log=True
        )
        self.assertIsInstance(res, str)
        self.assertEqual(res, '경기도 화성시 서신면 사곶리 산 1-1')

        # 20250630 법정동 변경사항 반영 테스트 추가
        res = self.instance.correct_changed_bjd(
            addr='경상북도 영덕군 영해면 대리 1',
            is_log=True
        )
        self.assertIsInstance(res, str)
        self.assertEqual(res, '경상북도 영덕군 영해면 대동리 1')

        # 20251017 법정동 변경사항 반영 테스트 추가
        res = self.instance.correct_changed_bjd(
            addr='경상남도 통영시 산양읍 삼덕리 100',
            is_log=True
        )
        self.assertIsInstance(res, str)
        self.assertEqual(res, '경상남도 통영시 산양읍 당포리 100')


    def test_correct_bjd(self):
        """correct_bjd 함수 테스트 메소드"""

        with self.assertRaises(TypeError):
            self.instance.correct_bjd(0)

        with self.assertRaises(TypeError):
            self.instance.correct_bjd(None)

        with self.assertRaises(TypeError):
            self.instance.correct_bjd(False)

        with self.assertRaises(TypeError):
            self.instance.correct_bjd(addr=self.addr_1, is_log=0)

        with self.assertRaises(TypeError):
            self.instance.correct_bjd(addr=self.addr_1, is_log=None)

        with self.assertRaises(TypeError):
            self.instance.correct_bjd(addr=self.addr_1, is_log='False')

        res = self.instance.correct_bjd(
            addr='서울시 강남구 삼성동 1',
            is_log=True
        )
        self.assertIsInstance(res, str)
        self.assertEqual(res, '서울시 강남구 삼성동 1')

        res = self.instance.correct_bjd(
            addr='강원도 춘천시 서면 현암리',
            is_log=True
        )
        self.assertIsInstance(res, str)
        self.assertEqual(res, '강원특별자치도 춘천시 서면 현암리')

        res = self.instance.correct_bjd(
            addr='강원도 춘천시 서면 현암리 1-1',
            is_log=True
        )
        self.assertIsInstance(res, str)
        self.assertEqual(res, '강원특별자치도 춘천시 서면 현암리 1-1')

        res = self.instance.correct_bjd(
            addr='강원도 춘천시 서면 현암리1-1',
            is_log=True
        )
        self.assertIsInstance(res, str)
        self.assertEqual(res, '강원특별자치도 춘천시 서면 현암리 1-1')

        res = self.instance.correct_bjd(
            addr='강원도   춘천시 서면 현암리 1-1',
            is_log=True
        )
        self.assertIsInstance(res, str)
        self.assertEqual(res, '강원특별자치도 춘천시 서면 현암리 1-1')


if __name__ == "__main__":
    unittest.main()