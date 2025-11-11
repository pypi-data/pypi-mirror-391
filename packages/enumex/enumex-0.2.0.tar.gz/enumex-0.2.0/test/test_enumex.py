# Add package directory to path for debugging
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import unittest 
from enumex import *
from enumex import autoex as auto
from enum import Enum as StdEnum
if sys.version_info >= (3, 4): 
    from enum import IntEnum as StdIntEnum
    if sys.version_info >= (3, 6):
        from enum import IntFlag as StdIntFlag, Flag as StdFlag, auto as StdAuto
        if sys.version_info >= (3, 11):
            from enum import StrEnum as StdStrEnum, ReprEnum as StdReprEnum
from abc import abstractmethod
from typing import Union, Callable

class EnumExTests(unittest.TestCase):

    def test_standard_functionality(self):
        class A(EnumEx):
            V1 = autoex()
            V2 = '2'
            V3 = 3

        self.assertIsInstance(A.V1,     A)
        self.assertIsInstance(A.V1,     EnumEx)
        self.assertEqual(1,             A.V1.value)
        self.assertEqual('2',           A.V2.value)
        self.assertEqual(3,             A.V3.value)
        self.assertEqual("A.V1",        str(A.V1))

        self.assertListEqual([A.V1, A.V2, A.V3], list(A))

        with self.assertRaises(AttributeError) as ec:
            A.V1 = 1
        self.assertEqual("cannot reassign member 'V1'", ec.exception.args[0])

    def test_std_auto(self):
        class A(EnumEx):
            V1 = StdAuto()
            V2 = StdAuto()
        class B(A):
            V3 = StdAuto()
            V4 = StdAuto()

        self.assertEqual(1,     A.V1.value)
        self.assertEqual(2,     A.V2.value)
        self.assertEqual(3,     B.V3.value)
        self.assertEqual(4,     B.V4.value)

    def test_std_instancecheck(self):
        class A(EnumEx):
            V1 = auto()

        class B(IntEnumEx):
            V1 = auto()

        class C(IntFlagEx):
            V1 = auto()

        class D(StrEnumEx):
            V1 = auto()

        class E(int, ReprEnumEx):
            V1 = auto()

        def test_isinstance(localcls:type[EnumEx], intenum:bool, flag:bool, intflag:bool, reprenum:bool, strenum:bool):
            msg = f"Testing {localcls.__name__} is "
            value:EnumEx = localcls.V1
            self.assertIsInstance(                value, EnumEx,      msg + f"instance of EnumEx")
            self.assertEqual(intenum,  isinstance(value, IntEnumEx),  msg + f"{'' if intenum   else 'not '}instance of IntEnumEx")
            self.assertEqual(flag,     isinstance(value, FlagEx),     msg + f"{'' if flag      else 'not '}instance of FlagEx")
            self.assertEqual(intflag,  isinstance(value, IntFlagEx),  msg + f"{'' if intflag   else 'not '}instance of IntFlagEx")
            self.assertEqual(reprenum, isinstance(value, ReprEnumEx), msg + f"{'' if reprenum  else 'not '}instance of ReprEnumEx")
            self.assertEqual(strenum,  isinstance(value, StrEnumEx),  msg + f"{'' if strenum   else 'not '}instance of StrEnumEx")

        test_isinstance(A, intenum=False,  flag=False, intflag=False,  reprenum=False, strenum=False)
        test_isinstance(B, intenum=True,   flag=False, intflag=False,  reprenum=True,  strenum=False)
        test_isinstance(C, intenum=False,  flag=True,  intflag=True,   reprenum=True,  strenum=False)
        test_isinstance(D, intenum=False,  flag=False, intflag=False,  reprenum=True,  strenum=True)
        test_isinstance(E, intenum=False,  flag=False, intflag=False,  reprenum=True,  strenum=False)

        def test_issubclass_std(extype:type[EnumEx], stdtype:type[StdEnum]):
            msg = f"Testing issubclass of {stdtype.__name__}"
            self.assertEqual(               issubclass(EnumEx,      extype),    issubclass(EnumEx,      stdtype), msg)
            if sys.version_info                                                                                             >= (3, 4):
                self.assertEqual(           issubclass(IntEnumEx,   extype),    issubclass(IntEnumEx,   stdtype), msg)
                if sys.version_info                                                                                         >= (3, 6):
                    self.assertEqual(       issubclass(IntFlagEx,   extype),    issubclass(IntFlagEx,   stdtype), msg)
                    self.assertEqual(       issubclass(FlagEx,      extype),    issubclass(FlagEx,      stdtype), msg)
                    if sys.version_info                                                                                     >= (3, 11):
                        self.assertEqual(   issubclass(ReprEnumEx,  extype),    issubclass(ReprEnumEx,  stdtype), msg)
                        self.assertEqual(   issubclass(StrEnumEx,   extype),    issubclass(StrEnumEx,   stdtype), msg)

            self.assertEqual(               issubclass(A,           extype),    issubclass(A,           stdtype), msg)
            self.assertEqual(               issubclass(B,           extype),    issubclass(B,           stdtype), msg)
            self.assertEqual(               issubclass(C,           extype),    issubclass(C,           stdtype), msg)
            self.assertEqual(               issubclass(D,           extype),    issubclass(D,           stdtype), msg)
            self.assertEqual(               issubclass(E,           extype),    issubclass(E,           stdtype), msg)

        def test_isinstance_std(localcls:type[EnumEx]):
            msg = f"Testing {localcls.__name__} isinstance of "
            val = localcls.V1
            self.assertIsInstance(                                                         val, StdEnum,        msg + f" {StdEnum.__name__}")
            if sys.version_info                                                                                                                     >= (3, 4):
                self.assertEqual(           isinstance(val, IntEnumEx),         isinstance(val, IntEnumEx),     msg + f" {IntEnumEx.__name__}")
                if sys.version_info                                                                                                                 >= (3, 6):
                    self.assertEqual(       isinstance(val, IntFlagEx),         isinstance(val, IntFlagEx),     msg + f" {IntFlagEx.__name__}")
                    self.assertEqual(       isinstance(val, FlagEx),            isinstance(val, FlagEx),        msg + f" {FlagEx.__name__}")
                    if sys.version_info                                                                                                             >= (3, 11):
                        self.assertEqual(   isinstance(val, ReprEnumEx),        isinstance(val, ReprEnumEx),    msg + f" {ReprEnumEx.__name__}")
                        self.assertEqual(   isinstance(val, StrEnumEx),         isinstance(val, StrEnumEx),     msg + f" {StrEnumEx.__name__}")

        test_issubclass_std(EnumEx,      StdEnum)

        if sys.version_info                                                 >= (3, 4):
            test_issubclass_std(        IntEnumEx,      StdIntEnum)
            if sys.version_info                                             >= (3, 6):
                test_issubclass_std(    IntFlagEx,      StdIntFlag)
                test_issubclass_std(    FlagEx,         StdFlag)
                if sys.version_info                                         >= (3, 11):
                    test_issubclass_std(ReprEnumEx,     StdReprEnum)
                    test_issubclass_std(StrEnumEx,      StdStrEnum)

        test_isinstance_std(A)
        test_isinstance_std(B)
        test_isinstance_std(C)
        test_isinstance_std(D)
        test_isinstance_std(E)
        
        # self.assertIsInstance(A.V1,             A)
        # self.assertIsInstance(A.V1,             enum.Enum)
        # self.assertIsInstance(A.V1,             enumex.EnumEx)
        # self.assertIsInstance(A.V1,             enum.IntEnum)
        # self.assertNotIsInstance(A.V1,          enum.Flag)
        # self.assertNotIsInstance(A.V1,          enum.IntFlag)
        # self.assertNotIsInstance(A.V1,          enum.StrEnum)

        # self.assertIsInstance(B.V1,             B)
        # self.assertIsInstance(B.V1,             enum.Enum)
        # self.assertIsInstance(B.V1,             enumex.EnumEx)
        # self.assertNotIsInstance(B.V1,          enum.IntEnum)
        # self.assertNotIsInstance(B.V1,          enum.Flag)
        # self.assertNotIsInstance(B.V1,          enum.IntFlag)
        # self.assertNotIsInstance(B.V1,          enum.StrEnum)

        # self.assertIsInstance(C.V1,             C)
        # self.assertIsInstance(C.V1,             enum.Enum)
        # self.assertIsInstance(C.V1,             enumex.EnumEx)
        # self.assertNotIsInstance(C.V1,          enum.IntEnum)
        # self.assertNotIsInstance(C.V1,          enum.Flag)
        # self.assertNotIsInstance(C.V1,          enum.IntFlag)
        # self.assertNotIsInstance(C.V1,          enum.StrEnum)

        # self.assertIsInstance(D.V1,             D)
        # self.assertIsInstance(D.V1,             enum.Enum)
        # self.assertIsInstance(D.V1,             enumex.EnumEx)
        # self.assertNotIsInstance(D.V1,          enum.IntEnum)
        # self.assertNotIsInstance(D.V1,          enum.Flag)
        # self.assertNotIsInstance(D.V1,          enum.IntFlag)
        # self.assertNotIsInstance(D.V1,          enum.StrEnum)

        # self.assertIsInstance(E.V1,             E)
        # self.assertIsInstance(E.V1,             enum.Enum)
        # self.assertIsInstance(E.V1,             enumex.EnumEx)
        # self.assertNotIsInstance(E.V1,          enum.IntEnum)
        # self.assertNotIsInstance(E.V1,          enum.Flag)
        # self.assertNotIsInstance(E.V1,          enum.IntFlag)
        # self.assertNotIsInstance(E.V1,          enum.StrEnum)
    
    def test_enumex_auto_inheritance(self):
        class A(EnumEx):
            V1 = autoex()
            V2 = '2'
            V3 = 3
        class B(A):
            V4 = autoex()
            V5 = autoex()

        self.assertIsInstance(A.V1,     A)
        self.assertIsInstance(B.V1,     A)
        self.assertIsInstance(B.V4,     A)
        self.assertNotIsInstance(A.V1,  B)
        self.assertEqual(1,             A.V1.value)
        self.assertEqual('2',           A.V2.value)
        self.assertEqual(3,             A.V3.value)
        self.assertEqual(1,             B.V1.value)
        self.assertEqual('2',           B.V2.value)
        self.assertEqual(3,             B.V3.value)
        self.assertEqual(4,             B.V4.value)
        self.assertEqual(5,             B.V5.value)
        self.assertEqual("A.V1",        str(A.V1))
        self.assertEqual("B.V1",        str(B.V1))

        self.assertListEqual([A.V1, A.V2, A.V3], list(A))
        self.assertListEqual([B.V1, B.V2, B.V3, B.V4, B.V5], list(B))

    def test_intenumex_auto_inheritance(self):
        class A(IntEnumEx):
            V1 = autoex()
            V2 = autoex()
            V3 = 3
        class B(A):
            V4 = autoex()
            V5 = autoex()

        self.assertIsInstance(A.V1,     A)
        self.assertIsInstance(B.V1,     A)
        self.assertIsInstance(B.V4,     A)
        self.assertNotIsInstance(A.V1,  B)
        self.assertEqual(1,             A.V1.value)
        self.assertEqual(2,             A.V2.value)
        self.assertEqual(3,             A.V3.value)
        self.assertEqual(1,             B.V1.value)
        self.assertEqual(2,             B.V2.value)
        self.assertEqual(3,             B.V3.value)
        self.assertEqual(4,             B.V4.value)
        self.assertEqual(5,             B.V5.value)
        self.assertGreater(B.V3,        A.V2)

        self.assertListEqual([A.V1, A.V2, A.V3], list(A))
        self.assertListEqual([A.V1, A.V2, A.V3, B.V4, B.V5], list(B))

    def test_intflagex_auto_inheritance(self):
        class A(IntFlagEx):
            F1 = autoex()
            F2 = autoex()
            F3 = 0b1100
        class B(A):
            F4 = autoex()
            F5 = autoex()

        self.assertIsInstance(A.F1,     A)
        self.assertIsInstance(B.F1,     A)
        self.assertIsInstance(B.F4,     A)
        self.assertIsInstance(B.F1,     B)
        self.assertNotIsInstance(A.F1,  B)
        self.assertEqual(1,             A.F1.value)
        self.assertEqual(2,             A.F2.value)
        self.assertEqual(0b1100,        A.F3.value)
        self.assertEqual(1,             A.F1.value)
        self.assertEqual(2,             B.F2.value)
        self.assertEqual(0b1100,        B.F3.value)
        self.assertEqual(0b10000,       B.F4.value)
        self.assertEqual(0b100000,      B.F5.value)

        print(", ".join(str(v) for v in list(A)))
        print(", ".join(str(v) for v in list(B)))

        self.assertListEqual([A.F1, A.F2], list(A))
        self.assertListEqual([A.F1, A.F2, B.F4, B.F5], list(B))

    def test_strenumex_auto_inheritance(self):
        class A(StrEnumEx):
            V1 = autoex()
            V2 = '2'
            V3 = V2
        class B(A):
            V4 = autoex()
            V5 = autoex()

        self.assertIsInstance(A.V1,     A)
        self.assertIsInstance(B.V1,     A)
        self.assertIsInstance(B.V4,     A)
        self.assertIsInstance(B.V1,     B)
        self.assertNotIsInstance(A.V1,  B)
        self.assertEqual('v1',          A.V1.value)
        self.assertEqual('2',           A.V2.value)
        self.assertEqual('2',           A.V3.value)
        self.assertEqual('v1',          B.V1.value)
        self.assertEqual('2',           B.V2.value)
        self.assertEqual('2',           B.V3.value)
        self.assertEqual('v4',          B.V4.value)
        self.assertEqual('v5',          B.V5.value)

        self.assertListEqual([A.V1, A.V3], list(A))
        self.assertListEqual([A.V1, A.V3, B.V4, B.V5], list(B))

    def test_errors(self):
        class A(EnumEx):
            V1 = autoex()
            V2 = '2'
            V3 = 3
        class B(A):
            V4 = autoex()
            V5 = autoex()

        with self.assertRaises(TypeError) as ec:
            class A(EnumEx):
                V1 = autoex()
                V2 = '2'
                V3 = 3
            class B(A):
                V3 = A.V3
        self.assertEqual("'V3' already defined as 3", ec.exception.args[0])
        
    def test_instance_methods(self):
        class A(EnumEx):
            V1 = autoex()
            V2 = autoex()

            def custom_format(self):
                return f"A.{self.name} : {self.value}"
        
        class B(A):
            V3 = autoex()
            V4 = autoex()

            def custom_format(self):
                return f"B.{self.name} : {self.value}"
        
        self.assertEqual("A.V1 : 1", A.V1.custom_format())
        self.assertEqual("B.V1 : 1", B.V1.custom_format())

    def test_abstract_methods(self):
        class A(EnumEx):
            V1 = autoex()
            
            def fee(cls):
                pass

            @abstractmethod
            def foo(self):
                pass

            def bar(self):
                pass
                return "A"
            
            @abstractmethod
            def foe(self):
                return
            
            @abstractmethod
            def fum():
                ...
            
        class B(A):
            V2 = autoex()

            def fee(self):
                return "B"
            
            def foo(self):
                return "B"            

        class C(B):     
            def fee(self):
                return "C"
                   
            def bar(self):
                return "C"
            
            def fum():
                return "C"

        class X(EnumEx):
            V1 = autoex()

            def foo(self):
                return "X"
            
        self.assertTrue(is_method_empty(A.fee),             msg="A fee is empty")
        self.assertTrue(is_method_empty(A.foo),             msg="A foo is empty")
        self.assertTrue(is_method_empty(A.fum),             msg="A fum is empty")
        self.assertFalse(is_method_empty(A.bar),            msg="A bar not empty")
        self.assertFalse(is_method_empty(A.foe),            msg="A foe not empty")

        self.assertTrue(is_method_empty(B.fum),             msg="B fum is empty")
        self.assertFalse(is_method_empty(B.fee),            msg="B fee not empty")
        self.assertFalse(is_method_empty(B.foo),            msg="B foo not empty")
        self.assertFalse(is_method_empty(B.bar),            msg="B bar not empty")
        self.assertFalse(is_method_empty(B.foe),            msg="B foe not empty")

        self.assertFalse(is_method_empty(C.fee),            msg="C fee not empty")
        self.assertFalse(is_method_empty(C.foo),            msg="C foo not empty")
        self.assertFalse(is_method_empty(C.bar),            msg="C bar not empty")
        self.assertFalse(is_method_empty(C.foe),            msg="C foe not empty")
        self.assertFalse(is_method_empty(C.fum),            msg="C fum not empty")

        self.assertTrue(is_abstract_enum(A),                msg="A is abstract enum")
        self.assertTrue(is_abstract_enum(B),                msg="B is abstract enum")
        self.assertTrue(is_abstract_enum(C),                msg="C is abstract enum")
        self.assertFalse(is_abstract_enum(X),               msg="X not abstract enum")
        
        self.assertTrue(is_unimplemented_abstract_enum(A),  msg="A is unimplemented abstract enum")
        self.assertTrue(is_unimplemented_abstract_enum(B),  msg="B is unimplemented abstract enum")
        self.assertFalse(is_unimplemented_abstract_enum(C), msg="C not unimplemented abstract enum")
        self.assertFalse(is_unimplemented_abstract_enum(X), msg="X not unimplemented abstract enum")

        def assert_all_in(col, prefix, *args):
            count = len(args)
            self.assertEqual(count, len(col), msg=f"{prefix} count")
            for arg in args:
                self.assertIn(arg, col, msg=f"{prefix} {arg} in")

        a_abstracts = get_abstract_methods(A)
        b_abstracts = get_abstract_methods(B)
        c_abstracts = get_abstract_methods(C)
        x_abstracts = get_abstract_methods(X)

        assert_all_in(a_abstracts, "A abstracts ", 'foo', 'fum')
        assert_all_in(b_abstracts, "B abstracts ", 'foo', 'fum')
        assert_all_in(c_abstracts, "C abstracts ", 'foo', 'fum')
        assert_all_in(x_abstracts, "X abstracts ")

        a_unimp = get_unimplemented_abstract_methods(A)
        b_unimp = get_unimplemented_abstract_methods(B)
        c_unimp = get_unimplemented_abstract_methods(C)
        x_unimp = get_unimplemented_abstract_methods(X)

        assert_all_in(a_unimp, "A unimplemented abstracts ", 'foo', 'fum')
        assert_all_in(b_unimp, "B unimplemented abstracts ", 'fum')
        assert_all_in(c_unimp, "C unimplemented abstracts ")
        assert_all_in(x_unimp, "X unimplemented abstracts ")

    def test_abstract_static_methods(self):
        class A(EnumEx):
            V1 = autoex()

            @staticmethod
            @abstractmethod
            def fee():
                pass

            @staticmethod
            @abstractmethod
            def foo():
                pass
            
            @staticmethod
            @abstractmethod
            def bar():
                pass
            
        class B(A):
            V2 = autoex()    

            @staticmethod
            def fee():
                return "B"   
            
            @staticmethod
            def foo():
                return "B"  

        class C(B):     
            @staticmethod       
            def foo():
                return "C"
            
            @staticmethod
            def bar():
                return "C"
            

        class X(EnumEx):
            V1 = autoex()

            @staticmethod
            @abstractmethod
            def soo(self):
                return "X"
        
        self.assertTrue(is_method_empty(A.fee),             msg="A fee is empty")
        self.assertTrue(is_method_empty(A.foo),             msg="A foo is empty")
        self.assertTrue(is_method_empty(A.bar),             msg="A bar is empty")

        self.assertTrue(is_method_empty(B.bar),             msg="B bar is empty")
        self.assertFalse(is_method_empty(B.fee),            msg="B fee is empty")
        self.assertFalse(is_method_empty(B.foo),            msg="B foo is empty")

        self.assertFalse(is_method_empty(C.fee),            msg="C fee not empty")
        self.assertFalse(is_method_empty(C.foo),            msg="C foo not empty")
        self.assertFalse(is_method_empty(C.bar),            msg="C bar not empty")
        self.assertFalse(is_method_empty(X.soo),            msg="X soo not empty")

        self.assertTrue(is_abstract_enum(A),                msg="A is abstract enum")
        self.assertTrue(is_abstract_enum(B),                msg="B is abstract enum")
        self.assertTrue(is_abstract_enum(C),                msg="C is abstract enum")
        self.assertFalse(is_abstract_enum(X),               msg="X not abstract enum")
        
        self.assertTrue(is_unimplemented_abstract_enum(A),  msg="A is unimplemented abstract enum")
        self.assertTrue(is_unimplemented_abstract_enum(B),  msg="B is unimplemented abstract enum")
        self.assertFalse(is_unimplemented_abstract_enum(C), msg="C not unimplemented abstract enum")
        self.assertFalse(is_unimplemented_abstract_enum(X), msg="X not unimplemented abstract enum")

        def assert_all_in(col, prefix, *args):
            count = len(args)
            self.assertEqual(count, len(col), msg=f"{prefix} count")
            for arg in args:
                self.assertIn(arg, col, msg=f"{prefix} {arg} in")

        a_abstracts = get_abstract_methods(A)
        b_abstracts = get_abstract_methods(B)
        c_abstracts = get_abstract_methods(C)
        x_abstracts = get_abstract_methods(X)

        assert_all_in(a_abstracts, "A abstracts ", 'fee', 'foo', 'bar')
        assert_all_in(b_abstracts, "B abstracts ", 'fee', 'foo', 'bar')
        assert_all_in(c_abstracts, "C abstracts ", 'fee', 'foo', 'bar')
        assert_all_in(x_abstracts, "X abstracts ")

        a_unimp = get_unimplemented_abstract_methods(A)
        b_unimp = get_unimplemented_abstract_methods(B)
        c_unimp = get_unimplemented_abstract_methods(C)
        x_unimp = get_unimplemented_abstract_methods(X)

        assert_all_in(a_unimp, "A unimplemented abstracts ", 'fee', 'foo', 'bar')
        assert_all_in(b_unimp, "B unimplemented abstracts ", 'bar')
        assert_all_in(c_unimp, "C unimplemented abstracts ")
        assert_all_in(x_unimp, "X unimplemented abstracts ")

        _assert_invalidabstract(self, A, 1, 'fee', 'foo', 'bar')
        _assert_invalidabstract(self, B, 1, 'bar')

        v = C(1)
        x = X(1)

    def test_abstract_class_methods(self):
        class A(EnumEx):
            V1 = autoex()

            @classmethod
            @abstractmethod
            def fee():
                pass

            @classmethod
            @abstractmethod
            def foo():
                pass
            
            @classmethod
            @abstractmethod
            def bar():
                pass
            
        class B(A):
            V2 = autoex()    

            @classmethod
            def fee():
                return "B"   
            
            @classmethod
            def foo():
                return "B"  

        class C(B):  
            @classmethod          
            def foo():
                return "C"
            
            @classmethod
            def bar():
                return "C"
            

        class X(EnumEx):
            V1 = autoex()

            @classmethod
            @abstractmethod
            def coo(self):
                return "coo"
        
        self.assertTrue(is_method_empty(A.fee),             msg="A fee is empty")
        self.assertTrue(is_method_empty(A.foo),             msg="A foo is empty")
        self.assertTrue(is_method_empty(A.bar),             msg="A bar is empty")

        self.assertTrue(is_method_empty(B.bar),             msg="B bar is empty")
        self.assertFalse(is_method_empty(B.fee),            msg="B fee is empty")
        self.assertFalse(is_method_empty(B.foo),            msg="B foo is empty")

        self.assertFalse(is_method_empty(C.fee),            msg="C fee not empty")
        self.assertFalse(is_method_empty(C.foo),            msg="C foo not empty")
        self.assertFalse(is_method_empty(C.bar),            msg="C bar not empty")
        self.assertFalse(is_method_empty(X.coo),            msg="X coo not empty")

        self.assertTrue(is_abstract_enum(A),                msg="A is abstract enum")
        self.assertTrue(is_abstract_enum(B),                msg="B is abstract enum")
        self.assertTrue(is_abstract_enum(C),                msg="C is abstract enum")
        self.assertFalse(is_abstract_enum(X),               msg="X not abstract enum")
        
        self.assertTrue(is_unimplemented_abstract_enum(A),  msg="A is unimplemented abstract enum")
        self.assertTrue(is_unimplemented_abstract_enum(B),  msg="B is unimplemented abstract enum")
        self.assertFalse(is_unimplemented_abstract_enum(C), msg="C not unimplemented abstract enum")
        self.assertFalse(is_unimplemented_abstract_enum(X), msg="X not unimplemented abstract enum")

        def assert_all_in(col, prefix, *args):
            count = len(args)
            self.assertEqual(count, len(col), msg=f"{prefix} count")
            for arg in args:
                self.assertIn(arg, col, msg=f"{prefix} {arg} in")

        a_abstracts = get_abstract_methods(A)
        b_abstracts = get_abstract_methods(B)
        c_abstracts = get_abstract_methods(C)
        x_abstracts = get_abstract_methods(X)

        assert_all_in(a_abstracts, "A abstracts ", 'fee', 'foo', 'bar')
        assert_all_in(b_abstracts, "B abstracts ", 'fee', 'foo', 'bar')
        assert_all_in(c_abstracts, "C abstracts ", 'fee', 'foo', 'bar')
        assert_all_in(x_abstracts, "X abstracts ")

        a_unimp = get_unimplemented_abstract_methods(A)
        b_unimp = get_unimplemented_abstract_methods(B)
        c_unimp = get_unimplemented_abstract_methods(C)
        x_unimp = get_unimplemented_abstract_methods(X)

        assert_all_in(a_unimp, "A unimplemented abstracts ", 'fee', 'foo', 'bar')
        assert_all_in(b_unimp, "B unimplemented abstracts ", 'bar')
        assert_all_in(c_unimp, "C unimplemented abstracts ")
        assert_all_in(x_unimp, "X unimplemented abstracts ")

        _assert_invalidabstract(self, A, 1, 'fee', 'foo', 'bar')
        _assert_invalidabstract(self, B, 1, 'bar')

        v = C(1)
        x = X(1)
        

    def test_abstract_properties(self):
        class A(EnumEx):
            V1 = autoex()

            @property
            @abstractmethod
            def pie(self):
                pass
            
            @property
            @abstractmethod
            def poo(self):
                pass

            @abstractmethod
            def get_poof(self):
                pass

            @abstractmethod
            def set_poof(self, value):
                pass

            @abstractmethod
            def del_poof(self):
                pass

            poof = property(get_poof, set_poof, del_poof)  
            
        class B(A):
            V2 = autoex()

            def __init__(self, *args, **kwds):
                super().__init__(*args, **kwds)
                self._poof = 'B'

            @property
            def pie(self):
                return 'B'

            def get_poof(self):
                return 'B'
            
            def set_poof(self, value):
                return

            poof = property(get_poof)   

        class C(B):       
            @property
            def pie(self):
                return 'C'

            @property
            def poo(self):
                return "C"
            
            def get_poof(self):
                return self._poof

            def set_poof(self, value):
                self.__setattr__('_poof', value)

            def del_poof(self):
                del self._poof

            def get_goof(self):
                return super().get_goof()

            poof = property(get_poof, set_poof, del_poof)  

        class D(A):
            V2 = autoex()

            def __init__(self, *args, **kwds):
                super().__init__(*args, **kwds)
                self._poof = 'B'

            @property
            def pie(self):
                return 'B'

            def get_poof(self):
                return 'B'
            
            def set_poof(self, value):
                return
            
            def del_poof(self, value):
                return

            poof = property(get_poof)   
            
        self.assertTrue(is_method_empty(A.get_poof),            msg="A get_poof is empty")
        self.assertTrue(is_method_empty(A.set_poof),            msg="A set_poof is empty")
        self.assertTrue(is_method_empty(A.del_poof),            msg="A del_poof is empty")
        self.assertTrue(is_method_empty(A.__dict__['pie']),     msg="A pie is empty")
        self.assertTrue(is_method_empty(A.__dict__['poo']),     msg="A poo is empty")
        self.assertTrue(is_method_empty(A.__dict__['poof']),    msg="A poof is empty")

        self.assertTrue(is_method_empty(B.del_poof),            msg="B del_poof is empty")
        try:
            self.assertTrue(is_method_empty(B.__dict__['poo']),     msg="B poo is empty")
        except:
            pass
        self.assertFalse(is_method_empty(B.get_poof),           msg="B get_poof not empty")
        self.assertFalse(is_method_empty(B.set_poof),           msg="B set_poof not empty")
        self.assertFalse(is_method_empty(B.__dict__['pie']),    msg="B pie not empty")
        self.assertFalse(is_method_empty(B.__dict__['poof']),   msg="B poof not empty")

        self.assertFalse(is_method_empty(C.get_poof),            msg="C get_poof not empty")
        self.assertFalse(is_method_empty(C.set_poof),            msg="C set_poof not empty")
        self.assertFalse(is_method_empty(C.del_poof),            msg="C del_poof not empty")
        self.assertFalse(is_method_empty(C.__dict__['pie']),     msg="C pie not empty")
        self.assertFalse(is_method_empty(C.__dict__['poo']),     msg="C poo not empty")
        self.assertFalse(is_method_empty(C.__dict__['poof']),    msg="C poof not empty")

        try:
            self.assertTrue(is_method_empty(D.__dict__['poo']),     msg="D poo is empty")
        except:
            pass
        self.assertFalse(is_method_empty(D.get_poof),           msg="D get_poof not empty")
        self.assertFalse(is_method_empty(D.set_poof),           msg="D set_poof not empty")
        self.assertFalse(is_method_empty(D.del_poof),            msg="D del_poof not empty")
        self.assertFalse(is_method_empty(D.__dict__['pie']),    msg="D pie not empty")
        self.assertFalse(is_method_empty(D.__dict__['poof']),   msg="D poof not empty")

        self.assertTrue(is_abstract_enum(A),                    msg="A abstract is enum")
        self.assertTrue(is_abstract_enum(B),                    msg="B abstract is enum")
        self.assertTrue(is_abstract_enum(C),                    msg="C abstract is enum")

        self.assertTrue(is_unimplemented_abstract_enum(A),      msg="A is unimplemented abstract enum")
        self.assertTrue(is_unimplemented_abstract_enum(B),      msg="B is unimplemented abstract enum")
        self.assertFalse(is_unimplemented_abstract_enum(C),     msg="C not unimplemented abstract enum")

        def assert_all_in(col, prefix, *args):
            count = len(args)
            self.assertEqual(count, len(col), msg=f"{prefix} count")
            for arg in args:
                self.assertIn(arg, col, msg=f"{prefix} {arg} in")

        a_abstracts = get_abstract_methods(A)
        b_abstracts = get_abstract_methods(B)
        c_abstracts = get_abstract_methods(C)
        d_abstracts = get_abstract_methods(D)

        assert_all_in(a_abstracts, "A abstracts ", 'pie', 'poo', 'poof', 'get_poof', 'set_poof', 'del_poof')
        assert_all_in(b_abstracts, "B abstracts ", 'pie', 'poo', 'poof', 'get_poof', 'set_poof', 'del_poof')
        assert_all_in(c_abstracts, "C abstracts ", 'pie', 'poo', 'poof', 'get_poof', 'set_poof', 'del_poof')
        assert_all_in(d_abstracts, "D abstracts ", 'pie', 'poo', 'poof', 'get_poof', 'set_poof', 'del_poof')

        a_unimp = get_unimplemented_abstract_methods(A)
        b_unimp = get_unimplemented_abstract_methods(B)
        c_unimp = get_unimplemented_abstract_methods(C)
        d_unimp = get_unimplemented_abstract_methods(D)

        assert_all_in(a_unimp, "A unimplemented abstracts ", 'pie', 'poo', 'poof', 'get_poof', 'set_poof', 'del_poof')
        assert_all_in(b_unimp, "B unimplemented abstracts ", 'poo', 'del_poof')
        assert_all_in(c_unimp, "C unimplemented abstracts ")
        assert_all_in(d_unimp, "B unimplemented abstracts ", 'poo')

        _assert_invalidabstract(self, A, 1, 'pie', 'poo', 'poof', 'get_poof', 'set_poof', 'del_poof')
        _assert_invalidabstract(self, B, 1, 'poo', 'del_poof')
        _assert_invalidabstract(self, D, 1, 'poo')

        v = C(1)


    def test_abstract_enumex(self):        
        class A(EnumEx):
            V1 = autoex()
            V2 = autoex()

            @abstractmethod
            def foo(self):
                pass

            @classmethod
            @abstractmethod
            def cfoo(cls):
                pass

            @staticmethod
            @abstractmethod
            def sfoo():
                pass
        
        class B(A):
            V3 = autoex()
            V4 = autoex()

            def foo(self):
                return "foo"
                pass

            def cfoo(cls):
                return "cfoo"

            def sfoo():
                return "sfoo"
            
        class C(B):
            pass
        
        class D(C):
            pass
            
        class X(A):
            V3 = autoex()
            V4 = autoex()

            def foo(self):
                pass

            def cfoo(cls):
                pass

            def sfoo():
                pass

        class Y(X):
            pass
        
        class Z(Y):
            pass

        v = B(1 | 2)
        v = C(1 | 2)
        v = D(1 | 2)

        _assert_invalidabstract(self, Z, lambda: Z(1 | 2), 'foo', 'cfoo', 'sfoo')
        _assert_invalidabstract(self, A, lambda: A(1 | 2), 'foo', 'cfoo', 'sfoo')

    def test_abstract_intenum(self):        
        class A(IntEnumEx):
            V1 = autoex()
            V2 = autoex()

            @abstractmethod
            def foo(self):
                pass

            @classmethod
            @abstractmethod
            def cfoo(cls):
                pass

            @staticmethod
            @abstractmethod
            def sfoo():
                pass
        
        class B(A):
            V3 = autoex()
            V4 = autoex()

            def foo(self):
                return "foo"
                pass

            def cfoo(cls):
                return "cfoo"

            def sfoo():
                return "sfoo"
            
        class C(B):
            pass
        
        class D(C):
            pass
            
        class X(A):
            V3 = autoex()
            V4 = autoex()

            def foo(self):
                pass

            def cfoo(cls):
                pass

            def sfoo():
                pass

        class Y(X):
            pass
        
        class Z(Y):
            pass

        v = B(1 | 2)
        v = C(1 | 2)
        v = D(1 | 2)

        _assert_invalidabstract(self, Z, lambda: Z(1 | 2), 'foo', 'cfoo', 'sfoo')
        _assert_invalidabstract(self, A, lambda: A(B.V1 | X.V2), 'foo', 'cfoo', 'sfoo')

    def test_abstract_intflag(self):
        class A(IntFlagEx):
            V1 = autoex()
            V2 = autoex()

            @abstractmethod
            def foo(self):
                pass

            @classmethod
            @abstractmethod
            def cfoo(cls):
                pass

            @staticmethod
            @abstractmethod
            def sfoo():
                pass

        
        class B(A):
            V3 = autoex()
            V4 = autoex()

            def foo(self):
                return "foo"

            def cfoo(cls):
                return "cfoo"

            def sfoo():
                return "sfoo"
            
        class C(B):
            pass
        
        class D(C):
            pass
            
        class X(A):
            V3 = autoex()
            V4 = autoex()

            def foo(self):
                return "foo"

            def cfoo(cls):
                pass

            def sfoo():
                pass

        class Y(X):
            pass
        
        class Z(Y):
            pass

        v = B(1 | 64)
        v = C(1 | 64)
        v = D(1 | 64)

        _assert_invalidabstract(self, Z, lambda: Z(1 | 64), 'cfoo', 'sfoo')
        _assert_invalidabstract(self, A, lambda: A(B.V3 | X.V4), 'foo', 'cfoo', 'sfoo')
        _assert_invalidabstract(self, X, lambda: ~X.V4, 'cfoo', 'sfoo')
        v = ~B.V1
        
    def test_abstract_strenumex(self):        
        class A(StrEnumEx):
            V1 = autoex()
            V2 = autoex()

            @abstractmethod
            def foo(self):
                pass

            @classmethod
            @abstractmethod
            def cfoo(cls):
                pass

            @staticmethod
            @abstractmethod
            def sfoo():
                pass
        
        class B(A):
            V3 = autoex()
            V4 = autoex()

            def foo(self):
                return "foo"
                pass

            def cfoo(cls):
                return "cfoo"

            def sfoo():
                return "sfoo"
            
        class C(B):
            pass
        
        class D(C):
            pass
            
        class X(A):
            V3 = autoex()
            V4 = autoex()

            def foo(self):
                pass

            def cfoo(cls):
                pass

            def sfoo():
                pass

        class Y(X):
            pass
        
        class Z(Y):
            pass

        v = B('v3')
        v = C('v4')
        v = D('v4')

        _assert_invalidabstract(self, Z, 'v4', 'foo', 'cfoo', 'sfoo')
        _assert_invalidabstract(self, A, 'v2', 'foo', 'cfoo', 'sfoo')

def _assert_invalidabstract(case:unittest.TestCase, cls:EnumEx, initvalue:Union[object,Callable], *args):
    with case.assertRaises(TypeError) as ec:
        if isinstance(initvalue, Callable):
            v = initvalue()
        else:
            v = cls(initvalue)
    count = len(args)
    case.assertEqual(count + 1, len(ec.exception.args))
    case.assertEqual(f"Can't instantiate abstract class {cls.__name__} with abstract method{'' if count == 1 else 's'}", ec.exception.args[0])
    method_args = ec.exception.args[1:]
    for arg in args:
        case.assertIn(arg, method_args)

if __name__ == "__main__":
    unittest.main()