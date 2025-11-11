#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/2/27 13:34
@Author  : dmj-11740
@File    : excel_read.py
@Software: PyCharm
@desc    :
"""
import json
import os
import warnings


class BList(list):
    """
    一个继承list对象，可直接to_excel的列表
    """

    def to_excel(
            self,
            file_name,
            sheet_name: str = "sheet1",
            mode: str = "w",
            null_as_string: bool = False,
    ):
        """
            导出到Excel
        :param file_name: 文件名
        :param sheet_name: 簿名
        :param mode: 模式
        :param null_as_string: None输出成NULL
        :return:
        """
        file_name = (
            file_name + ".xlsx" if not file_name.endswith(".xlsx") else file_name
        )
        try:
            import pandas
        except:
            raise Exception("pandas not found!")
        data = []
        have_convert = False
        # 判断是否有嵌套字典, 有则转换成json字符串
        for key, value in self[0].items():
            if isinstance(value, dict) or isinstance(value, list):
                have_convert = True
                break
        if have_convert:
            for item in self:
                for key, value in item.items():
                    if isinstance(value, dict) or isinstance(value, list):
                        item[key] = json.dumps(value, ensure_ascii=False)
                data.append(item)
        df = pandas.DataFrame(data or self)
        mode = "w" if not os.path.exists(file_name) else mode
        if null_as_string:
            df = df.where(pandas.notna(df), "NULL")
        with pandas.ExcelWriter(
                file_name,
                mode=mode,
                engine="xlsxwriter",
                engine_kwargs={"options": {"strings_to_urls": False}},
        ) as writer:
            df.to_excel(writer, index=False, sheet_name=sheet_name)


class ExcelRead:
    def __init__(self, file_path, sheet_name=0, header=0):
        """
            读取Excel
        :param file_path:  文件路径
        :param sheet_name: 表名
        :param header: 字段key所在行索引
        """
        self.path = file_path
        self.sheet_name = sheet_name
        self.header = header
        self._sheet_names = None
        self.__values = None
        self.__sheet_name_bck = None

    @property
    def values(self) -> BList:
        """
            获取包含多个数据字典的列表
        :return:[{}...]
        """
        try:
            import pandas
        except:
            raise Exception("pandas not found!")
        if self.__values:
            return self.__values
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"找不到文件:{self.path}")

        null_like = {
            "#n/a",
            "#n/a n/a",
            "#na",
            "-1.#ind",
            "-1.#qnan",
            "-nan",
            "1.#ind",
            "1.#qnan",
            "na",
            "n/a",
            "nan",
            "null",
            "nil",
        }

        def clean_cell(x):
            if pandas.isna(x):
                return None
            lower = x.strip().lower()
            if lower in null_like:
                return None
            if lower == "true":
                return True
            if lower == "false":
                return False
            return x

        excel_name = self.path.rsplit("/", 1)[-1]
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("ignore", ResourceWarning)
            df = pandas.read_excel(
                self.path,
                sheet_name=self.sheet_name,
                header=self.header,
                keep_default_na=False,
            )
            df = df.astype("string")
        df = df.map(clean_cell)
        df_list = []
        for row in df.index.values:
            # loc为按列名索引 iloc为按位置索引，使用的是 [[行号], [列名]]
            df_line = df.loc[row, df.columns.values.tolist()].to_dict()
            df_list.append(df_line)
        self.__values = BList(df_list)
        return self.__values

    @property
    def values_str(self) -> BList:
        """
            获取包含多个数据字典的列表，但是value值皆为str，包括None,True,False
        :return:
        """
        json_str = BList()
        for value_json in self.values:
            json_str.append({key: str(value) for key, value in value_json.items()})
        return json_str

    def only_index(self, index: str, *args) -> dict:
        """
            根据keys，将list转换成dict，相同key的数据会合并到一个list
        :param index: key名
        :param args: 更多key名
        :return: {"key1###key2":[value1,value2...]}
        """
        index = [index]
        index.extend(args)
        item = {}
        for val in self.values:
            keys = "###".join([val.get(k, "") for k in index])
            assert (
                keys
            ), f"有值为空:{val[list(val.keys())[0]]}, {val[list(val.keys())[1]]}"
            item.setdefault(keys, [])
            item[keys].append(val)
        return item

    @property
    def values_all(self) -> BList:
        """
            获取所有工作表数据
        :return:
        """
        try:
            import pandas
        except:
            raise Exception("pandas not found!")
        excel_file = pandas.ExcelFile(self.path)
        self._sheet_names = excel_file.sheet_names
        items = BList()
        self.__sheet_name_bck = self.sheet_name
        for sheet_name in self._sheet_names:
            self.sheet_name = sheet_name
            item = self.values
            items.extend(item)
        self.sheet_name = self.__sheet_name_bck
        return items
