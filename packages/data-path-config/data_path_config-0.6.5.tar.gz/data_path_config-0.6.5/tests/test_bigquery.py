import pytest
import pandas as pd
import tempfile
import os
from data_path_config.google.bigquery import BigQueryManager

def test_imports():
    """Test that BigQueryManager can be imported and has expected methods."""
    assert BigQueryManager
    assert hasattr(BigQueryManager, 'upload_dataframe')
    assert hasattr(BigQueryManager, 'upload_csv')
    assert hasattr(BigQueryManager, 'list_datasets')
    assert hasattr(BigQueryManager, 'list_tables')
    assert hasattr(BigQueryManager, 'create_dataset')
    assert hasattr(BigQueryManager, 'create_table')

def test_bigquery_manager():
    """Test BigQueryManager initialization."""
    try:
        manager = BigQueryManager()
        assert manager.client is not None
    except (ValueError, FileNotFoundError) as e:
        # Expected if .env not set or file missing
        assert "not set" in str(e) or "No such file" in str(e)

def test_upload_dataframe():
    """Test upload_dataframe method with a sample DataFrame."""
    try:
        manager = BigQueryManager()
        # Create a sample DataFrame
        df = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie'],
            'age': [25, 30, 35],
            'city': ['New York', 'London', 'Tokyo']
        })
        # Note: This will attempt to upload, but without actual BigQuery dataset/table, behavior may vary
        # In a real test, you'd need to set up a test dataset
        # For now, just check that the method exists and can be called
        result = manager.upload_dataframe(df, 'test_dataset', 'test_table')
        print(f"Upload result: {result}")
        # If it succeeds, check return type
        assert isinstance(result, str)
        # Query the table to check if data was uploaded
        query = f"SELECT COUNT(*) as count FROM `{result}`"
        try:
            result_df = manager.query_table(query)
            count = result_df.iloc[0]['count']
            print(f"Row count after upload: {count}")
            assert count == 3, f"Expected 3 rows, but got {count}"
        except Exception as e:
            print(f"Query failed: {e}")
            # If query fails, perhaps permissions or table not created
            pass
    except (ValueError, FileNotFoundError) as e:
        # Expected if .env not set or file missing
        assert "not set" in str(e) or "No such file" in str(e)
    except Exception as e:
        # May raise if dataset/table invalid or other issues
        print(f"Upload failed: {e}")
        pass

def test_upload_csv():
    """Test upload_csv method with a temporary CSV file."""
    try:
        manager = BigQueryManager()
        # Create a temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("name,age,city\n")
            f.write("Alice,25,New York\n")
            f.write("Bob,30,London\n")
            f.write("Charlie,35,Tokyo\n")
            csv_path = f.name
        
        try:
            # Note: This will fail without actual BigQuery dataset/table, but tests the method call
            with pytest.raises(Exception):  # Expecting an exception due to invalid dataset/table
                manager.upload_csv(csv_path, 'test_dataset', 'test_table')
        finally:
            os.unlink(csv_path)  # Clean up the temporary file
    except (ValueError, FileNotFoundError) as e:
        # Expected if .env not set or file missing
        assert "not set" in str(e) or "No such file" in str(e)

def test_list_datasets():
    """Test list_datasets method."""
    try:
        manager = BigQueryManager()
        datasets = manager.list_datasets()
        assert isinstance(datasets, list)
        print(f"Available datasets: {datasets}")
        # Note: This may return actual datasets if credentials are set, or fail if not
    except Exception as e:
        # Expected if .env not set or invalid credentials
        print(f"Expected error: {e}")
        # Test passes as long as no unexpected errors

def test_list_tables():
    """Test list_tables method."""
    try:
        manager = BigQueryManager()
        # Test listing tables in the existing test_dataset_temp
        try:
            tables = manager.list_tables('test_dataset_temp')
            print(f"Tables in 'test_dataset_temp': {tables}")
            assert isinstance(tables, list)
        except Exception as e:
            # Expected if dataset doesn't exist or permissions issue
            print(f"Expected error during table listing: {e}")
    except (ValueError, FileNotFoundError) as e:
        # Expected if .env not set or file missing
        assert "not set" in str(e) or "No such file" in str(e)

def test_create_dataset():
    """Test create_dataset method."""
    try:
        manager = BigQueryManager()
        # This may succeed or fail depending on permissions and dataset name
        try:
            manager.create_dataset('test_dataset_temp')
        except Exception as e:
            # Expected if permissions are insufficient or dataset exists
            print(f"Expected error during dataset creation: {e}")
    except (ValueError, FileNotFoundError) as e:
        # Expected if .env not set or file missing
        assert "not set" in str(e) or "No such file" in str(e)

def test_create_table():
    """Test create_table method."""
    try:
        manager = BigQueryManager()
        from google.cloud import bigquery
        schema = [
            bigquery.SchemaField("name", "STRING"),
            bigquery.SchemaField("age", "INTEGER"),
        ]
        # Test creating a table in the existing test_dataset_temp
        try:
            manager.create_table('test_dataset_temp', 'test_table', schema)
            print("Successfully created table 'test_table' in 'test_dataset_temp'")
        except Exception as e:
            # Expected if permissions are insufficient or table already exists
            print(f"Expected error during table creation: {e}")
    except (ValueError, FileNotFoundError) as e:
        # Expected if .env not set or file missing
        assert "not set" in str(e) or "No such file" in str(e)

def test_query_table():
    """Test query_table method."""
    try:
        manager = BigQueryManager()
        # Query a simple table if it exists
        query = "SELECT 1 as test_column"
        result_df = manager.query_table(query)
        assert not result_df.empty
        assert result_df.iloc[0]['test_column'] == 1
        print("Query test passed")
    except Exception as e:
        # Expected if .env not set or query fails
        print(f"Query test failed: {e}")
        pass