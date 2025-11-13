"""
Comprehensive tests for bioconverter with actual data validation
Tests both conversion correctness and compressed file support
"""

import pytest
import pandas as pd
import gzip
import tempfile
import os
from pathlib import Path
from bioconverter.convertor import (
    convert_single_file,
    read_data,
    match_columns,
    create_genetic_column_patterns
)
from bioconverter.interactive_converter import auto_suggest_mapping


# Get test data directory
TEST_DIR = Path(__file__).parent


class TestCompressionSupport:
    """Test conversion of compressed files"""
    
    def test_gzip_gwas_file(self):
        """Test conversion of gzip compressed GWAS file"""
        input_file = TEST_DIR / "GCST90043616_buildGRCh37.tsv.gz"
        
        # Convert the file
        result = convert_single_file(str(input_file), verbose=False)
        
        # Validate result structure
        assert result is not None
        assert len(result) > 0, "Result should not be empty"
        
        # Check expected columns are present
        expected_cols = {'chr', 'rsid', 'a1', 'a2', 'n', 'beta', 'se', 'pval'}
        assert expected_cols.issubset(set(result.columns)), f"Missing columns: {expected_cols - set(result.columns)}"
        
        # Validate data types
        assert pd.api.types.is_integer_dtype(result['chr']), "chr should be integer"
        assert pd.api.types.is_numeric_dtype(result['beta']), "beta should be numeric"
        assert pd.api.types.is_numeric_dtype(result['pval']), "pval should be numeric"
        
        # Validate data ranges
        assert result['pval'].between(0, 1).all(), "p-values should be between 0 and 1"
        assert result['chr'].min() >= 1, "chr should be >= 1"
        assert result['chr'].max() <= 22, "chr should be <= 22 (or X/Y)"
        
        print(f"✓ Successfully converted {len(result)} rows from gzipped file")
        print(f"✓ Columns: {list(result.columns)}")
    
    def test_vcf_gz_file(self):
        """Test conversion of VCF.gz file"""
        input_file = TEST_DIR / "finn-b-F5_ALLANXIOUS.vcf.gz"
        
        # Convert the file
        result = convert_single_file(str(input_file), verbose=False)
        
        # Validate result
        assert result is not None
        assert len(result) > 0
        
        # VCF should have standard columns
        assert 'chr' in result.columns or 'CHROM' in result.columns
        assert 'pos' in result.columns or 'POS' in result.columns
        
        print(f"✓ Successfully converted VCF.gz with {len(result)} variants")
        print(f"✓ Columns: {list(result.columns)}")
    
    def test_multiple_compression_formats(self):
        """Test that we can handle different compression formats"""
        # Create test data
        test_data = pd.DataFrame({
            'CHR': [1, 1, 2],
            'POS': [1000, 2000, 3000],
            'SNP': ['rs1', 'rs2', 'rs3'],
            'A1': ['A', 'C', 'G'],
            'A2': ['G', 'T', 'A'],
            'BETA': [0.1, -0.2, 0.3],
            'SE': [0.05, 0.06, 0.04],
            'P': [0.01, 0.001, 0.05]
        })
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Test gzip
            gz_file = Path(tmpdir) / "test.tsv.gz"
            test_data.to_csv(gz_file, sep='\t', index=False, compression='gzip')
            
            result_gz = convert_single_file(str(gz_file), verbose=False)
            assert len(result_gz) == 3
            assert 'chr' in result_gz.columns
            assert 'pval' in result_gz.columns
            
            # Verify actual values are preserved
            assert result_gz['chr'].tolist() == [1, 1, 2]
            assert result_gz['rsid'].tolist() == ['rs1', 'rs2', 'rs3']
            
            print("✓ Gzip compression test passed")
            
            # Test bz2
            bz2_file = Path(tmpdir) / "test.tsv.bz2"
            test_data.to_csv(bz2_file, sep='\t', index=False, compression='bz2')
            
            result_bz2 = convert_single_file(str(bz2_file), verbose=False)
            assert len(result_bz2) == 3
            
            print("✓ Bz2 compression test passed")


