from typing import Dict, Set
import pandas as pd
import pytest
from completejourney_py import get_data

def test_get_data_all_datasets() -> None:
    """Test loading all datasets when no parameter is provided."""
    data: Dict[str, pd.DataFrame] = get_data()

    assert len(data) == 8
    expected_keys: Set[str] = {'campaign_descriptions', 'coupons', 'promotions',
                               'campaigns', 'demographics', 'transactions',
                               'coupon_redemptions', 'products'}
    assert set(data.keys()) == expected_keys
    for _, item in data.items():
        assert item.shape[0] > 0 and item.shape[1] > 0


def test_get_data_single_dataset_string() -> None:
    """Test loading a single dataset by string name."""
    data: Dict[str, pd.DataFrame] = get_data("transactions")
    
    assert len(data) == 1
    assert "transactions" in data
    assert isinstance(data["transactions"], pd.DataFrame)
    assert data["transactions"].shape[0] > 0


def test_get_data_multiple_datasets_list() -> None:
    """Test loading multiple datasets using a list."""
    datasets = ["transactions", "demographics"]
    data: Dict[str, pd.DataFrame] = get_data(datasets)
    
    assert len(data) == 2
    assert set(data.keys()) == set(datasets)
    for df in data.values():
        assert isinstance(df, pd.DataFrame)
        assert df.shape[0] > 0


def test_get_data_multiple_datasets_tuple() -> None:
    """Test loading multiple datasets using a tuple."""
    datasets = ("products", "coupons")
    data: Dict[str, pd.DataFrame] = get_data(datasets)
    
    assert len(data) == 2
    assert set(data.keys()) == set(datasets)
    for df in data.values():
        assert isinstance(df, pd.DataFrame)
        assert df.shape[0] > 0


def test_get_data_empty_list() -> None:
    """Test that empty list returns empty dictionary."""
    data: Dict[str, pd.DataFrame] = get_data([])
    
    assert len(data) == 0
    assert data == {}


def test_get_data_invalid_dataset_name() -> None:
    """Test that invalid dataset name raises appropriate error."""
    with pytest.raises((FileNotFoundError, KeyError)):
        get_data("nonexistent_dataset")


def test_get_data_mixed_valid_invalid() -> None:
    """Test behavior with mix of valid and invalid dataset names."""
    with pytest.raises((FileNotFoundError, KeyError)):
        get_data(["transactions", "nonexistent_dataset"])


def test_get_data_invalid_parameter_type() -> None:
    """Test that invalid parameter type raises appropriate error."""
    with pytest.raises((TypeError, AttributeError)):
        get_data(123)  # type: ignore


def test_get_data_dataframe_properties() -> None:
    """Test that returned DataFrames have expected properties."""
    data: Dict[str, pd.DataFrame] = get_data(["transactions"])
    
    df = data["transactions"]
    # Verify it's actually a pandas DataFrame
    assert isinstance(df, pd.DataFrame)
    # Verify it has columns
    assert len(df.columns) > 0
    # Verify it has an index
    assert df.index is not None
    # Verify data types are reasonable (not all object)
    assert not all(df.dtypes == 'object')
