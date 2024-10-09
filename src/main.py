import asyncio
import logging
import os

import db_manager
import discord
from discord.app_commands import locale_str

from embed_manager import EmbedManager
from utils import (
    INFO,
    ERROR,
    WARN,
    DEBUG,
    SUCCESS,
    FORMAT,
    DATEFORMAT,
    blue,
    red,
    yellow,
    magenta,
    green,
    cyan,
    bold,
    CommandsTranslator,
    Stock,
)
from view_manager import StockManageView


intents = discord.Intents.all()

logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt=DATEFORMAT)

class Client(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.db_manager = db_manager.DBManager()
        self.embed_manager = EmbedManager()
    

    async def on_ready(self):
        await self.sync_commands()
        
        self.target_guild = self.get_guild(int(os.getenv('STOCK_CONTROL_GUILD')))
        self.target_channel = self.target_guild.get_channel(int(os.getenv('STOCK_CONTROL_CHANNEL')))
        
        # クライアント再起動時は前のメッセージを削除
        async for message in self.target_channel.history(limit=200):
            await message.delete()
        
        view = StockManageView()
        
        all_stocks = await self.db_manager.get_all_stock()
        sorted_stocks = await sort_stocks_by_group(all_stocks)
        
        
        # ストック(商品)ごとにメッセージを送信
        try:
            for stock in sorted_stocks:
                embed = self.embed_manager.get_embed(
                    stock.detail,
                    stock.count,
                    stock.stock_id,
                    price=stock.price,
                    group=stock.group
                )
                message = await self.target_channel.send(
                    embed=embed,
                    view=view,
                    silent=True
                )
                await asyncio.sleep(0.5)
                await self.target_channel.send('‎', silent=True)
                await asyncio.sleep(0.5)
        except Exception as e:
            logging.error(ERROR + f'Error occurred while sending stock messages:\n{e}')
        
        logging.info(SUCCESS + 'All stock messages have been sent.')
        logging.info(INFO + f'Logged in as {green(self.user.name)} ({blue(self.user.id)})')
        logging.info(INFO + f'Connected to {green(len(self.guilds))} guilds')
        logging.info(INFO + bold('Bot is ready.'))

    async def setup_hook(self) -> None:
        await tree.set_translator(CommandsTranslator())

    async def sync_commands(self) -> None:
        await tree.sync()
    
    async def on_app_command_completion(
        self,
        interaction: discord.Interaction,
        command: discord.app_commands.Command | discord.app_commands.ContextMenu
        ):
        # 装飾してログを出力
        exec_guild = yellow(interaction.guild) if interaction.guild else 'DM'
        exec_channel = magenta(interaction.channel) if interaction.channel else '(DM)'
        exec_user = interaction.user
        user_name = blue(exec_user.name)
        user_id = blue(exec_user.id)
        exec_command = green(command.name)
        logging.info(INFO + f'Command executed by {user_name}({user_id}): {exec_command} in {exec_guild}({exec_channel})')


async def sort_stocks_by_count(all_stocks: list[Stock]) -> list[Stock]:
    return sorted(all_stocks, key=lambda x: x.count, reverse=True)

async def sort_stocks_by_price(all_stocks: list[Stock]) -> list[Stock]:
    return sorted(all_stocks, key=lambda x: x.price, reverse=True)

async def sort_stocks_by_group(all_stocks: list[Stock]) -> list[Stock]:
    return sorted(all_stocks, key=lambda x: x.group)


client = Client()
tree = discord.app_commands.CommandTree(client=client)


@tree.command(
    name=locale_str('ping'),
    description=locale_str('Ping the bot.')
)
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(discord.Embed(title='Pong!'), ephemeral=True)


@tree.command(
    name=locale_str('add_stock'),
    description=locale_str('Add a new stock to the stock list.')
)
async def add_stock(interaction: discord.Interaction, group: str, detail: str, price: int):
    db_manager = client.db_manager
    stock = await db_manager.add_stock(Stock(detail=detail, price=price, group=group))
    
    embed = client.embed_manager.get_embed(
        stock.detail,
        stock.count,
        stock.stock_id,
        price=stock.price,
        group=stock.group
    )
    await client.target_channel.send(embed=embed, view=StockManageView(), silent=True)
    await interaction.response.send_message('商品が追加されました', ephemeral=True)


@tree.command(
    name=locale_str('remove_stock'),
    description=locale_str('Remove a stock from the stock list.')
)
async def remove_stock(interaction: discord.Interaction, stock_id: str):
    db_manager = client.db_manager
    await db_manager.remove_stock(stock_id)
    
    await interaction.response.send_message('商品は削除されました', ephemeral=True)


@tree.command(
    name=locale_str('get_all_stocks'),
    description=locale_str('Get all stocks in the stock list.')
)
async def get_all_stocks(interaction: discord.Interaction):
    db_manager = client.db_manager
    all_stocks = await db_manager.get_all_stock()
    
    stock_list = '\n'.join([f'{stock.detail}({stock.price}) - 売上: {stock.count}個' for stock in all_stocks])
    await interaction.response.send_message(stock_list, ephemeral=True)


@tree.command(
    name=locale_str('calc_total_sales'),
    description=locale_str('Calculate total sales.')
)
async def calc_total_sales(interaction: discord.Interaction):
    # すべての商品を取得
    db_manager = client.db_manager
    all_stocks = await db_manager.get_all_stock()

    # 売上を計算
    sales = {}
    for stock in all_stocks:
        sales[f'{stock.group} ({stock.detail})'] = stock.count * stock.price
    
    # 総売上を計算
    total_sales = sum(sales.values())
    sales['total_sales'] = total_sales
    
    # 売上リストを作成
    sales_list = '\n- '.join([f'{key}:\n    - {value}円' for key, value in sales.items() if key != 'total_sales'])
    sales_list += f'\n\n**総売上: __{total_sales}__円**'

    # メッセージを送信
    embed = discord.Embed(
        title='売上一覧',
        description=sales_list,
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(
    name=locale_str('sort_by_count'),
    description=locale_str('Sort stocks by count.')
)
async def sort_by_count(interaction: discord.Interaction):
    # 商品を個数順にソート
    db_manager = client.db_manager
    all_stocks = await db_manager.get_all_stock()
    sorted_stocks = await sort_stocks_by_count(all_stocks)
    
    # メッセージを削除
    async for message in client.target_channel.history(limit=200):
        await message.delete()
        await asyncio.sleep(0.5)
    
    # ソートされた商品を送信
    for stock in sorted_stocks:
        embed = client.embed_manager.get_embed(
            stock.detail,
            stock.count,
            stock.stock_id,
            price=stock.price,
            group=stock.group
        )
        message = await client.target_channel.send(
            embed=embed,
            view=StockManageView(),
            silent=True
        )
        await client.target_channel.send('‎', silent=True)
        await asyncio.sleep(0.5)
    
    await interaction.response.send_message('商品は売上個数順に並べ替えられました', ephemeral=True)


@tree.command(
    name=locale_str('sort_by_price'),
    description=locale_str('Sort stocks by price.')
)
async def sort_by_price(interaction: discord.Interaction):
    # 商品を価格順にソート
    db_manager = client.db_manager
    all_stocks = await db_manager.get_all_stock()
    sorted_stocks = await sort_stocks_by_price(all_stocks)
    
    # メッセージを削除
    async for message in client.target_channel.history(limit=200):
        await message.delete()
        await asyncio.sleep(0.5)
    
    # ソートされた商品を送信
    for stock in sorted_stocks:
        embed = client.embed_manager.get_embed(
            stock.detail,
            stock.count,
            stock.stock_id,
            price=stock.price,
            group=stock.group
        )
        message = await client.target_channel.send(
            embed=embed,
            view=StockManageView(),
            silent=True
        )
        await client.target_channel.send('‎', silent=True)
        await asyncio.sleep(0.5)
    
    await interaction.response.send_message('商品は価格順に並べ替えられました', ephemeral=True)


@tree.command(
    name=locale_str('sort_by_group'),
    description=locale_str('Sort stocks by group.')
)
async def sort_by_group(interaction: discord.Interaction):
    # 商品をグループ順にソート
    db_manager = client.db_manager
    all_stocks = await db_manager.get_all_stock()
    sorted_stocks = await sort_stocks_by_group(all_stocks)
    
    # メッセージを削除
    async for message in client.target_channel.history(limit=200):
        await message.delete()
        await asyncio.sleep(0.5)
    
    # ソートされた商品を送信
    for stock in sorted_stocks:
        embed = client.embed_manager.get_embed(
            stock.detail,
            stock.count,
            stock.stock_id,
            price=stock.price,
            group=stock.group
        )
        message = await client.target_channel.send(
            embed=embed,
            view=StockManageView(),
            silent=True
        )
        await client.target_channel.send('‎', silent=True)
        await asyncio.sleep(0.5)
    
    await interaction.response.send_message('商品はグループ順に並べ替えられました', ephemeral=True)



if __name__ == '__main__':
    client.run(os.getenv('DS_BOT_STOCK_CONTROL_TOKEN'))
