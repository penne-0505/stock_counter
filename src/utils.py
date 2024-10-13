import uuid
from dataclasses import dataclass

from colorama import Fore, Style
import discord


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def generate_id(stock_name: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, stock_name))


@dataclass
class Stock:
    detail: str = None
    group: str = None  # like 'food', 'drink', 'etc'
    stock_id: str = None
    count: int = 0
    price: int = None


# logging constants
INFO = f"{Fore.BLUE}[INFO]{Style.RESET_ALL}: "
ERROR = f"{Fore.RED}[ERROR]{Style.RESET_ALL}: "
WARN = f"{Fore.YELLOW}[WARNING]{Style.RESET_ALL}: "
DEBUG = f"{Fore.MAGENTA}[DEBUG]{Style.RESET_ALL}: "
SUCCESS = f"{Fore.GREEN}[SUCCESS]{Style.RESET_ALL}: "
FORMAT = str(f"{Fore.BLUE}%(asctime)s{Style.RESET_ALL} - %(message)s")
DATEFORMAT = str("%Y-%m-%d %H:%M:%S")


def blue(text: str) -> str:
    return f"{Fore.BLUE}{text}{Style.RESET_ALL}"


def red(text: str) -> str:
    return f"{Fore.RED}{text}{Style.RESET_ALL}"


def yellow(text: str) -> str:
    return f"{Fore.YELLOW}{text}{Style.RESET_ALL}"


def magenta(text: str) -> str:
    return f"{Fore.MAGENTA}{text}{Style.RESET_ALL}"


def green(text: str) -> str:
    return f"{Fore.GREEN}{text}{Style.RESET_ALL}"


def cyan(text: str) -> str:
    return f"{Fore.CYAN}{text}{Style.RESET_ALL}"


def bold(text: str) -> str:
    return f"{Style.BRIGHT}{text}{Style.RESET_ALL}"


class CommandsTranslator(discord.app_commands.Translator):
    async def translate(
        self,
        string: discord.app_commands.locale_str,
        locale: discord.Locale,
        context: discord.app_commands.TranslationContext,
    ) -> str | None:
        command_names = {
            "ja": {
                "ping": "ping",
                "add_stock": "商品の追加",
                "remove_stock": "商品の削除",
                "get_all_stocks": "全商品の取得",
                "search_stock": "商品の検索",
                "sort_by_group": "グループでソート",
                "sort_by_count": "個数でソート",
                "sort_by_price": "価格でソート",
                "calc_total_sales": "売上の計算",
                "Ping the bot.": "ボットにPingを送信します。",
                "Add a new stock to the stock list.": "商品リストに新しい商品を追加します。",
                "Remove a stock from the stock list.": "商品リストから商品を削除します。",
                "Get all stocks in the stock list.": "商品リスト内の全商品を取得します。",
                "Search a stock from the stock list and return messge link.": "商品リストから商品を検索し、メッセージリンクを返します。",
                "Sort all stocks by group.": "全商品をグループでソートします。",
                "Sort all stocks by count.": "全商品を個数でソートします。",
                "Sort all stocks by price.": "全商品を価格でソートします。",
                "Calculate total sales.": "売上を計算します。",
            },
            "en-US": {
                "ping": "ping",
                "add_stock": "add_stock",
                "remove_stock": "remove_stock",
                "get_all_stocks": "get_all_stocks",
                "search_stock": "search_stock",
                "sort_by_group": "sort_by_group",
                "sort_by_count": "sort_by_count",
                "sort_by_price": "sort_by_price",
                "calc_total_sales": "calc_total_sales",
                "Ping the bot.": "Ping the bot.",
                "Add a new stock to the stock list.": "Add a new stock to the stock list.",
                "Remove a stock from the stock list.": "Remove a stock from the stock list.",
                "Get all stocks in the stock list.": "Get all stocks in the stock list.",
                "Search a stock from the stock list and return messge link.": "Search a stock from the stock list and return messge link.",
                "Sort all stocks by group.": "Sort all stocks by group.",
                "Sort all stocks by count.": "Sort all stocks by count.",
                "Sort all stocks by price.": "Sort all stocks by price.",
                "Calculate total sales.": "Calculate total sales.",
            },
        }

        if (
            locale.value in command_names
            and string.message in command_names[locale.value]
        ):
            return command_names[locale.value][string.message]

        return None


if __name__ == "__main__":
    print(generate_id("test"))
