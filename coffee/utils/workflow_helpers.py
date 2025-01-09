from datetime import datetime
from threading import Thread, Semaphore, Lock
from typing import Callable

import pandas as pd
import pandera as pa
from tqdm import tqdm

from coffee.config import logger, settings
from coffee.exceptions.helper_exceptions import MultipleFormulaColumnException
from coffee.utils.calc_helpers import sort_data_topological
from coffee.utils.helpers import check_csv_format


CONCURRENT_REQUESTS = settings.CONCURRENT_REQUEST_LIMIT if settings else 4


# region generic csv
def check_and_sort_formula_columns(df: pd.DataFrame):
    """
    Sorts df columns in order of formula references - non-calculated columns first
    :raises MultipleFormulaColumnException: if multiple formula columns exist
    """
    formula_cols = [col for col in df.columns if 'formula' in col]

    if len(formula_cols) > 0:
        if len(formula_cols) > 1:
            raise MultipleFormulaColumnException(f'Received more formula columns than expected [{str(formula_cols)}]')
        else:
            formula_col = formula_cols[0]
            if df[formula_col].notna().any():
                df = sort_data_topological(df,
                                           formula_col=formula_col,
                                           is_calc_col='is_calculation',
                                           children_col='formula_variables')

        df[formula_col] = df[formula_col].fillna('')


def read_and_check_csv(csv_path: str, expected_csv_columns: dict[str, pa.Column], operation: str) -> pd.DataFrame:
    """read bulk upload csv from file path, performing columns checks before returning"""
    df = pd.read_csv(csv_path, dtype={'name_formula': str, 'formula': str})
    df = df.fillna('').copy()

    check_csv_format(df, expected_csv_columns)

    df[operation] = False
    df[operation + '_error'] = ''

    check_and_sort_formula_columns(df)

    return df


def upload_models_from_df(df: pd.DataFrame, operation_callable: Callable, operation: str):
    for index, row in tqdm(df.iterrows(), total=len(df), desc="Processing"):
        try:
            # Call the passed operation_callable with row as an argument
            operation_callable(row)
            df.at[index, operation] = True
        except Exception as e:
            df.at[index, operation + '_error'] = str(e)
            logger.error(f"Error processing row {index}: {e}")


def upload_models_from_df_multithreaded(df: pd.DataFrame, operation_callable: Callable, operation: str):
    """
    Uploads `CONCURRENT_REQUESTS` rows from df at a time
    """
    semaphore = Semaphore(CONCURRENT_REQUESTS)
    lock = Lock()

    def inner_upload_func(idx, df_row, pbar):
        semaphore.acquire()
        try:
            # Call the passed operation_callable with row as an argument
            operation_callable(df_row)
            df.at[idx, operation] = True
        except Exception as e:
            df.at[idx, operation + '_error'] = str(e)
            logger.error(f"Error processing row {idx}: {e}")
        finally:
            semaphore.release()
            # Update the progress bar in a thread-safe way, with lock
            with lock:
                pbar.update(1)

    threads = []
    with tqdm(total=len(df), desc=operation, unit='row') as pbar:
        for index, row in df.iterrows():
            thread = Thread(target=inner_upload_func, args=(index, row, pbar))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()


def save_updated_csv(df: pd.DataFrame, csv_path: str, operation: str):
    processed_csv_path = csv_path.replace('.csv', f'_{operation}_{datetime.now().strftime("%Y%m%d_%H%M")}.csv')
    df.to_csv(processed_csv_path, index=False)
    logger.info(f"Processing complete. Results saved to {processed_csv_path}")


def process_csv_generic(csv_path: str, expected_csv_columns: dict[str, pa.Column], operation_callable: Callable,
                        operation: str = 'processed', upload_multithreaded: bool = False):
    """
    A generic method for processing rows of a CSV file and applying a specified operation to each row.

    This method reads a CSV file from the given path, checks if it matches the expected format, and iterates
    through each row. For each row, it calls the provided `operation_callable` with the row as an argument.
    It tracks the success or failure of operations for each row and saves the results to a new CSV file.

    :param csv_path: Path to the CSV file to be processed. The file should match the expected format for
                     the specific operation being performed (e.g., columns for 'component_type', 'constant_property',
                     and 'series' for collation operations).
    :type csv_path: str
    :param expected_csv_columns: A dictionary with the expected columns to be processed.
    :type expected_csv_columns: dict[str, pa.Column]
    :param operation_callable: A callable (function or method) that will be executed for each row of the CSV.
                               The callable should accept a single argument: the row to be processed.
    :type operation_callable: callable
    :param operation: The name of the operation to be performed (e.g., processed, collated, linked, created)
    :type operation: str, optional
    :param upload_multithreaded: Executes `CONCURRENT_REQUESTS` requests concurrently in python threads
        :type operation: str, optional
    :return: True if the file was processed successfully. The method also saves a new CSV file with a suffix
             indicating it has been processed, which includes columns for 'processed' (a boolean indicating
             whether the operation was successful) and 'error' (containing error messages if any).
    """
    df = read_and_check_csv(csv_path, expected_csv_columns, operation)

    if upload_multithreaded:
        upload_models_from_df_multithreaded(df, operation_callable, operation)
    else:
        upload_models_from_df(df, operation_callable, operation)

    save_updated_csv(df, csv_path, operation)

    return True
# endregion


def get_extra_kwargs(row: pd.Series,
                     main_cols: list[str],
                     lower_cols: list[str],
                     expected_csv_columns: dict[str, pa.Column]) -> dict[str, str]:
    extra_kwargs = {}
    for k, v in row.to_dict().items():
        if (k not in main_cols) and (k in expected_csv_columns):
            if k in lower_cols:
                extra_kwargs.update({k: v.lower()})
            else:
                extra_kwargs.update({k: v})
    return extra_kwargs
