import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timezone
import aiosqlite
from database import DB_PATH


class TodayCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="today", description="See everything you've logged today")
    async def today(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        today_start = datetime.now(timezone.utc).replace(
            hour=0, minute= 0, second=0, microsecond=0
        ).isoformat()

        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute(
                "SELECT id, description, calories FROM entries WHERE user_id = ? AND created_at >= ? ORDER BY id ASC",
                (user_id, today_start)
            )
            rows = await cursor.fetchall()

            goal_cursor = await db.execute(
                "SELECT daily_calories, mode from goals WHERE user_id = ?", (user_id,)
            )
            goal_row = await goal_cursor.fetchone()
        
        if not rows:
            await interaction.response.send_message("Nothing logged today yet")
            return

        message = "\n".join(f"{i}. {row[1]} (~{row [2]} kcal)" for i, row in enumerate(rows, start=1))
        total_calories = sum(row[2] or 0 for row in rows)
        message += f"\n\nTotal: ~{total_calories} kcal"

        if goal_row:
            target, mode = goal_row
            if mode == "daily":
                message += f"\nDaily goal: {target} kcal ({total_calories - target:+d} vs goal)"
            else:
                message += f"\nWeekly goal: {target} kcal"

        await interaction.response.send_message(f"Today's log:\n{message}")

async def setup(bot):
    await bot.add_cog(TodayCog(bot))


    