class TestDataIntegrity:
    """Test that data values are correctly preserved during conversion"""
    
    def test_value_preservation(self):
        """Test that actual data values are preserved during conversion"""
        # Create test data with known values
        test_data = pd.DataFrame({
            'CHR': [1, 2, 3],
            'POS': [12345, 67890, 111213],
            'SNP': ['rs100', 'rs200', 'rs300'],
            'A1': ['A', 'C', 'G'],
            'A2': ['G', 'T', 'A'],
            'BETA': [0.123, -0.456, 0.789],
            'SE': [0.011, 0.022, 0.033],
            'P': [1e-5, 1e-10, 0.05]
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tsv', delete=False) as f:
            test_data.to_csv(f, sep='\t', index=False)
            temp_file = f.name
        
        try:
            result = convert_single_file(temp_file, verbose=False)
            
            # Check exact values are preserved
            assert result['chr'].tolist() == [1, 2, 3]
            assert result['pos'].tolist() == [12345, 67890, 111213]
            assert result['rsid'].tolist() == ['rs100', 'rs200', 'rs300']
            assert result['a1'].tolist() == ['A', 'C', 'G']
            assert result['a2'].tolist() == ['G', 'T', 'A']
            
            # Check numeric values with tolerance
            assert abs(result['beta'].iloc[0] - 0.123) < 1e-6
            assert abs(result['beta'].iloc[1] - (-0.456)) < 1e-6
            assert abs(result['pval'].iloc[0] - 1e-5) < 1e-15
            
            print("✓ All values correctly preserved during conversion")
        finally:
            os.unlink(temp_file)
    
    def test_column_mapping_accuracy(self):
        """Test that column mapping is accurate"""
        # Test with various column name formats
        test_cases = [
            ('CHR', 'chr'),
            ('chromosome', 'chr'),
            ('CHROM', 'chr'),
            ('POS', 'pos'),
            ('position', 'pos'),
            ('BP', 'pos'),
            ('SNP', 'rsid'),
            ('rsid', 'rsid'),
            ('variant_id', 'rsid'),
            ('P', 'pval'),
            ('p_value', 'pval'),
            ('PVALUE', 'pval'),
            ('BETA', 'beta'),
            ('effect', 'beta'),
            ('SE', 'se'),
            ('standard_error', 'se')
        ]
        
        patterns = create_genetic_column_patterns()
        
        for original, expected in test_cases:
            matched = match_columns([original], patterns)
            assert matched[original] == expected, f"Failed to map {original} -> {expected}, got {matched[original]}"
        
        print(f"✓ All {len(test_cases)} column mappings correct")
    
    def test_real_gwas_data_quality(self):
        """Test conversion quality on real GWAS data"""
        input_file = TEST_DIR / "GCST90043616_buildGRCh37.tsv.gz"
        
        # Read original data
        original = pd.read_csv(input_file, sep='\t', nrows=100)
        
        # Convert
        result = convert_single_file(str(input_file), verbose=False)
        result_sample = result.head(100)
        
        # Verify chromosome values match
        assert (original['chromosome'] == result_sample['chr']).all(), "Chromosome values don't match"
        
        # Verify beta values match
        assert (abs(original['beta'] - result_sample['beta']) < 1e-6).all(), "Beta values don't match"
        
        # Verify p-values match
        assert (abs(original['p_value'] - result_sample['pval']) < 1e-10).all(), "P-values don't match"
        
        # Verify sample size matches
        assert (original['N'] == result_sample['n']).all(), "Sample size values don't match"
        
        print("✓ Real GWAS data conversion verified - all values match")


class TestAutoSuggestMapping:
    """Test automatic column mapping suggestions"""
    
    def test_auto_suggest_on_gwas(self):
        """Test auto-suggest mapping on GWAS file"""
        input_file = TEST_DIR / "GCST90043616_buildGRCh37.tsv.gz"
        
        # Read sample
        df = pd.read_csv(input_file, sep='\t', nrows=100)
        
        # Get suggestions
        mapping = auto_suggest_mapping(df)
        
        # Verify key mappings are suggested
        assert 'chromosome' in mapping
        assert mapping['chromosome'] == 'chr'
        assert 'p_value' in mapping
        assert mapping['p_value'] == 'pval'
        assert 'beta' in mapping
        assert mapping['beta'] == 'beta'
        
        print(f"✓ Auto-suggest found {len(mapping)} mappings")
        print(f"✓ Mappings: {mapping}")


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_mapping(self):
        """Test behavior with no matching columns"""
        test_data = pd.DataFrame({
            'random_col1': [1, 2, 3],
            'random_col2': ['a', 'b', 'c']
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tsv', delete=False) as f:
            test_data.to_csv(f, sep='\t', index=False)
            temp_file = f.name
        
        try:
            result = convert_single_file(temp_file, verbose=False)
            # Should return empty dataframe or only keep unmatched if specified
            assert isinstance(result, pd.DataFrame)
            print("✓ Handled file with no matching columns")
        finally:
            os.unlink(temp_file)
    
    def test_missing_values(self):
        """Test handling of missing values"""
        test_data = pd.DataFrame({
            'CHR': [1, 2, None],
            'POS': [1000, None, 3000],
            'BETA': [0.1, None, 0.3],
            'P': [0.01, 0.001, None]
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tsv', delete=False) as f:
            test_data.to_csv(f, sep='\t', index=False)
            temp_file = f.name
        
        try:
            result = convert_single_file(temp_file, verbose=False)
            assert len(result) == 3
            # Check that NaN values are preserved
            assert result['chr'].isna().sum() == 1
            print("✓ Missing values handled correctly")
        finally:
            os.unlink(temp_file)


def test_full_pipeline():
    """Integration test of full conversion pipeline"""
    print("\n" + "="*60)
    print("RUNNING FULL PIPELINE TEST")
    print("="*60)
    
    input_file = TEST_DIR / "GCST90043616_buildGRCh37.tsv.gz"
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "output.tsv.gz"
        
        # Convert
        result = convert_single_file(str(input_file), verbose=True)
        
        # Save
        result.to_csv(output_file, sep='\t', index=False, compression='gzip')
        
        # Read back
        reloaded = pd.read_csv(output_file, sep='\t')
        
        # Verify
        assert len(reloaded) == len(result)
        assert list(reloaded.columns) == list(result.columns)
        
        print(f"\n✓ Full pipeline test passed")
        print(f"✓ Input: {len(result)} rows")
        print(f"✓ Output saved and reloaded successfully")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
