import os
import logging

bot = None

async def notify(msg):
    server_id = os.environ.get('DEPLOY_NOTIFY', None)
    print(server_id)
    print(bot)
    if server_id:
        await bot.get_guild(int(server_id)).text_channels[0].send(msg)

async def say(ctx, message):
    logging.info(message)
    await ctx.send(message)
