"""Excel exporter with organization by platform and organism."""

import pandas as pd
from typing import List, Dict
from pathlib import Path
from utils import is_human_organism
from config import COLUMN_ORDER


class ExcelExporter:
    """Exports spatial transcriptomics data to organized Excel files."""
    
    def __init__(self, output_file: str = "st_catalog.xlsx"):
        """
        Initialize exporter.
        
        Args:
            output_file: Output Excel file path
        """
        self.output_file = output_file
    
    def export(self, datasets: List[Dict], separate_by: str = "both") -> None:
        """
        Export datasets to Excel with organization.
        
        Args:
            datasets: List of dataset dictionaries
            separate_by: How to organize data - 'platform', 'organism', or 'both'
        """
        if not datasets:
            print("⚠️  No datasets to export.")
            return
        
        print(f"\n📊 Organizing and exporting {len(datasets)} datasets...")
        
        # Convert to DataFrame
        df = pd.DataFrame(datasets)
        
        # Add serial numbers
        df.insert(0, 'S.No.', range(1, len(df) + 1))
        
        # Ensure column order
        available_columns = [col for col in COLUMN_ORDER if col in df.columns]
        other_columns = [col for col in df.columns if col not in COLUMN_ORDER]
        df = df[available_columns + other_columns]
        
        if separate_by == "both":
            self._export_by_platform_and_organism(df)
        elif separate_by == "platform":
            self._export_by_platform(df)
        elif separate_by == "organism":
            self._export_by_organism(df)
        else:
            # Single sheet export
            self._export_single_sheet(df)
        
        print(f"✅ Export complete: {self.output_file}")
        self._print_summary(df)
    
    def _export_single_sheet(self, df: pd.DataFrame) -> None:
        """
        Export all data to a single sheet.
        
        Args:
            df: DataFrame to export
        """
        with pd.ExcelWriter(self.output_file, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='All Datasets', index=False)
    
    def _export_by_platform(self, df: pd.DataFrame) -> None:
        """
        Export data organized by platform (separate sheets).
        
        Args:
            df: DataFrame to export
        """
        with pd.ExcelWriter(self.output_file, engine='openpyxl') as writer:
            # Summary sheet
            self._write_summary_sheet(writer, df)
            
            # Group by platform
            if 'Source' in df.columns:
                grouped = df.groupby('Source')
                
                for platform, group_df in grouped:
                    # Reset serial numbers for each sheet
                    sheet_df = group_df.copy()
                    sheet_df['S.No.'] = range(1, len(sheet_df) + 1)
                    
                    sheet_name = self._sanitize_sheet_name(platform)
                    sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    def _export_by_organism(self, df: pd.DataFrame) -> None:
        """
        Export data organized by organism (human vs others).
        
        Args:
            df: DataFrame to export
        """
        with pd.ExcelWriter(self.output_file, engine='openpyxl') as writer:
            # Summary sheet
            self._write_summary_sheet(writer, df)
            
            # Separate human and non-human
            if 'Organism' in df.columns:
                human_df = df[df['Organism'].apply(is_human_organism)].copy()
                other_df = df[~df['Organism'].apply(is_human_organism)].copy()
                
                if not human_df.empty:
                    human_df['S.No.'] = range(1, len(human_df) + 1)
                    human_df.to_excel(writer, sheet_name='Human', index=False)
                
                if not other_df.empty:
                    other_df['S.No.'] = range(1, len(other_df) + 1)
                    other_df.to_excel(writer, sheet_name='Other Organisms', index=False)
    
    def _export_by_platform_and_organism(self, df: pd.DataFrame) -> None:
        """
        Export data organized by both platform and organism.
        
        Args:
            df: DataFrame to export
        """
        with pd.ExcelWriter(self.output_file, engine='openpyxl') as writer:
            # Summary sheet
            self._write_summary_sheet(writer, df)
            
            # Separate by organism first
            if 'Organism' in df.columns:
                human_df = df[df['Organism'].apply(is_human_organism)].copy()
                other_df = df[~df['Organism'].apply(is_human_organism)].copy()
                
                # Export human data by platform
                if not human_df.empty:
                    self._export_organism_by_platform(writer, human_df, "Human")
                
                # Export other organisms by platform
                if not other_df.empty:
                    self._export_organism_by_platform(writer, other_df, "Other")
    
    def _export_organism_by_platform(self, writer, df: pd.DataFrame, organism_label: str) -> None:
        """
        Export organism data organized by platform.
        
        Args:
            writer: Excel writer object
            df: DataFrame to export
            organism_label: Label for organism group (e.g., 'Human', 'Other')
        """
        if 'Source' in df.columns:
            grouped = df.groupby('Source')
            
            for platform, group_df in grouped:
                sheet_df = group_df.copy()
                sheet_df['S.No.'] = range(1, len(sheet_df) + 1)
                
                # Create sheet name like "Human - NCBI GEO"
                sheet_name = f"{organism_label} - {platform}"
                sheet_name = self._sanitize_sheet_name(sheet_name)
                
                sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    def _write_summary_sheet(self, writer, df: pd.DataFrame) -> None:
        """
        Write summary statistics sheet.
        
        Args:
            writer: Excel writer object
            df: DataFrame with all data
        """
        summary_data = []
        
        # Total datasets
        summary_data.append({"Metric": "Total Datasets", "Value": len(df)})
        
        # By platform
        if 'Source' in df.columns:
            platform_counts = df['Source'].value_counts()
            for platform, count in platform_counts.items():
                summary_data.append({"Metric": f"  {platform}", "Value": count})
        
        # By organism
        if 'Organism' in df.columns:
            human_count = df['Organism'].apply(is_human_organism).sum()
            other_count = len(df) - human_count
            summary_data.append({"Metric": "Human Datasets", "Value": human_count})
            summary_data.append({"Metric": "Other Organisms", "Value": other_count})
        
        # Unique organisms
        if 'Organism' in df.columns:
            unique_organisms = df['Organism'].nunique()
            summary_data.append({"Metric": "Unique Organisms", "Value": unique_organisms})
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
    
    def _sanitize_sheet_name(self, name: str) -> str:
        """
        Sanitize sheet name to comply with Excel limitations.
        
        Args:
            name: Original sheet name
        
        Returns:
            Sanitized sheet name
        """
        # Excel sheet names can't exceed 31 characters and can't contain certain characters
        name = name.replace('[', '').replace(']', '').replace('*', '').replace('?', '')
        name = name.replace('/', '-').replace('\\', '-').replace(':', '-')
        
        if len(name) > 31:
            name = name[:31]
        
        return name
    
    def _print_summary(self, df: pd.DataFrame) -> None:
        """
        Print summary statistics to console.
        
        Args:
            df: DataFrame with all data
        """
        print("\n" + "="*50)
        print("  SUMMARY")
        print("="*50)
        print(f"Total Datasets: {len(df)}")
        
        if 'Source' in df.columns:
            print("\nBy Platform:")
            platform_counts = df['Source'].value_counts()
            for platform, count in platform_counts.items():
                print(f"  • {platform}: {count}")
        
        if 'Organism' in df.columns:
            human_count = df['Organism'].apply(is_human_organism).sum()
            other_count = len(df) - human_count
            print(f"\nBy Organism:")
            print(f"  • Human: {human_count}")
            print(f"  • Other Organisms: {other_count}")
            
            # Top organisms
            print(f"\nTop 5 Organisms:")
            top_organisms = df['Organism'].value_counts().head(5)
            for organism, count in top_organisms.items():
                print(f"  • {organism}: {count}")
        
        print("="*50 + "\n")
