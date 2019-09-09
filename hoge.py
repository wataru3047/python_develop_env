import requests


class WekanAPI:
    """
    wekanのapiを操作するためのクラス
    """

    def __init__(self, wekan_url: str, username: str, password: str):
        """
        コンストラクタ wekanのURLとユーザー名、パスワードをクラス変数に格納してログインまで行う
        Args:
            wekan_url: str
                wekanのURL
            username: str
                wekanに登録しているユーザ名
            password: str
                wekanに登録しているパスワード

        Return:
            なし
        """
        self.session = requests.Session()
        self.proxies = None
        self.wekan_url = wekan_url
        credentials = {"username": username, "password": password}
        # wekanにログインしておく
        api_login = self.api_call("/users/login", data=credentials, authed=False)
        self.token = api_login["token"]
        self.user_id = api_login["id"]

    def api_call(self, api_url: str, data: dict = None, authed=True):
        """
        wekanのAPIを叩く関数
        Args:
            api_url: str
                叩きたいapiのurl
            data: dict
                postで送るユーザ情報

        Return: dict
            apiの結果。jsonで帰ってくる
        """
        if data is None:
            api_response = self.session.get(
                "{}{}".format(self.wekan_url, api_url),
                headers={"Authorization": "Bearer {}".format(self.token)},
                proxies=self.proxies,
            )
        else:
            if authed:
                headers = {"Authorization": "Bearer {}".format(self.token)}
            else:
                headers = {}
            api_response = self.session.post(
                "{}{}".format(self.wekan_url, api_url),
                data=data,
                headers=headers,
                proxies=self.proxies,
            )
        return api_response.json()

    def get_boards(self) -> list:
        """
        すべてのボードのIDとタイトルをdictでまとめたlist取得
        Args:
            なし
        Return: list[<dict>]
            wekanに登録されているボードのIDとタイトルのdictをまとめたlist
        """
        return self.api_call("/api/users/{}/boards".format(self.user_id))

    def get_lists(self, board_id: str) -> list:
        """
        ボード内のすべてのリストのIDとタイトルをdictでまとめたlistを取得
        Args:
            board_id: str
                リストを取得したいボードのID
        Return: list[<dict>]
            ボード内の全てのリストのIDとタイトルをdictでまとめたlist
        """
        return self.api_call("/api/boards/{}/lists".format(board_id))

    def get_cards(self, board_id: str, list_id: str) -> list:
        """
        リスト内のすべてのカードのIDとタイトルをdictでまとめたlistを取得
        Args:
            board_id: str
                ボードID
            list_id: str
                リストID
        Return: list[<dict>]
            リスト内のすべてのカードのIDとタイトルをdictでまとめたlist
        """
        return self.api_call("/api/boards/{}/lists/{}/cards".format(board_id, list_id))

    def get_card_data(self, board_id: str, list_id: str, card_id: str) -> list:
        """
        カード情報をdictでまとめたlistを取得
        Args:
            board_id: str
                ボードID
            list_id: str
                リストID
            card_id: str
                カードID
        Return: list[<dict>]
            カード情報をdictでまとめたlist
        """
        return self.api_call(
            "/api/boards/{}/lists/{}/cards/{}".format(board_id, list_id, card_id)
        )

    def get_board_id(self, board_title: str) -> str:
        """
        指定したタイトルのボードIDを取得
        Args:
            board_title: str
                ボードタイトル
        Return: str
            ボードID
        """
        boards = self.get_boards()
        board_id = ""
        for board in boards:
            board_title_ = board["title"]
            if board_title == board_title_:
                board_id = board["_id"]
                break
        return board_id

    def get_list_title(self, lists: list, list_id: str) -> str:
        """
        リストIDからリストタイトルを取得する
        Args:
            lists: list[<dict>]
                すべてのリスト情報をまとめたlist
            list_id: str
                リストID
        Return: str
            リストタイトル
        """
        list_title = ""
        for list_ in lists:
            list_id_ = list_["_id"]
            if list_id == list_id_:
                list_title = list_["title"]
                break
        return list_title

    def get_list_id(self, lists: list, list_title: str) -> str:
        """
        リストタイトルからリストIDを取得する
        Args:
            lists: list[<dict>]
                すべてのリスト情報をまとめたlist
            list_title: str
                リストタイトル
        Return: str
            リストID
        """
        list_id = ""
        for list_ in lists:
            list_title_ = list_["title"]
            if list_title == list_title_:
                list_id = list_["_id"]
                break
        return list_id

    def get_all_card_data(self, board_title: str) -> list:
        """
        指定したタイトルのボードに登録されているすべてのカード情報を取得
        Args:
            board_title: str
                ボードタイトル
        Return: list[<dict>]
            指定したボードタイトルに登録されているすべてのカード情報
        """
        card_datas = []
        board_id = self.get_board_id(board_title)
        lists = self.get_lists(board_id)
        for list_ in lists:
            list_id = list_["_id"]
            cards = self.get_cards(board_id, list_id)
            for card in cards:
                card_datas.append(self.get_card_data(board_id, list_id, card["_id"]))

        return card_datas

    def add_card(self, board_title: str, list_title: str, card_data: dict):
        """
        指定したボード、リストに新たにカードを追加する
        Args:
            board_title: str
                ボードタイトル
            list_title: str
                リストタイトル
            card_data: dict
                登録するカードのデータ
        Return: 
            
        """
        # 登録に必要なボードID、リストIDをタイトルから取得
        board_id = self.get_board_id(board_title)
        lists = self.get_lists(board_id)
        list_id = self.get_list_id(lists, list_title)
        # apiを叩いてカードを新規登録
        self.api_call(
            "/api/boards/{}/lists/{}/cards".format(board_id, list_id), data=card_data
        )


if __name__ == "__main__":
    wekan_url = "http://localhost:80"
    username = "wataru"
    password = "30470818"
    board_title = "wataru"
    wekan = WekanAPI(wekan_url, username, password)
    # 全てのカード情報を取得
    all_cards_data = wekan.get_all_card_data(board_title)
    card_data = {}

