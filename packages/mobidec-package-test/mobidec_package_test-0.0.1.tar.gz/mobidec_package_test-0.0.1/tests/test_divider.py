import pytest
from mobidec_package_test.divider import CantDivideByZeroError, divide


def test_devide_by_zero():
    with pytest.raises(CantDivideByZeroError):
        divide(1, 0)


def test_devide_by_one():
    assert divide(1, 1) == 1
