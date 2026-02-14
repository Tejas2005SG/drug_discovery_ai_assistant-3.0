"""
Google Drive Data Manager for Drug Discovery AI
Handles all data I/O to/from Google Drive
"""

import os
import json
import pickle
import pandas as pd
from pathlib import Path

class GoogleDriveManager:
    """
    Manages all data storage on Google Drive
    Assumes Google Drive is mounted at G:\ or accessible path
    """
    
    def __init__(self, drive_path="G:\\My Drive\\drug_discovery_ai"):
        """
        Initialize with Google Drive path
        
        Args:
            drive_path: Path to Google Drive folder (Windows: G:\, Mac/Linux: ~/Google Drive)
        """
        self.drive_path = Path(drive_path)
        self.datasets_path = self.drive_path / "datasets"
        self.models_path = self.drive_path / "models"
        self.results_path = self.drive_path / "results"
        
        # Create directories if they don't exist
        self._create_directories()
        
        print("="*70)
        print("GOOGLE DRIVE MANAGER INITIALIZED")
        print("="*70)
        print(f"Drive Path: {self.drive_path}")
        print(f"Datasets: {self.datasets_path}")
        print(f"Models: {self.models_path}")
        print(f"Results: {self.results_path}")
        print("="*70)
    
    def _create_directories(self):
        """Create necessary directories on Google Drive"""
        for path in [self.datasets_path, self.models_path, self.results_path]:
            path.mkdir(parents=True, exist_ok=True)
    
    def save_dataset(self, data, filename, format='json'):
        """
        Save dataset to Google Drive
        
        Args:
            data: Data to save (DataFrame, dict, list)
            filename: Name of file
            format: 'json', 'csv', 'pkl'
        """
        filepath = self.datasets_path / filename
        
        if format == 'json':
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        elif format == 'csv' and isinstance(data, pd.DataFrame):
            data.to_csv(filepath, index=False)
        elif format == 'pkl':
            with open(filepath, 'wb') as f:
                pickle.dump(data, f)
        
        print(f"[OK] Saved to Google Drive: {filepath}")
        return filepath
    
    def load_dataset(self, filename, format='json'):
        """Load dataset from Google Drive"""
        filepath = self.datasets_path / filename
        
        if not filepath.exists():
            print(f"[WARNING] File not found: {filepath}")
            return None
        
        if format == 'json':
            with open(filepath, 'r') as f:
                return json.load(f)
        elif format == 'csv':
            return pd.read_csv(filepath)
        elif format == 'pkl':
            with open(filepath, 'rb') as f:
                return pickle.load(f)
    
    def save_model_weights(self, model_state, model_name):
        """Save model weights to Google Drive"""
        filepath = self.models_path / f"{model_name}.pkl"
        with open(filepath, 'wb') as f:
            pickle.dump(model_state, f)
        print(f"[OK] Model saved: {filepath}")
        return filepath
    
    def load_model_weights(self, model_name):
        """Load model weights from Google Drive"""
        filepath = self.models_path / f"{model_name}.pkl"
        if not filepath.exists():
            return None
        with open(filepath, 'rb') as f:
            return pickle.load(f)
    
    def save_results(self, results, experiment_name):
        """Save experiment results"""
        filepath = self.results_path / f"{experiment_name}.json"
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"[OK] Results saved: {filepath}")
        return filepath
    
    def list_datasets(self):
        """List all datasets in Google Drive"""
        files = list(self.datasets_path.glob('*'))
        print("\n[DATASETS ON GOOGLE DRIVE]")
        for f in files:
            size_mb = f.stat().st_size / (1024 * 1024)
            print(f"  • {f.name} ({size_mb:.1f} MB)")
        return files
    
    def get_storage_stats(self):
        """Get storage usage statistics"""
        def get_dir_size(path):
            total = 0
            for file in path.rglob('*'):
                if file.is_file():
                    total += file.stat().st_size
            return total / (1024 * 1024 * 1024)  # Convert to GB
        
        datasets_gb = get_dir_size(self.datasets_path)
        models_gb = get_dir_size(self.models_path)
        results_gb = get_dir_size(self.results_path)
        total_gb = datasets_gb + models_gb + results_gb
        
        print("\n[STORAGE STATISTICS]")
        print(f"  Datasets: {datasets_gb:.2f} GB")
        print(f"  Models:   {models_gb:.2f} GB")
        print(f"  Results:  {results_gb:.2f} GB")
        print(f"  Total:    {total_gb:.2f} GB / 15.00 GB ({(total_gb/15)*100:.1f}%)")
        
        return {
            'datasets_gb': datasets_gb,
            'models_gb': models_gb,
            'results_gb': results_gb,
            'total_gb': total_gb,
            'remaining_gb': 15 - total_gb
        }


# Test the manager
if __name__ == "__main__":
    # Initialize (adjust path for your system)
    # Windows: G:\My Drive\drug_discovery_ai
    # Mac/Linux: ~/Google Drive/drug_discovery_ai
    
    drive_manager = GoogleDriveManager("G:\\My Drive\\drug_discovery_ai")
    
    # Show storage stats
    stats = drive_manager.get_storage_stats()
    
    # List existing datasets
    drive_manager.list_datasets()
