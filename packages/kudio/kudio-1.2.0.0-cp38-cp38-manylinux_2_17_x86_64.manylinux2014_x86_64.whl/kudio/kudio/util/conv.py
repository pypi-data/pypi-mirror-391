import os
import pandas as pd
from openpyxl.utils import get_column_letter

__all__ = [
    'data2xlsx',
    'lowercase',
    'upercase',
]


def data2xlsx(data, xlsx_dir, sheet_name, index=False, fit_column=True):
    if not pd.__version__ >= '1.0.3':
        print("Need pandas version >= 1.0.3")
        return
    if isinstance(data, dict):
        try:
            data_frame = pd.DataFrame.from_dict(data, orient='columns')
        except Exception as e:
            print(e)
            return f'[data2xlsx] data error: {e}'
    elif isinstance(data, pd.DataFrame):
        data_frame = data
    else:
        return '[data2xlsx] check the data type'
    if not os.path.isdir(os.path.dirname(xlsx_dir)):
        os.makedirs(os.path.dirname(xlsx_dir))
    # write excel (pandas==1.0.3)
    if os.path.isfile(xlsx_dir):
        with pd.ExcelWriter(xlsx_dir, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        # with pd.ExcelWriter(xlsx_dir, engine='openpyxl', mode='a') as writer:
            data_frame.to_excel(writer, sheet_name=sheet_name, index=index)
            if fit_column:  # 按文字大小調整column size
                workbook = writer.book
                worksheet = workbook[sheet_name]
                for column_cells in worksheet.columns:
                    length = max(len(str(cell.value)) for cell in column_cells)
                    worksheet.column_dimensions[get_column_letter(column_cells[0].column)].width = length
    else:
        data_frame.to_excel(xlsx_dir, sheet_name=sheet_name, index=index)

def lowercase(lst):
    return [_.lower() for _ in lst if isinstance(_, str)]


def upercase(lst):
    return [_.upper() for _ in lst if isinstance(_, str)]
