import os
import sys
import unittest
from datetime import datetime
from symspellpy import SymSpell
from symspellpy.suggest_item import SuggestItem
sys.path.append(os.getcwd())
from vdutils.cordate import (
    CorDate,
    get_correct_array,
    get_correct_one
)


class TestClass(unittest.TestCase):

    @classmethod
    def setUp(cls):
        "Hook method for setting fixture before running tests in the class"
        cls.driver = 'test'
        cls.instance = CorDate()
        cls.date_1 = '19880416'
        cls.date_2 = '1988416'
        cls.date_3 = '9880416'
        cls.date_4 = '198804'
        cls.date_5 = '880416'
        cls.date_6 = '88416'
        cls.date_7 = '19884'
        cls.date_8 = '1988'
        cls.err_str = 'abc'


    @classmethod
    def tearDown(cls):
        "Hook method for deconstructing the class fixture after running all tests in the class"


    def test_sym_spell(self):
        """클래스 인스턴스 초기 생성자 sym_spell 타입 테스트 메소드"""
        self.assertIsInstance(self.instance.sym_spell, SymSpell)


    def test_dictionary_path(self):
        """클래스 인스턴스 초기 생성자 dictionary_path 타입, 값 테스트 메소드"""
        self.assertIsInstance(self.instance.dictionary_path, str)
        self.assertEqual(
            self.instance.dictionary_path,
            f'{os.getcwd()}/vdutils/data/date/date_dictionary.txt'
        )


    def test_this_year(self):
        """클래스 인스턴스 초기 생성자 this_year 타입, 값 테스트 메소드"""
        self.assertIsInstance(self.instance.this_year, int)
        self.assertEqual(self.instance.this_year, datetime.now().year)


    def test_this_year_two_length(self):
        """클래스 인스턴스 초기 생성자 this_year_tow_length 타입, 값 테스트 메소드"""
        self.assertIsInstance(self.instance.this_year_two_length, int)
        self.assertEqual(
            self.instance.this_year_two_length, 
            int(str(datetime.now().year)[2:])
        )


    def test_max_edit_distance(self):
        """클래스 인스턴스 초기 생성자 max_edit_distance 타입, 값 테스트 메소드"""
        self.assertIsInstance(self.instance.max_edit_distance, int)
        self.assertEqual(self.instance.max_edit_distance, 2)


    def test_runs(self):
        """단순 실행여부 판별하는 테스트 메소드"""

        get_correct_array(self.date_1)
        get_correct_one(self.date_1)
        self.instance.load_date_dictionary()
        self.instance.look_up_array(self.date_1)
        self.instance.look_up_one(self.date_1)
        self.instance.get_correct_array(self.date_1)
        self.instance.get_correct_one(self.date_1)


    def test_get_correct_array(self):
        """get_correct_array 함수 테스트 메소드"""

        with self.assertRaises(TypeError):
            get_correct_array(int(self.date_1))

        with self.assertRaises(ValueError):
            get_correct_array(self.err_str)

        res = get_correct_array(self.date_1)
        self.assertIsInstance(res, list)
        self.assertEqual(res, ['19880416'])


    def test_get_correct_one(self):
        """get_correct_one 함수 테스트 메소드"""

        with self.assertRaises(TypeError):
            get_correct_one(int(self.date_1))

        with self.assertRaises(ValueError):
            get_correct_array(self.err_str)

        res = get_correct_one(self.date_1)
        self.assertIsInstance(res, str)
        self.assertEqual(res, '19880416')


    def test_cls_load_date_dictionary(self):
        """load_date_dictionary 함수 테스트 메소드"""

        res = self.instance.load_date_dictionary()
        self.assertIsInstance(res, bool)
        self.assertEqual(res, True)


    def test_cls_look_up_array(self):
        """cordate.look_up_array 함수 테스트 메소드"""

        self.instance.load_date_dictionary()

        with self.assertRaises(TypeError):
            self.instance.look_up_array(int(self.date_1))

        with self.assertRaises(ValueError):
            self.instance.look_up_array(self.err_str)

        res = self.instance.look_up_array(self.date_1)
        self.assertIsInstance(res, list)
        self.assertEqual(res[0].term, '19880416')


    def test_cls_look_up_one(self):
        """cordate.look_up_one 함수 테스트 메소드"""

        self.instance.load_date_dictionary()
        
        with self.assertRaises(TypeError):
            self.instance.look_up_one(int(self.date_1))

        with self.assertRaises(ValueError):
            self.instance.look_up_one(self.err_str)

        res = self.instance.look_up_one(self.date_1)
        self.assertIsInstance(res, SuggestItem)
        self.assertEqual(res.term, '19880416')


    def test_cls_look_up_array_clean(self):
        """cordate.look_up_array_clean 함수 테스트 메소드"""

        self.instance.load_date_dictionary()

        with self.assertRaises(TypeError):
            self.instance.look_up_array_clean(int(self.date_1))

        with self.assertRaises(ValueError):
            self.instance.look_up_array_clean(self.err_str)

        res = self.instance.look_up_array_clean(self.date_1)
        self.assertIsInstance(res, list)
        self.assertEqual(res[0], '19880416')


    def test_cls_look_up_one_clean(self):
        """cordate.look_up_one_clean 함수 테스트 메소드"""

        self.instance.load_date_dictionary()
        
        with self.assertRaises(TypeError):
            self.instance.look_up_one_clean(int(self.date_1))

        with self.assertRaises(ValueError):
            self.instance.look_up_one_clean(self.err_str)

        res = self.instance.look_up_one_clean(self.date_1)
        self.assertIsInstance(res, str)
        self.assertEqual(res, '19880416')


    def test_cls_get_correct_array(self):
        """cordate.get_correct_array 함수 테스트 메소드"""

        self.instance.load_date_dictionary()
        
        with self.assertRaises(TypeError):
            self.instance.get_correct_array(int(self.date_1))

        with self.assertRaises(ValueError):
            self.instance.get_correct_array(self.err_str)
        
        res = self.instance.get_correct_array(self.date_1)
        self.assertIsInstance(res, list)
        self.assertEqual(res, ['19880416'])


    def test_cls_get_correct_one(self):
        """cordate.get_correct_one 함수 테스트 메소드"""
        
        self.instance.load_date_dictionary()
        
        with self.assertRaises(TypeError):
            self.instance.get_correct_array(int(self.date_1))

        with self.assertRaises(ValueError):
            self.instance.get_correct_array(self.err_str)

        res = self.instance.get_correct_one(self.date_1)
        self.assertIsInstance(res, str)
        self.assertEqual(res, '19880416')


    def test_correct_value(self):
        """
        get_correct_one 함수 실행결과 테스트 메소드
        cordate.get_correct_one 함수 실행결과 테스트 메소드
        """

        self.instance.load_date_dictionary()

        self.assertEqual(get_correct_one(self.date_1), '19880416')
        self.assertEqual(get_correct_one(self.date_2), '19880416')
        self.assertEqual(get_correct_one(self.date_3), '19880416')
        self.assertEqual(get_correct_one(self.date_4), '19880401')
        self.assertEqual(get_correct_one(self.date_5), '19880416')
        self.assertEqual(get_correct_one(self.date_6), '19880416')
        self.assertEqual(get_correct_one(self.date_7), '19880401')
        self.assertEqual(get_correct_one(self.date_8), '19880101')

        self.assertEqual(self.instance.get_correct_one(self.date_1), '19880416')
        self.assertEqual(self.instance.get_correct_one(self.date_2), '19880416')
        self.assertEqual(self.instance.get_correct_one(self.date_3), '19880416')
        self.assertEqual(self.instance.get_correct_one(self.date_4), '19880401')
        self.assertEqual(self.instance.get_correct_one(self.date_5), '19880416')
        self.assertEqual(self.instance.get_correct_one(self.date_6), '19880416')
        self.assertEqual(self.instance.get_correct_one(self.date_7), '19880401')
        self.assertEqual(self.instance.get_correct_one(self.date_8), '19880101')

        self.assertEqual(get_correct_one('19990101'), '19990101')
        self.assertEqual(get_correct_one('9990101'), '19990101')
        self.assertEqual(get_correct_one('990101'), '19990101')
        self.assertEqual(get_correct_one('199901'), '19990101')
        self.assertEqual(get_correct_one('199911'), '19991101')
        self.assertEqual(get_correct_one('19991'), '19990101')
        self.assertEqual(get_correct_one('9901'), '19990101')
        self.assertEqual(get_correct_one('1999'), '19990101')
        
        self.assertEqual(self.instance.get_correct_one('19990101'), '19990101')
        self.assertEqual(self.instance.get_correct_one('9990101'), '19990101')
        self.assertEqual(self.instance.get_correct_one('990101'), '19990101')
        self.assertEqual(self.instance.get_correct_one('199901'), '19990101')
        self.assertEqual(self.instance.get_correct_one('199911'), '19991101')
        self.assertEqual(self.instance.get_correct_one('19991'), '19990101')
        self.assertEqual(self.instance.get_correct_one('9901'), '19990101')
        self.assertEqual(self.instance.get_correct_one('1999'), '19990101')

        self.assertEqual(get_correct_one('20220505'), '20220505')
        self.assertEqual(get_correct_one('2022055'), '20220505')
        self.assertEqual(get_correct_one('2022505'), '20220505')
        self.assertEqual(get_correct_one('202255'), '20220505')
        self.assertEqual(get_correct_one('220505'), '20220505')
        self.assertEqual(get_correct_one('22055'), '20220505')
        self.assertEqual(get_correct_one('2255'), '20220505')
        self.assertEqual(get_correct_one('2205'), '20220501')
        self.assertEqual(get_correct_one('2022'), '20220101')
        
        self.assertEqual(self.instance.get_correct_one('20220505'), '20220505')
        self.assertEqual(self.instance.get_correct_one('2022055'), '20220505')
        self.assertEqual(self.instance.get_correct_one('2022505'), '20220505')
        self.assertEqual(self.instance.get_correct_one('202255'), '20220505')
        self.assertEqual(self.instance.get_correct_one('220505'), '20220505')
        self.assertEqual(self.instance.get_correct_one('22055'), '20220505')
        self.assertEqual(self.instance.get_correct_one('2255'), '20220505')
        self.assertEqual(self.instance.get_correct_one('2205'), '20220501')
        self.assertEqual(self.instance.get_correct_one('2022'), '20220101')
        
        self.assertEqual(get_correct_one('20230505'), '20230505')
        self.assertEqual(get_correct_one('2023055'), '20230505')
        self.assertEqual(get_correct_one('2023505'), '20230505')
        self.assertEqual(get_correct_one('202355'), '20230505')
        self.assertEqual(get_correct_one('230505'), '20230505')
        self.assertEqual(get_correct_one('23055'), '20230505')
        self.assertEqual(get_correct_one('2355'), '20230505')
        self.assertEqual(get_correct_one('2305'), '20230501')
        self.assertEqual(get_correct_one('2023'), '20230101')
        
        self.assertEqual(self.instance.get_correct_one('20230505'), '20230505')
        self.assertEqual(self.instance.get_correct_one('2023055'), '20230505')
        self.assertEqual(self.instance.get_correct_one('2023505'), '20230505')
        self.assertEqual(self.instance.get_correct_one('202355'), '20230505')
        self.assertEqual(self.instance.get_correct_one('230505'), '20230505')
        self.assertEqual(self.instance.get_correct_one('23055'), '20230505')
        self.assertEqual(self.instance.get_correct_one('2355'), '20230505')
        self.assertEqual(self.instance.get_correct_one('2305'), '20230501')
        self.assertEqual(self.instance.get_correct_one('2023'), '20230101')


if __name__ == "__main__":
    unittest.main()