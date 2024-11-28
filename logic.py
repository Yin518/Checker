from random import randint
class UltimatePasswordGame:
    def __init__(self):
        self.players = []
        self.game_started = False  # 遊戲開始標誌
        self.range_set = False  # 設定範圍標誌
        self.current_turn = 0
        self.password = None
        self.lower_bound = None
        self.upper_bound = None

    def add_player(self, name):
        if name in self.players:
            return False, "玩家名稱已被使用，請選擇其他名稱。"
        self.players.append(name)
        if len(self.players) == 2:  # 第二位玩家加入時，設置遊戲為準備完成
            self.game_started = True
            return True, f"玩家 {name} 加入成功!\n遊戲已準備完成！"
        return True, f"玩家 {name} 加入成功！"

    def set_range(self, lower, upper, player_name):
        if len(self.players) < 2:
            return False, "等待另一位玩家加入。"
        if self.range_set:
            return False, "範圍已經設定！"
        if lower >= upper:
            return False, "請確認最低範圍小於最高範圍！"
        self.lower_bound = lower
        self.upper_bound = upper
        self.password = randint(lower, upper)
        self.range_set = True
        self.current_turn = 1  # 第二位玩家先猜
        return True, f"範圍設定成功！終極密碼範圍是：{lower}~{upper}"

    def is_ready(self):
        return self.game_started and self.range_set

    def get_status(self):
        print(f"當前狀態：{self.players}, 準備狀態: {self.game_started}, 範圍設置: {self.range_set}")
        return {
            "players": self.players,
            "current_turn": self.current_turn,
            "range": (self.lower_bound, self.upper_bound),
            "last_guess": self.last_guess if hasattr(self, 'last_guess') else None
        }

    def guess_number(self, guess, player_name):
        if guess < self.lower_bound or guess > self.upper_bound:
            return False, f"請輸入合法範圍內的數字：{self.lower_bound}~{self.upper_bound}。"
        self.last_guess = guess
        if guess == self.password:
            return True, f"恭喜 {player_name} 猜中終極密碼！"
        # 調整範圍
        if self.current_turn == 0:
            self.lower_bound = guess + 1
        else:
            self.upper_bound = guess - 1
        self.current_turn = 1 - self.current_turn  # 換人猜
        return False, f"目前範圍是 {self.lower_bound}~{self.upper_bound}，上一位玩家猜了：{guess}"
