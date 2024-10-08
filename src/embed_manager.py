import discord

class EmbedManager:
    def __init__(self):
        pass

    def get_embed(self, detail: str, count: int, id: str, price: int, group: str) -> discord.Embed:
        embed = discord.Embed(
            title=detail if not price else f'{group}（{detail}） -  ¥{price}',
            description=f'個数: **{count}**個\n売上: **{count * price}**円',
            color=discord.Color.blurple()
        )
        
        embed.set_footer(text=id)
        
        return embed
