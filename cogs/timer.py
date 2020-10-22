from discord.ext import commands
import os
import re
import math
import time
import asyncio
import logging


class Timer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.timers = {}
        print("Timer initialized.")

    async def notify(self, msg):
        server_id = os.environ.get('DEPLOY_NOTIFY', None)
        if server_id:
            await self.bot.get_guild(int(server_id)).text_channels[0].send(msg)

    async def say(self, ctx, message):
        logging.info(message)
        await ctx.send(message)

    def timer_id(self, ctx):
        return ctx.guild.id

    def parse_rest_time(self, timestr):
        result = re.match(r'([\d\.]+)\s*(m(in)?)?', timestr)
        return int(result[1])

    def next_minute(self, current_minute):
        n = 0
        if (current_minute > 10):
            n = math.floor((current_minute - 1) / 10) * 10
        elif (current_minute > 5):
            n = 5
        elif (current_minute > 3):
            n = 3
        else:
            n = current_minute - 1
        return n

    def timer_stop(self, tid):
        self.timers[tid].close()
        del self.timers[tid]

    def timer_exists(self, tid):
        return tid in self.timers

    def set_timer(self, tid, coroutine):
        self.timers[tid] = coroutine

    def get_timer(self, tid):
        return self.timers[tid]

    def delete_timer(self, tid):
        del self.timers[tid]

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def timer(self, ctx, arg):
        await self.notify("timer")
        tid = self.timer_id(ctx)

        if arg == "stop":
            self.timer_stop(tid)
            await self.say(ctx, "タイマーを停止しました")
        else:
            if self.timer_exists(tid):
                await self.say(ctx, "すでにスタートしています")
            else:
                minute = self.parse_rest_time(arg)
                target_time = time.time() + minute * 60

                nm = self.next_minute(minute)
                await self.say(ctx, "タイマースタート")
                while True:
                    self.set_timer(tid, asyncio.sleep(
                        target_time - time.time() - nm * 60))
                    await self.get_timer(tid)
                    if nm > 0:
                        msg = f"@here 残り{nm}分です!"
                        await self.say(ctx, msg)
                        nm = self.next_minute(nm)
                    else:
                        await self.say(ctx, "@here タイマー終了!")
                        await ctx.send("...時間です", tts=True)
                        self.delete_timer(tid)
                        break

    @commands.command()
    @commands.is_owner()
    async def timer_count(self, ctx):
        print(len(self.timers))


def setup(bot):
    bot.add_cog(Timer(bot))
