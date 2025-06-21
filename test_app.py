import unittest
from app import app
import tempfile
import os
from bs4 import BeautifulSoup  # pip install beautifulsoup4

class FlaskHypothesisTestCase(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

        # テスト用CSVファイルを一時作成
        self.csv_data = "group,value\nA,1\nA,2\nB,3\nB,4"
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
        self.temp_file.write(self.csv_data.encode())
        self.temp_file.close()
    
    def tearDown(self):
        os.unlink(self.temp_file.name)

    def test_upload_shows_columns(self):
        # ステップ1：CSVをアップロードして列が表示されるか
        with open(self.temp_file.name, 'rb') as f:
            response = self.client.post('/', data={'file': f}, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)
        self.assertIn('group'.encode(), response.data)
        self.assertIn('value'.encode(), response.data)

    def test_upload_and_ttest_execution(self):
        # アップロード（df_pathを取得）
        with open(self.temp_file.name, 'rb') as f:
            upload_response = self.client.post('/', data={'file': f}, content_type='multipart/form-data')
        self.assertEqual(upload_response.status_code, 200)

        # hidden input から df_path を取得
        soup = BeautifulSoup(upload_response.data, 'html.parser')
        df_path = soup.find('input', {'name': 'df_path'})['value']

        # t検定を実行
        response = self.client.post('/test', data={
            'df_path': df_path,
            'test_type': 't_test',
            'col1': 'value',
            'col2': 'group'
        })
        self.assertEqual(response.status_code, 200)
        html = response.data.decode()

        # 検定結果用のdiv（class指定）
        # result_div = soup.find('div', class_='alert alert-info mt-4')
        # self.assertIsNotNone(result_div, "検定結果のdivが見つかりません")

        # # 表内のすべての行を走査
        # rows = result_div.find_all('tr')
        # pval_found = False
  
        # for row in rows:
        #     header = row.find('th')
        #     if header and 'p値' in header.text:
        #         value_cell = row.find('td')
        #         print("p値セルの内容:", value_cell.text)
        #         pval_found = True
        #         break

        # self.assertTrue(pval_found, "検定結果テーブルに p値 の行が見つかりません")

if __name__ == '__main__':
    unittest.main()