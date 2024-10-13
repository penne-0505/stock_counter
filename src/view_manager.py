import discord
import logging

from utils import (
    INFO,
    Stock,
)


class IncreaseButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="増やす",
            emoji="➕",
            style=discord.ButtonStyle.primary,
        )

    async def callback(self, interaction: discord.Interaction):
        # db上の値を増やす
        stock_id = interaction.message.embeds[0].footer.text
        db_manager = interaction.client.db_manager
        result = await db_manager.increment_stock(Stock(stock_id=stock_id, count=1))
        increased_amount = result.count if isinstance(Stock, result) else None

        # embedを作成して更新
        embed = interaction.message.embeds[0]
        embed.description = f"個数: **{increased_amount}**個\n売上: **{increased_amount * result.price}**円"
        await interaction.response.edit_message(embed=embed)

        # ログを出力
        logging.info(
            INFO
            + f"{result.groupe} ({result.detail}) was increased by {interaction.user.name}."
        )


class DecreaseButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="減らす",
            emoji="➖",
            style=discord.ButtonStyle.secondary,
        )

    async def callback(self, interaction: discord.Interaction):
        # db上の値を減らす
        stock_id = interaction.message.embeds[0].footer.text
        db_manager = interaction.client.db_manager
        result = await db_manager.decrease_stock(Stock(stock_id=stock_id, count=1))
        decreased_amount = result.count if isinstance(Stock, result) else None

        # embedを作成して更新
        embed = interaction.message.embeds[0]
        embed.description = f"個数: **{decreased_amount}**個\n売上: **{decreased_amount * result.price}**円"
        await interaction.response.edit_message(embed=embed)

        # ログを出力
        logging.info(
            INFO
            + f"{result.groupe} ({result.detail}) was decreased by {interaction.user.name}."
        )


class StockManageView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(IncreaseButton())
        self.add_item(DecreaseButton())
