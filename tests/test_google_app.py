import os
import json
import unittest

import pytest
from googleapiclient.http import HttpMock

from ..datacommon.google_app import *

class MockSheet(Sheet):
    @property
    def mock_response(self):
        return self.__mock_resp

    @mock_response.setter
    def mock_response(self, mock_resp):
        self.__mock_resp = mock_resp

    def _exec_request(self, request):
        return request.execute(http=self.__mock_resp)

class Test_Sheet(unittest.TestCase):
    def setUp(self):
        self.sh = MockSheet('')

    def test_format_range(self):
        self.assertEqual(self.sh.format_range('helloworld', 'A1:B1'), "'helloworld'!A1:B1")

    def test_fetch_sheet_metadata(self):
        expect = {
            'spreadsheetId': '1zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz', 
            'properties': {
                'title': 'spreadsheet_title', 
                'locale': 'zh_TW', 
                'autoRecalc': 'ON_CHANGE', 
                'timeZone': 'Asia/Shanghai', 
                'defaultFormat': {
                    'backgroundColor': {'red': 1, 'green': 1, 'blue': 1}, 
                    'padding': {'top': 2, 'right': 3, 'bottom': 2, 'left': 3}, 
                    'verticalAlignment': 'BOTTOM', 'wrapStrategy': 'OVERFLOW_CELL', 
                    'textFormat': {
                        'foregroundColor': {}, 
                        'fontFamily': 'arial,sans,sans-serif', 
                        'fontSize': 10, 
                        'bold': False, 
                        'italic': False, 
                        'strikethrough': False, 
                        'underline': False, 
                        'foregroundColorStyle': {'rgbColor': {}}
                    }, 
                    'backgroundColorStyle': {
                        'rgbColor': {'red': 1, 'green': 1, 'blue': 1}
                    }
                }
            }, 
            'sheets': [
                {
                    'properties': {
                        'sheetId': 0, 
                        'title': 'sheet1', 'index': 0, 'sheetType': 'GRID', 'gridProperties': {'rowCount': 1000, 'columnCount': 26}
                    }
                }
            ], 
            'spreadsheetUrl': 'https://docs.google.com/spreadsheets/d/1zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz/edit'
        }
        mock_resp = HttpMock()
        mock_resp.data = json.dumps(expect)
        self.sh.mock_response = mock_resp
        self.assertDictEqual(self.sh.fetch_sheet_metadata(), expect)

    def test__spreadsheet_batchUpdate(self):
        expect = {
            "addNamedRange": {},
            "addSheet": {},
            "addFilterView": {},
            "duplicateFilterView": {},
            "duplicateSheet": {},
            "findReplace": {},
            "updateEmbeddedObjectPosition": {},
            "updateConditionalFormatRule": {},
            "deleteConditionalFormatRule": {},
            "addProtectedRange": {},
            "addChart": {},
            "addBanding": {},
            "createDeveloperMetadata": {},
            "updateDeveloperMetadata": {},
            "deleteDeveloperMetadata": {},
            "addDimensionGroup": {},
            "deleteDimensionGroup": {},
            "trimWhitespace": {},
            "deleteDuplicates": {},
            "addSlicer": {}
        }
        mock_resp = HttpMock()
        mock_resp.data = json.dumps(expect)
        self.sh.mock_response = mock_resp

        self.assertGreaterEqual(
            expect.items(),
            self.sh._spreadsheet_batchUpdate(
                [
                    {
                        'addSheet': {
                            'properties': {
                                'title': 'test'
                            }
                        }
                    }
                ]
            ).items()
        )

    def test_get_values_by_range(self):
        expect = {
            "range": "A1:C1",
            "values": [
                [1,2,3]
            ]
        }
        mock_resp = HttpMock()
        mock_resp.data = json.dumps(expect)
        self.sh.mock_response = mock_resp

        self.assertListEqual(expect['values'], self.sh.get_values_by_range('A1:C1'))

if __name__ == "__main__":
    unittest.main(verbosity=2)