# Add package directory to path for debugging
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import unittest 
from enumex import *
from enumex import autoex as auto
from enum import Enum as StdEnum

_SYS_VERSION_MAJOR_MINOR_ = sys.version_info[:2]

if _SYS_VERSION_MAJOR_MINOR_ >= (3, 4): 
    from enum import IntEnum as StdIntEnum
    if _SYS_VERSION_MAJOR_MINOR_ >= (3, 6):
        from enum import IntFlag as StdIntFlag, Flag as StdFlag, auto as StdAuto
        if _SYS_VERSION_MAJOR_MINOR_ >= (3, 11):
            from enum import StrEnum as StdStrEnum, ReprEnum as StdReprEnum
from abc import ABC, abstractmethod
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
    
    def test_enumex_auto_inheritance(self):
        if _SYS_VERSION_MAJOR_MINOR_ < (3, 13):
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
        else:
            class A(EnumEx):
                V1 = autoex()
                V2 = 2
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
        if _SYS_VERSION_MAJOR_MINOR_ < (3, 13):
            with self.assertWarns(DeprecationWarning) as wc:
                class A(EnumEx):
                    V1 = autoex()
                    V2 = '2'
                    V3 = 3
                class B(A):
                    V4 = autoex()
                    V5 = autoex()
            self.assertEqual("In 3.13 the default `auto()`/`_generate_next_value_` will require all values to be sortable and support adding +1\nand the value returned will be the largest value in the enum incremented by 1", wc.warning.args[0])

            with self.assertRaises(TypeError) as ec:
                class A(EnumEx):
                    V1 = autoex()
                    V2 = '2'
                    V3 = 3
                class B(A):
                    V3 = A.V3
            self.assertEqual("'V3' already defined as 3", ec.exception.args[0])
        else:
            with self.assertRaises(TypeError) as ec:
                class A(EnumEx):
                    V1 = autoex()
                    V2 = '2'
                    V3 = 3
                class B(A):
                    V4 = autoex()
                    V5 = autoex()
            self.assertEqual("unable to sort non-numeric values", ec.exception.args[0])

            with self.assertRaises(TypeError) as ec:
                class A(EnumEx):
                    V1 = autoex()
                    V2 = 2
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
        class A(ABC, EnumEx):
            V1 = autoex()
            
            @abstractmethod
            def foo(self):
                pass

            @abstractmethod
            def bar(self):
                pass
            
            @abstractmethod
            def baz(self):
                pass

            @abstractmethod
            def doe(self):
                pass

            def doe(self):
                pass
            
        class B(A):
            V2 = autoex()

            def foo(self):
                pass   

        class C(B):     
            def bar(self):
                pass
                   
        class D(C):
            def baz(self):
                pass

        class X(ABC, EnumEx):
            V1 = autoex()
            def foo(self):
                pass

            @abstractmethod
            def foo(self):
                pass

        class Y(EnumEx):
            V1 = autoex()
            def foo(self):
                pass

            @abstractmethod
            def foo(self):
                pass
            
        _assert_invalidabstract(self, A, 1, 'foo', 'bar', 'baz')
        _assert_invalidabstract(self, B, 1, 'bar', 'baz')
        _assert_invalidabstract(self, C, 1, 'baz')
        _assert_invalidabstract(self, X, 1, 'foo')

        v = D(1)
        v = Y(1)
        self.assertEqual(len(D.__abstractmethods__), 0, msg="D __abstractmethods__")
        self.assertEqual(len(Y.__abstractmethods__), 1, msg="Y __abstractmethods__")

    def test_abstract_static_methods(self):
        class A(ABC, EnumEx):
            V1 = autoex()

            @staticmethod
            @abstractmethod
            def foo():
                pass
            
        class B(A):
            V2 = autoex()    

            @staticmethod
            def foo():
                pass 

        _assert_invalidabstract(self, A, 1, 'foo')
        b = B(1)

    def test_abstract_class_methods(self):
        class A(ABC, EnumEx):
            V1 = autoex()

            @classmethod
            @abstractmethod
            def foo(cls):
                pass
            
        class B(A):
            V2 = autoex()    

            @classmethod
            def foo(cls):
                pass 

        _assert_invalidabstract(self, A, 1, 'foo')
        b = B(1)
        

    def test_abstract_properties(self):
        class A(ABC, EnumEx):
            V1 = autoex()

            @property
            @abstractmethod
            def foo(self):
                pass
            
            @property
            @abstractmethod
            def bar(self):
                pass

            @abstractmethod
            def get_baz(self):
                pass

            @abstractmethod
            def set_baz(self, value):
                pass

            @abstractmethod
            def del_baz(self):
                pass

            baz = property(get_baz, set_baz, del_baz)  
            
        class B(A):
            V2 = autoex()

            @property
            def foo(self):
                pass

            def get_baz(self):
                pass
            
            def set_baz(self, value):
                pass

            bar = property(get_baz)   

        class C(B):       
            @property
            def bar(self):
                return "C"

            def del_baz(self):
                pass

            baz = property(B.get_baz, B.set_baz, del_baz)  
            
        _assert_invalidabstract(self, A, 1, 'foo', 'bar', 'get_baz', 'set_baz', 'del_baz', 'baz')
        _assert_invalidabstract(self, B, 1, 'del_baz')
        v = C(1)

    def test_flagex_operators(self):
        class A(FlagEx):
            F1 = autoex()
            F2 = autoex()
            F3 = autoex()
            F4 = autoex()
        class B(A):
            F5 = autoex()
            F6 = autoex()

        from enum import Flag, auto
        class X(Flag):
            F1 = auto()
            F2 = auto()
            F3 = auto()
            F4 = auto()
            F5 = auto()
            F6 = auto()

        or_std_result  = X.F3 | X.F1
        and_std_result = X.F1 & X.F1
        xor_std_result = X.F1 ^ X.F2
        or_result  = A.F3 | A.F1
        and_result = A.F1 & A.F1
        xor_result = A.F1 ^ A.F2

        self.assertIsInstance(or_result,  A,                        msg="OR is A")
        self.assertIsInstance(and_result, A,                        msg="AND is A")
        self.assertIsInstance(xor_result, A,                        msg="XOR is A")
        self.assertEqual(0b101,     or_result.value,                msg="A | A equal")
        self.assertEqual(1,         and_result.value,               msg="A & A equal")
        self.assertEqual(0b11,      xor_result.value,               msg="A ^ A equal")
        self.assertEqual(or_std_result.value, or_result.value,      msg="OR IntFlagEx == IntFlag")
        self.assertEqual(and_std_result.value, and_result.value,    msg="AND IntFlagEx == IntFlag")
        self.assertEqual(xor_std_result.value, xor_result.value,    msg="XOR IntFlagEx == IntFlag")

        or_std_result  = X.F3 | X.F1
        and_std_result = X.F1 & X.F1
        xor_std_result = X.F1 ^ X.F2
        or_result  = B.F3 | A.F1
        and_result = B.F1 & A.F1
        xor_result = B.F1 ^ A.F2

        self.assertIsInstance(or_result,  B,                        msg="OR is B")
        self.assertIsInstance(and_result, B,                        msg="AND is B")
        self.assertIsInstance(xor_result, B,                        msg="XOR is B")
        self.assertEqual(0b101,     or_result.value,                msg="B | A equal")
        self.assertEqual(1,         and_result.value,               msg="B & A equal")
        self.assertEqual(0b11,      xor_result.value,               msg="B ^ A equal")
        self.assertEqual(or_std_result.value, or_result.value,      msg="OR IntFlagEx == IntFlag")
        self.assertEqual(and_std_result.value, and_result.value,    msg="AND IntFlagEx == IntFlag")
        self.assertEqual(xor_std_result.value, xor_result.value,    msg="XOR IntFlagEx == IntFlag")

        with self.assertRaises(TypeError) as ec:
            or_result = 0b11 | A.F3
        self.assertEqual("unsupported operand type(s) for |: 'int' and 'A'", ec.exception.args[0])

        with self.assertRaises(TypeError) as ec:
            or_result = 0b11 & A.F3
        self.assertEqual("unsupported operand type(s) for &: 'int' and 'A'", ec.exception.args[0])

        with self.assertRaises(TypeError) as ec:
            or_result = 0b11 ^ A.F3
        self.assertEqual("unsupported operand type(s) for ^: 'int' and 'A'", ec.exception.args[0])

    def test_flagex_not_operator_default(self):
        from enum import Flag
        class A(FlagEx):
            F1 = autoex()
            F2 = autoex()
            F3 = autoex()
            F4 = autoex()
        class B(A):
            F5 = autoex()
            F6 = autoex()

        class X(Flag):
            F1 = auto()
            F2 = auto()
            F3 = auto()
            F4 = auto()
        class Y(Flag):
            F1 = auto()
            F2 = auto()
            F3 = auto()
            F4 = auto()
            F5 = auto()
            F6 = auto()

        std_result = ~X.F1
        not_result = ~A.F1
        expected = ~1 & 0b1111

        self.assertIsInstance(not_result, A,                    msg="NOT is A")
        self.assertEqual(expected, not_result.value,            msg="~ equal")
        self.assertEqual(std_result.value, not_result.value,    msg="~IntFlagEx == ~IntFlag")

        std_result = ~Y.F5
        not_result = ~B.F5
        expected = ~(1 << 4) & 0b111111

        self.assertIsInstance(not_result, B,                    msg="NOT is B")
        self.assertEqual(expected, not_result.value,            msg="~ equal")
        self.assertEqual(std_result.value, not_result.value,    msg="~IntFlagEx == ~IntFlag")

    def test_intflagex_operators(self):
        class A(IntFlagEx):
            F1 = autoex()
            F2 = autoex()
            F3 = autoex()
            F4 = autoex()
        class B(A):
            F5 = autoex()
            F6 = autoex()

        from enum import IntFlag, auto
        class X(IntFlag):
            F1 = auto()
            F2 = auto()
            F3 = auto()
            F4 = auto()

        or_result       = A.F3 | 0b11
        and_result      = A.F1 & 0b11
        xor_result      = A.F1 ^ 0b11
        or_std_result   = X.F3 | 0b11
        and_std_result  = X.F1 & 0b11
        xor_std_result  = X.F1 ^ 0b11

        self.assertIsInstance(or_result,    A,              msg="OR is A")
        self.assertIsInstance(and_result,   A,              msg="AND is A")
        self.assertIsInstance(xor_result,   A,              msg="XOR is A")
        self.assertEqual(0b111,             or_result,      msg="A | int OR")
        self.assertEqual(1,                 and_result,     msg="A & int AND")
        self.assertEqual(0b10,              xor_result,     msg="A ^ int XOR")
        self.assertEqual(or_std_result,     or_result,      msg="IntFlagEx == IntFlag OR")
        self.assertEqual(and_std_result,    and_result,     msg="IntFlagEx == IntFlag AND")
        self.assertEqual(xor_std_result,    xor_result,     msg="IntFlagEx == IntFlag XOR")

        or_result  = A.F3 | A.F1
        and_result = A.F1 & A.F1
        xor_result = A.F1 ^ (A.F2 | 0b101)

        self.assertIsInstance(or_result,  A,    msg="OR is A")
        self.assertIsInstance(and_result, A,    msg="AND is A")
        self.assertIsInstance(xor_result, A,    msg="XOR is A")
        self.assertEqual(0b101,     or_result,  msg="A | A equal")
        self.assertEqual(1,         and_result, msg="A & A equal")
        self.assertEqual(0b110,     xor_result, msg="A ^ A equal")

        or_result  = B.F5 | 0b11
        and_result = B.F1 & 0b11
        xor_result = B.F1 ^ 0b10

        self.assertIsInstance(or_result,  B,    msg="OR is B")
        self.assertIsInstance(and_result, B,    msg="AND is B")
        self.assertIsInstance(xor_result, B,    msg="XOR is B")
        self.assertEqual(0b10011,   or_result,  msg="B | int equal")
        self.assertEqual(1,         and_result, msg="B & int equal")
        self.assertEqual(0b11,      xor_result, msg="B ^ int equal")

        or_result  = B.F3 | A.F1
        and_result = B.F1 & A.F1
        xor_result = B.F1 ^ A.F2

        self.assertIsInstance(or_result,  B,    msg="OR is B")
        self.assertIsInstance(and_result, B,    msg="AND is B")
        self.assertIsInstance(xor_result, B,    msg="XOR is B")
        self.assertEqual(0b101,     or_result,  msg="B | A equal")
        self.assertEqual(1,         and_result, msg="B & A equal")
        self.assertEqual(0b11,      xor_result, msg="B ^ A equal")

        or_result  = 0b11 | A.F3
        and_result = 0b11 & A.F1
        xor_result = 0b10 ^ A.F1

        self.assertIsInstance(or_result,  A,    msg="OR is A")
        self.assertIsInstance(and_result, A,    msg="AND is A")
        self.assertIsInstance(xor_result, A,    msg="XOR is A")
        self.assertEqual(0b111, or_result,      msg="int | A equal")
        self.assertEqual(1,     and_result,     msg="int & A equal")
        self.assertEqual(0b11,  xor_result,     msg="int ^ A equal")

    def test_intflagex_not_operator_default(self):
        from enum import IntFlag
        class A(IntFlagEx):
            F1 = autoex()
            F2 = autoex()
            F3 = autoex()
            F4 = autoex()
        class B(A):
            F5 = autoex()
            F6 = autoex()

        class X(IntFlag):
            F1 = auto()
            F2 = auto()
            F3 = auto()
            F4 = auto()
        class Y(IntFlag):
            F1 = auto()
            F2 = auto()
            F3 = auto()
            F4 = auto()
            F5 = auto()
            F6 = auto()

        std_result = ~X.F1
        not_result = ~A.F1
        expected = ~1

        if _SYS_VERSION_MAJOR_MINOR_ >= (3, 11):
            expected &= 0b1111

        self.assertIsInstance(not_result, A,     msg="NOT is A")
        self.assertEqual(expected, not_result,   msg="~ equal")
        self.assertEqual(std_result, not_result, msg="~IntFlagEx == ~IntFlag")

        std_result = ~Y.F5
        not_result = ~B.F5
        expected = ~(1 << 4)

        if _SYS_VERSION_MAJOR_MINOR_ >= (3, 11):
            expected &= 0b111111

        self.assertIsInstance(not_result, B,     msg="NOT is B")
        self.assertEqual(expected, not_result,   msg="~ equal")
        self.assertEqual(std_result, not_result, msg="~IntFlagEx == ~IntFlag")

    def test_intflagex_operators_abstract(self):
        class A(ABC, IntFlagEx):
            F1 = autoex()
            F2 = autoex()

            @abstractmethod
            def foo(self):
                pass

        class B(A):
            F3 = autoex()
            F4 = autoex()

            def foo(self):
                return 'foo'

        # Just test so see it doesnt raise
        or_result  = B.F3 | 0b11
        and_result = B.F1 & 0b11
        xor_result = B.F1 ^ 0b10
        a_lshift_result = A.F1 << 3
        a_rshift_result = A.F2 >> 1
        b_lshift_result = B.F1 << 3
        b_rshift_result = B.F4 >> 3

        self.assertIsInstance(or_result,  B,            msg="OR is B")
        self.assertIsInstance(and_result, B,            msg="AND is B")
        self.assertIsInstance(xor_result, B,            msg="XOR is B")
        self.assertIsInstance(a_lshift_result, int,     msg="A << is int")
        self.assertIsInstance(a_rshift_result, int,     msg="A >> is int")
        self.assertNotIsInstance(a_lshift_result, A,    msg="A << is not A")
        self.assertNotIsInstance(a_rshift_result, A,    msg="A >> is not A")
        self.assertIsInstance(b_lshift_result, int,     msg="B << is int")
        self.assertIsInstance(b_rshift_result, int,     msg="B >> is int")
        self.assertNotIsInstance(b_lshift_result, B,    msg="B << is not B")
        self.assertNotIsInstance(b_rshift_result, B,    msg="B >> is not B")
        self.assertEqual(0b111,  or_result,             msg="B | A equal")
        self.assertEqual(1,      and_result,            msg="B & A equal")
        self.assertEqual(0b11,   xor_result,            msg="B ^ A equal")
        self.assertEqual(0b1000, a_lshift_result,       msg="A << equal")
        self.assertEqual(0b1,    a_rshift_result,       msg="A >> equal")
        self.assertEqual(0b1000, b_lshift_result,       msg="B << equal")
        self.assertEqual(0b1,    b_rshift_result,       msg="B >> equal")

        or_result  = B.F3 | A.F1
        and_result = B.F1 & A.F1
        xor_result = B.F1 ^ A.F2
        a_lshift_result = A.F1 << A.F2
        a_rshift_result = A.F2 >> A.F1
        b_lshift_result = B.F1 << A.F2
        b_rshift_result = B.F4 >> A.F2

        self.assertIsInstance(or_result,  B,            msg="OR is B")
        self.assertIsInstance(and_result, B,            msg="AND is B")
        self.assertIsInstance(xor_result, B,            msg="XOR is B")
        self.assertIsInstance(b_lshift_result, int,     msg="B << is int")
        self.assertIsInstance(b_rshift_result, int,     msg="B >> is int")
        self.assertNotIsInstance(b_lshift_result, B,    msg="B << is not B")
        self.assertNotIsInstance(b_rshift_result, B,    msg="B >> is not B")
        self.assertEqual(0b101,  or_result,             msg="B | A equal")
        self.assertEqual(1,      and_result,            msg="B & A equal")
        self.assertEqual(0b11,   xor_result,            msg="B ^ A equal")
        self.assertEqual(0b100,  a_lshift_result,       msg="A << equal")
        self.assertEqual(0b1,    a_rshift_result,       msg="A >> equal")
        self.assertEqual(0b100,  b_lshift_result,       msg="B << equal")
        self.assertEqual(0b10,   b_rshift_result,       msg="B >> equal")

        # Test to ensure it raises
        _assert_invalidabstract(self, A, lambda: A.F1 | B.F3,  'foo')
        _assert_invalidabstract(self, A, lambda: A.F1 & B.F1,  'foo')
        _assert_invalidabstract(self, A, lambda: A.F1 ^ B.F2,  'foo')
        _assert_invalidabstract(self, A, lambda: ~A.F1,        'foo')

    def test_intflagex_lshift_operator(self):
        class A(IntFlagEx):
            F1 = autoex()
            F2 = autoex()
            F3 = autoex()
            F4 = autoex()
        class B(A):
            F5 = autoex()
            F6 = autoex()

        shift_result = A.F1 << 3
        self.assertIsInstance(shift_result, int,    msg="A << is int")
        self.assertNotIsInstance(shift_result, A,   msg="A << is not A")
        self.assertEqual(0b1000, shift_result,      msg="A << equal")

        shift_result = B.F1 << 4
        self.assertIsInstance(shift_result, int,    msg="B << is int")
        self.assertNotIsInstance(shift_result, B,   msg="B << is not B")
        self.assertEqual(0b10000, shift_result,     msg="B << equal")

    def test_intflagex_rshift_operator(self):
        class A(IntFlagEx):
            F1 = autoex()
            F2 = autoex()
            F3 = autoex()
            F4 = autoex()
        class B(A):
            F5 = autoex()
            F6 = autoex()

        shift_result = A.F4 >> 3
        self.assertIsInstance(shift_result, int,    msg="A << is int")
        self.assertNotIsInstance(shift_result, A,   msg="A << is not A")
        self.assertEqual(0b1, shift_result,         msg="A >> equal")

        shift_result = B.F6 >> 2
        self.assertIsInstance(shift_result, int,    msg="B << is int")
        self.assertNotIsInstance(shift_result, B,   msg="B << is not B")
        self.assertEqual(0b1000, shift_result,      msg="B >> equal")

    if _SYS_VERSION_MAJOR_MINOR_ >= (3, 11):
        def test_intflagex_not_operator_strict(self):
            class A(IntFlagEx, boundary=STRICT):
                F1 = autoex()
                F2 = autoex()
                F3 = autoex()
                F4 = autoex()
            class B(A):
                F5 = autoex()
                F6 = autoex()

            from enum import IntFlag, auto, STRICT as StdSTRICT
            class X(IntFlag, boundary=StdSTRICT):
                F1 = auto()
                F2 = auto()
                F3 = auto()
                F4 = auto()

            std_result = ~X.F1
            not_result = ~A.F1

            self.assertIsInstance(not_result, A,     msg="NOT is A")
            self.assertEqual(0b1110,    not_result,  msg="NOT equal")
            self.assertEqual(std_result, not_result, msg="~IntFlagEx == ~IntFlag")

            not_result = ~B.F5
            self.assertIsInstance(not_result, B,     msg="NOT is B")
            self.assertEqual(0b101111,  not_result,  msg="NOT equal")

            with self.assertRaises(ValueError) as ec:
                not_result = ~(A(B.F5 | 0b10_000_000))
            self.assertEqual("<flag 'B'> invalid value 144\n    given 0b0 10010000\n  allowed 0b0 00111111",
                            ec.exception.args[0],
                            msg="STRICT NOT error message"
            )


        def test_intflagex_not_operator_conform(self):
            class A(IntFlagEx, boundary=CONFORM):
                F1 = autoex()
                F2 = autoex()
                F3 = autoex()
                F4 = autoex()
            class B(A):
                F5 = autoex()
                F6 = autoex()

            from enum import IntFlag, auto, CONFORM as StdCONFORM
            class X(IntFlag, boundary=StdCONFORM):
                F1 = auto()
                F2 = auto()
                F3 = auto()
                F4 = auto()

            std_result = ~X.F1
            not_result = ~A.F1

            self.assertIsInstance(not_result, A,     msg="NOT is A")
            self.assertEqual(0b1110,    not_result,  msg="NOT equal")
            self.assertEqual(std_result, not_result, msg="~IntFlagEx == ~IntFlag")

            not_result = ~B.F5
            self.assertIsInstance(not_result, B,     msg="NOT is B")
            self.assertEqual(0b101111,  not_result,  msg="NOT equal")

            std_result = ~(X(B.F5 | 0b10_000_000))
            not_result = ~(A(B.F5 | 0b10_000_000))
            expected_result = ~0b10_010_000 & 0b1111
            self.assertIsInstance(not_result, A,            msg="NOT is A")
            self.assertEqual(expected_result, not_result,   msg="NOT equal")
            self.assertEqual(std_result, not_result,        msg="~IntFlagEx == ~IntFlag")

        def test_intflagex_not_operator_eject(self):
            class A(IntFlagEx, boundary=EJECT):
                F1 = autoex()
                F2 = autoex()
                F3 = autoex()
                F4 = autoex()
            class B(A):
                F5 = autoex()
                F6 = autoex()

            from enum import IntFlag, auto, EJECT as StdEJECT
            class X(IntFlag, boundary=StdEJECT):
                F1 = auto()
                F2 = auto()
                F3 = auto()
                F4 = auto()

            std_result = ~X.F1
            not_result = ~A.F1

            self.assertIsInstance(not_result, A,     msg="NOT is A")
            self.assertEqual(0b1110,    not_result,  msg="NOT equal")
            self.assertEqual(std_result, not_result, msg="~IntFlagEx == ~IntFlag")

            not_result = ~B.F5
            self.assertIsInstance(not_result, B,     msg="NOT is B")
            self.assertEqual(0b101111,  not_result,  msg="NOT equal")

            std_result = ~(X(B.F5 | 0b10_000_000))
            not_result = ~(A(B.F5 | 0b10_000_000))
            expected_result = ~0b10_010_000
            self.assertIsInstance(not_result, int,          msg="NOT is int")
            self.assertNotIsInstance(not_result, A,         msg="NOT is not A")
            self.assertEqual(expected_result, not_result,   msg="NOT equal")
            self.assertEqual(std_result, not_result,        msg="~IntFlagEx == ~IntFlag")

        def test_intflagex_not_operator_keep(self):
            class A(IntFlagEx, boundary=KEEP):
                F1 = autoex()
                F2 = autoex()
                F3 = autoex()
                F4 = autoex()
            class B(A):
                F5 = autoex()
                F6 = autoex()

            from enum import IntFlag, auto, KEEP as StdKEEP
            class X(IntFlag, boundary=StdKEEP):
                F1 = auto()
                F2 = auto()
                F3 = auto()
                F4 = auto()

            std_result = ~X.F1
            not_result = ~A.F1

            self.assertIsInstance(not_result, A,     msg="NOT is A")
            self.assertEqual(0b1110,    not_result,  msg="NOT equal")
            self.assertEqual(std_result, not_result, msg="~IntFlagEx == ~IntFlag")

            not_result = ~B.F5
            self.assertIsInstance(not_result, B,     msg="NOT is B")
            self.assertEqual(0b101111,  not_result,  msg="NOT equal")

            # std_result = ~(X(0b10_000_000))
            # not_result = ~(A(0b10_000_000))
            # expected_result = ~0b10_000_000
            # self.assertIsInstance(not_result, A,            msg="NOT is A")
            # self.assertEqual(expected_result, not_result,   msg="NOT equal")
            # self.assertEqual(std_result, not_result,        msg="~IntFlagEx == ~IntFlag")

            std_result = ~(X(B.F5 | 0b10_000_000))
            not_result = ~(A(B.F5 | 0b10_000_000))
            expected_result = ~0b10_010_000 & 0b11_111_111
            self.assertIsInstance(not_result, A,            msg="NOT is A")
            self.assertEqual(expected_result, not_result,   msg="NOT equal")
            self.assertEqual(std_result, not_result,        msg="~IntFlagEx == ~IntFlag")

        def test_flagexboundary_strict(self):
            class A(IntFlagEx, boundary=STRICT):
                F1 = autoex()

            with self.assertRaises(ValueError) as ec:
                v = A(2)
            self.assertEqual("<flag 'A'> invalid value 2\n    given 0b0 10\n  allowed 0b0 01", 
                            ec.exception.args[0],  msg="FlagExBoundary STRICT error message")

        def test_flagexboundary_conform(self):
            class A(IntFlagEx, boundary=CONFORM):
                F1 = autoex()

            v = A(3)
            self.assertIsInstance(v, A,             msg="FlagExBoundary CONFORM isinstance A")
            self.assertEqual(A.F1, v,               msg="FlagExBoundary CONFORM equal")

        def test_flagexboundary_eject(self):
            class A(IntFlagEx, boundary=EJECT):
                F1 = autoex()

            v = A(2)
            self.assertIsInstance(v, int,           msg="FlagExBoundary CONFORM isinstance int")
            self.assertNotIsInstance(v, FlagEx,     msg="FlagExBoundary CONFORM not isinstance FlagEx")
            self.assertEqual(2, v,                  msg="FlagExBoundary CONFORM equal")

        def test_flagexboundary_keep(self):
            class A(IntFlagEx, boundary=KEEP):
                F1 = autoex()

            v = A(2)
            self.assertIsInstance(v, A,             msg="FlagExBoundary CONFORM isinstance A")
            self.assertEqual(2, v.value,            msg="FlagExBoundary CONFORM equal")

def _assert_invalidabstract(case:unittest.TestCase, cls:EnumEx, initvalue:Union[object,Callable], *args):
    with case.assertRaises(TypeError) as ec:
        if isinstance(initvalue, Callable):
            v = initvalue()
        else:
            v = cls(initvalue)
    count = len(args)
    case.assertEqual(len(cls.__abstractmethods__), count, msg="Assert __abstractmethods__")
    case.assertEqual(count + 1, len(ec.exception.args), msg="Exception args length of abstract methods")
    case.assertEqual(f"Can't instantiate abstract class {cls.__name__} with abstract method{'' if count == 1 else 's'}", ec.exception.args[0], msg="_enforce_abstract error message")
    method_args = ec.exception.args[1:]
    for arg in args:
        case.assertIn(arg, method_args, msg="Abstract method in exception args.")

if __name__ == "__main__":
    unittest.main()