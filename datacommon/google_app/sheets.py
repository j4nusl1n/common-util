import os

from google.oauth2 import service_account
from googleapiclient.discovery import build

__all__ = [
    'Sheet'
]

class Sheet(object):
    def __init__(self, sheet_id: str, credential_path: str=None, scope: list=None):
        """A wrapper class for accessing Google Spreadsheets

        Args:
            sheet_id (str): The id of the Google Spreadsheets
            credential_path (str, optional): Google Application Credentials file path. Defaults to None and uses environ GOOGLE_APPLICATION_CREDENTIALS.
            scope (list, optional): Google Spreadsheets auth scope. Defaults to None.
        """        
        if credential_path is None:
            credential_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', '')

        if scope is None:
            scope = [
                'https://www.googleapis.com/auth/drive',
                'https://www.googleapis.com/auth/drive.file',
                'https://www.googleapis.com/auth/spreadsheets',
            ]

        self.__cred = service_account.Credentials.from_service_account_file(
            credential_path,
            scopes=scope
        )
        
        self.__id = sheet_id
        self.__service = build('sheets', 'v4', credentials=self.__cred)
    
    @property
    def service(self):
        """Resource object for interacting with Google Spreadsheets service

        Returns:
            Resource: Resource object
        """        
        return self.__service

    @property
    def spreadsheets(self):
        """Resource object of the spreadsheets

        Returns:
            Resource: The spreadsheets Resource object
        """        
        return self.service.spreadsheets()

    @staticmethod
    def format_range(sheet_name, range_notation):
        """Construct a A1 notation for Google Spreadsheet

        Args:
            sheet_name (str): Name of the sheet
            range_notation (str): A1 notation without specific sheet name

        Returns:
            str: A1 notation with sheet name specified
        """        
        return "'{}'!{}".format(sheet_name, range_notation)

    def _exec_request(self, request, http=None):
        return request.execute(http=http)

    def fetch_sheet_metadata(self, params: dict=None):
        """Returns metadata of the spreadsheets

        Args:
            params (dict, optional): Parameters passing to the API. Defaults to None.

        Returns:
            dict: Response data as dict from API
        """        
        if params is None:
            params = {
                'includeGridData': False
            }

        request = self.spreadsheets.get(
            spreadsheetId=self.__id,
            includeGridData=params.get('includeGridData', False)
        )
        results = self._exec_request(request)

        return results

    def _spreadsheet_batchUpdate(self, requests: list) -> dict:
        """Wrapper method for sending Spreadsheets batchUpdate request

        Args:
            requests (list): A list consists of requests

        Returns:
            dict: A dict of the API responses
        """
        body = {
            'requests': requests
        }
        http_request = self.spreadsheets.batchUpdate(
            spreadsheetId=self.__id,
            body=body
        )
        results = self._exec_request(http_request)
        return results

    def create_sheet(self, sheet_name: str) -> dict:
        """Create sheet with sheet name specified

        Args:
            sheet_name (str): Sheet name to be created

        Returns:
            dict: Response from Spreadsheets API
        """
        sheet_properties = {
            'title': sheet_name
        }
        requests = [
            {
                'addSheet': {
                    'properties': sheet_properties
                }
            }
        ]
        return self._spreadsheet_batchUpdate(requests)

    def get_sheet_id(self, sheet_name: str) -> int:
        """Get id of the sheet with specific name

        Args:
            sheet_name (str): Sheet name to be searched

        Returns:
            int: Sheet id
        """
        metadata = self.fetch_sheet_metadata()
        if not metadata:
            return None

        for sheet in metadata['sheets']:
            if sheet['properties']['title'] == sheet_name:
                return sheet['properties']['sheetId']
        
        return None

    def delete_sheet_by_id(self, sheet_id: int) -> dict:
        """Delete sheet with specific id

        Args:
            sheet_id (int): Sheet id

        Returns:
            dict: Response from Spreadsheets API
        """
        request = [
            {
                'deleteSheet': {
                    'sheetId': sheet_id
                }
            }
        ]

        return self._spreadsheet_batchUpdate(request)

    def delete_sheet_by_name(self, sheet_name: str) -> dict:
        """Delete sheet with specific name

        Args:
            sheet_name (str): Sheet name

        Returns:
            dict: Response from Spreadsheets API
        """
        sheet_id = self.get_sheet_id(sheet_name)
        if sheet_id is None:
            return None

        return self.delete_sheet_by_id(sheet_id)

    def get_values_by_range(self, _range: str) -> list:
        """Get values from sheet within range specified

        Args:
            _range (str): A1 notation of the range

        Raises:
            TypeError: if type of {_range} is not str

        Returns:
            list: Values from the range
        """
        if not isinstance(_range, (str,)):
            raise TypeError('Type of argument "_range" is invalid')

        resp = self.spreadsheets.values().get(
            spreadsheetId=self.__id,
            range=_range
        )
        results = self._exec_request(resp)
        return results.get('values', [])

    def update_values_by_range(self, _range: str, values: list, valueInputOption: str='USER_ENTERED') -> int:
        """Update values within specific range

        Args:
            _range (str): A1 notation of the range to be updated
            values (list): A list of rows of new values
            valueInputOption (str, optional): Spreadsheets API parameters. Defaults to 'USER_ENTERED'.

        Returns:
            int: The number of cells updated
        """
        body = {
            'values': values
        }
        request = self.spreadsheets.values().update(
            spreadsheetId=self.__id,
            range=_range,
            valueInputOption=valueInputOption,
            body=body
        )
        results = self._exec_request(request)
        return results.get('updatedCells')

    def append_values(self, _range: str, values: list, valueInputOption: str='USER_ENTERED'):
        """Append new rows with range column specified

        Args:
            _range (str): A1 notation of the columns to append
            values (list): A list of rows to append
            valueInputOption (str, optional): Spreadsheets API parameter. Defaults to 'USER_ENTERED'.

        Returns:
            dict: Information about the updates that were applied
        """
        body = {
            'values': values
        }
        request = self.spreadsheets.values().append(
            spreadsheetId=self.__id,
            range=_range,
            valueInputOption=valueInputOption,
            body=body
        )
        results = self._exec_request(request)
        return results.get('updates')
