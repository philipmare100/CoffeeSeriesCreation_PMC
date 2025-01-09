import pandas as pd
from typing import Dict, Any, Optional


class DataObject:
    """
    A class representing the data object returned by custom data endpoints.
    """
    def __init__(self, raw_data: Dict[str, Any]):
        self.raw_data = raw_data

    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert raw data to a pandas DataFrame.
        """
        return pd.DataFrame(self.raw_data)


class SeriesDataObject:
    """
    Represents series data returned by the GetData endpoint,
    including data, quality, missing_values, uncertainties, and query parameters as attributes.
    """

    def __init__(self,
                 data: Dict[str, Dict[str, Any]],
                 quality: Optional[Dict[str, Dict[str, Any]]] = None,
                 missing_values: Optional[Dict[str, Dict[str, Any]]] = None,
                 uncertainties: Optional[Dict[str, Dict[str, Any]]] = None,
                 **kwargs):
        # Convert dictionaries to DataFrames
        self.data = self._dict_of_series_to_df(data)
        self.quality = self._dict_of_series_to_df(quality) if quality else None
        self.missing_values = self._dict_of_series_to_df(missing_values) if missing_values else None
        self.uncertainties = self._dict_of_series_to_df(uncertainties) if uncertainties else None

        # Set the query params as attributes, excluding protected ones
        for key, value in kwargs.items():
            if not key.startswith('_'):
                setattr(self, key, value)

    @staticmethod
    def _dict_of_series_to_df(dict_of_series: Dict[str, Dict[str, Any]]) -> pd.DataFrame:
        """
        Converts a dictionary of series into a pandas DataFrame.
        """
        df = pd.DataFrame()
        for series_name, series_data in dict_of_series.items():
            temp_df = pd.DataFrame.from_dict(series_data, orient='index', columns=[series_name])
            temp_df.index = pd.to_datetime(temp_df.index)
            df = pd.concat([df, temp_df], axis=1)
        return df

    def to_dataframe(self) -> pd.DataFrame:
        """
        Combine data, quality, missing_values, and uncertainties into a single DataFrame.
        """
        df = self.data.copy()

        # Merge quality DataFrame
        if self.quality is not None:
            quality_df = self.quality.add_suffix('_quality')
            df = df.join(quality_df, how='left')

        # Merge missing_values DataFrame
        if self.missing_values is not None:
            missing_df = self.missing_values.add_suffix('_missing')
            df = df.join(missing_df, how='left')

        # Merge uncertainties DataFrame
        if self.uncertainties is not None:
            uncertainties_df = self.uncertainties.add_suffix('_uncertainty')
            df = df.join(uncertainties_df, how='left')

        # Reset index to have 'timestamp' as a column
        df = df.reset_index().rename(columns={'index': 'timestamp'})

        return df

