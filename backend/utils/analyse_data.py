import pandas as pd
import numpy as np
from collections import defaultdict
from typing import Dict, List, Set

class FashionDataCleaner:
    def __init__(self):
        self.data = None
        self.error_rows = []
        
    def load_and_clean_data(self, csv_path: str) -> pd.DataFrame:
        """Load and clean the fashion dataset, handling potential errors"""
        print("Loading data and checking for inconsistencies...")
        
        with open(csv_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            
        # Get header
        header = lines[0].strip().split(',')
        expected_columns = len(header)
        

        clean_lines = [lines[0]]  # Start with header
        for i, line in enumerate(lines[1:], 1):
            fields = line.strip().split(',')
            if len(fields) != expected_columns:
                self.error_rows.append({
                    'line_number': i + 1,
                    'field_count': len(fields),
                    'content': line.strip()
                })
                # Try to fix the line if possible
                fixed_line = self._attempt_fix_line(line, expected_columns)
                if fixed_line:
                    clean_lines.append(fixed_line)
            else:
                clean_lines.append(line)
        
        # Create a temporary clean CSV
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as temp_file:
            temp_file.writelines(clean_lines)
            temp_path = temp_file.name
            
        # Read the clean CSV
        try:
            self.data = pd.read_csv(temp_path)
            print(f"Successfully loaded {len(self.data)} rows of data")
            
            # Remove temporary file
            import os
            os.unlink(temp_path)
            
            # Print error summary
            if self.error_rows:
                print(f"\nFound {len(self.error_rows)} problematic rows:")
                for err in self.error_rows[:5]:  # Show first 5 errors
                    print(f"Line {err['line_number']}: Expected {expected_columns} fields, found {err['field_count']}")
                if len(self.error_rows) > 5:
                    print(f"... and {len(self.error_rows) - 5} more issues")
                    
            return self.data
            
        except Exception as e:
            print(f"Error reading cleaned data: {str(e)}")
            raise
            
    def _attempt_fix_line(self, line: str, expected_columns: int) -> str:
        """Attempt to fix problematic lines"""
        # Remove any quotes and split
        fields = line.replace('"', '').strip().split(',')
        
        if len(fields) > expected_columns:
            while len(fields) > expected_columns:
                for i in range(len(fields) - 1):
                    if i < len(fields) - 1:
                        combined = fields[i] + ' ' + fields[i + 1]
                        fields = fields[:i] + [combined] + fields[i+2:]
                        if len(fields) == expected_columns:
                            break
                            
        elif len(fields) < expected_columns:

            fields.extend([''] * (expected_columns - len(fields)))
            
        return ','.join(fields) + '\n'

class FashionCategoryAnalyzer:
    def __init__(self):
        self.data = None
        self.category_hierarchy = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))
        self.color_palette = set()
        self.seasons = set()
        self.usages = set()
        self.years = set()
        
    def load_data(self, csv_path: str) -> None:
        """Load and analyze the fashion dataset"""
        print("\nLoading and analyzing fashion data...")
        
        # First clean the data
        cleaner = FashionDataCleaner()
        self.data = cleaner.load_and_clean_data(csv_path)
        
        # Now analyze the cleaned data
        self._analyze_categories()
        
    def _analyze_categories(self) -> None:
        """Analyze and organize all categories in the dataset"""
        print("\nAnalyzing categories...")
        
        # First, check for any missing or invalid values
        for column in self.data.columns:
            missing = self.data[column].isnull().sum()
            if missing > 0:
                print(f"Found {missing} missing values in {column}")
                
        # Analyze main category hierarchy
        for _, row in self.data.iterrows():
            try:
                self.category_hierarchy[row['gender']][row['masterCategory']][row['subCategory']].add(row['articleType'])
                if pd.notna(row['baseColour']):
                    self.color_palette.add(row['baseColour'])
                if pd.notna(row['season']):
                    self.seasons.add(row['season'])
                if pd.notna(row['usage']):
                    self.usages.add(row['usage'])
                if pd.notna(row['year']):
                    self.years.add(row['year'])
            except Exception as e:
                print(f"Error processing row: {row}")
                print(f"Error: {str(e)}")
                
    def print_detailed_summary(self) -> None:
        """Print a detailed summary of the dataset"""
        print("\n=== Detailed Fashion Dataset Analysis ===")
        
        print("\nDataset Shape:", self.data.shape)
        print("\nColumns:", list(self.data.columns))
        
        print("\nMissing Values Summary:")
        missing = self.data.isnull().sum()
        for col, count in missing.items():
            if count > 0:
                print(f"- {col}: {count} missing values")
                
        print("\nValue Counts for Key Categories:")
        for col in ['gender', 'masterCategory', 'subCategory', 'usage', 'season']:
            print(f"\n{col} distribution:")
            print(self.data[col].value_counts().head())

# Example usage
def main():
    analyzer = FashionCategoryAnalyzer()
    
    try:

        analyzer.load_data('/Users/spurge/Desktop/recommendation/styles.csv')
        
        # Print detailed summary
        analyzer.print_detailed_summary()
        
    except Exception as e:
        print(f"Error in main: {str(e)}")
        raise

if __name__ == "__main__":
    main()