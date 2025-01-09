from typing import Dict, List, Union, Tuple

import pandas as pd

from coffee.config import logger
from coffee.exceptions import InvalidCalculationGraphException


def sort_data_topological(df: pd.DataFrame,
                          formula_col: str = 'formula',
                          is_calc_col: str = 'is_calculation',
                          item_col: str = 'name',
                          children_col: str = 'children',
                          split: bool = False) -> pd.DataFrame | Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Takes in a pd.DataFrame of items ready for creation or updating, converts them to a graph and
     sorts that graph topologically.


    :param df: a pandas.DataFrame of items ready
    :type df: pandas.DataFrame
    :param formula_col: what is the column name with the formula in your input DataFrame
    :type formula_col: str, optional
    :param item_col: Name of the column that contains the names of the items being added
    :type item_col: str, optional
    :param is_calc_col: what is the column that contains the boolean is_calculation
    :type is_calc_col: str, optional
    :param children_col: the column name of the output child symbols to be extracted from the formula column
    :type children_col: str, optional
    :param split: whether to the output into an in_calc_tree_df and independent_df or just return one DataFrame
    :type split: bool, optional
    :return: Topologically sort DataFrame of calculations; or tuple with DataFrame of items in calculation tree and
     DataFrame with independent items
    :rtype graph: pd.DataFrame | Tuple[pd.DataFrame, pd.DataFrame]
    """
    if len(df) <= 1:
        return df

    if formula_col not in df.columns:
        raise ValueError(f'Formula column {formula_col} not found in DataFrame')

    if is_calc_col not in df.columns:
        logger.info(f'Creating new column `{is_calc_col}` in DataFrame')
        df[is_calc_col] = df[formula_col].notnull().astype(bool)

    df_with_children = extract_formula_children(df,
                                                formula_col=formula_col,
                                                is_calc_col=is_calc_col,
                                                children_col=children_col)

    name_graph = dict()
    for index, row in df_with_children.iterrows():
        name_graph[str(row[item_col])] = row[children_col]

    name_graph = prune_missing_from_graph(graph=name_graph)

    roots = find_topological_graph_starts(name_graph)
    sorted_names = iterative_topological_sort(graph=name_graph, starts=roots, reverse=True)

    if split:
        # Determine if a row is a calculation or used in one
        calculations = df[df[is_calc_col]][item_col].tolist()
        all_children = set([child for sublist in name_graph.values() for child in sublist])
        df['calculation_status'] = df.apply(
            lambda x: 'in_calc_tree' if x[item_col] in calculations or x[item_col] in all_children else 'independent', axis=1
        )

        in_calc_tree_df = df[df['calculation_status'] == 'in_calc_tree'].drop('calculation_status', axis=1)
        independent_df = df[df['calculation_status'] == 'independent'].drop('calculation_status', axis=1)

        return in_calc_tree_df, independent_df
    else:
        item_name_map = {
            str(item['name']): item for index, item in df.iterrows()
        }
        response = [
            item_name_map[name]
            for name in sorted_names
            if name in item_name_map
        ]
        return pd.DataFrame(response)



def extract_formula_children(df: pd.DataFrame,
                             formula_col: str = 'formula',
                             is_calc_col: str = 'is_calculation',
                             children_col: str = 'children') -> pd.DataFrame:
    """
    Extracts item names (CP names) from a specified 'formula' column of a DataFrame,
    where each CP name is enclosed in square brackets. It adds these CP names as a list in a new
    column (default or specified) for each row where the specified 'is_calculation' column is True.
    The function retains all original columns and adds the new column to the DataFrame.

    :param df: The input DataFrame containing at least the specified 'formula' column.
               The 'formula' column contains the formulas as strings. The 'is_calculation' is an optional
               boolean column indicating whether the row's formula should be processed to extract CP names.
               If 'is_calculation' is not provided or does not exist, rows with a 'formula' are considered.
    :type df: pandas.DataFrame
    :param formula_col: The name of the column in 'df' that contains the formula strings. Defaults to 'formula'.
    :type formula_col: str, optional
    :param is_calc_col: The name of the optional boolean column in 'df' indicating if the row should be processed.
                        If not provided or the column does not exist, rows with a 'formula' are considered for processing.
    :type is_calc_col: str, optional
    :param children_col: The name of the output column to be added to 'df', which will contain lists of
                         extracted CP names. This column is created by the function.
    :type children_col: str, optional

    :return: A copy of the input DataFrame with an additional column (as specified by 'children_col').
             For rows where 'is_calculation' is True, this column will contain a list of extracted CP names
             from the 'formula'. For other rows, this column will be an empty list.
    :rtype: pandas.DataFrame
    """
    result_df = df.copy()
    name_pattern = r'\[([A-Z0-9_]+)\]'
    result_df[children_col] = [[] for _ in range(len(result_df))]

    if is_calc_col in result_df.columns:
        calculation_rows = result_df[is_calc_col]
    else:
        # If is_calc_col does not exist, consider rows with a non-empty/non-null formula as calculation rows
        calculation_rows = result_df[formula_col].notnull() & result_df[formula_col].str.strip().astype(bool)

    result_df.loc[calculation_rows, children_col] = result_df.loc[calculation_rows, formula_col].str.findall(
        name_pattern
    )

    return result_df


def prune_missing_from_graph(graph: dict[str, list[str]]):
    """
    Removes child vertices that don't exist as keys in the graph
    :param graph:
    :return:
    """
    return {key: [value for value in graph[key] if value in graph] for key in graph}


def find_topological_graph_starts(graph: Dict[str, List[str]]) -> List[str]:
    targets = set()
    # Populate target set
    for k, vs in graph.items():
        for v in vs:
            targets.add(v)

    starts = [k for k in graph if k not in targets]
    if len(starts) == 0:
        raise InvalidCalculationGraphException(
            "Graph does not have a start node - no item is set to calculation"
        )

    return starts


def iterative_topological_sort(
        graph: Dict[str, List[str]], starts: List[str], reverse=False
) -> List[str]:
    """
    From: https://stackoverflow.com/a/47234034.
    Adapted to support multiple root nodes.

    Example:
    graph = {
        '1' : ['2', '3'],
        '2': [],
        '3': []
    }
    start = '1'

    :param graph: dict with key parent node id and value list of child node ids
    :param starts: All the nodes in the graph that does not have any parent nodes.
    :param reverse: If True, child nodes will appear first in the list.
    :return:
    """
    seen = set()
    stack = []  # path variable is gone, stack and order are new
    order = []  # order will be in reverse order at first
    q = starts
    while q:
        v = q.pop()
        if v not in seen:
            seen.add(v)  # no need to append to path anymore
            q.extend(graph[v])

            while stack and v not in graph[stack[-1]]:  # new stuff here!
                order.append(stack.pop())
            stack.append(v)

    result = stack + order[::-1]
    if reverse:
        result.reverse()

    return result  # new return value!
