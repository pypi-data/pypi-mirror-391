from dataclasses import dataclass

@dataclass
class BaseConf:
    # runtime parameters
    sub_file_path: str
    annotate_mode: str
    data_root_path: str
    result_root_path: str

    # annotate column keys
    cell_type_col: str
    confidence_col: str
    unknown_key: str
