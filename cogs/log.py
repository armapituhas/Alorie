import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timezone
import aiosqlite
from database import DB_PATH
from nutrition import estimate_nutrition


class LogCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="log", description="Log what you ate by photo")
    @app_commands.describe(
        photo="A photo of your food",
        meal="Breakfast / lunch / dinner / snack",
        description="Extra context (optional)"
    )
    @app_commands.choices(meal=[
        app_commands.Choice(name="Breakfast", value="breakfast"),
        app_commands.Choice(name="Lunch", value="lunch"),
        app_commands.Choice(name="Dinner", value="dinner"),
        app_commands.Choice(name="Snack", value="snack"),
    ])
    async def log(self, interaction: discord.Interaction, photo: discord.Attachment,
                  meal : app_commands.Choice[str], description: str = None):
        await interaction.response.defer()
        user_id = str(interaction.user.id)
        timestamp = datetime.now(timezone.utc).isoformat()

        try:
            image_bytes = await photo.read()
            media_type = photo.content_type or "image/jpeg"
            nutrition = await estimate_nutrition(image_bytes=image_bytes, media_type=media_type, context=description)
        except Exception as e:
            await interaction.followup.send(f"Couldn't estimate that one, try again.*({e})")
            return

        final_description = nutrition.get("description", description or "food")

        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                """INSERT INTO entries (user_id, description, created_at, meal, calories, protein_g, carbs_g, fat_g)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                   (user_id, final_description, timestamp, meal.value,
                   nutrition["calories"], nutrition["protein_g"], nutrition["carbs_g"], nutrition["fat_g"])
            )
            await db.commit()

        await interaction.followup.send(
            f"Logged ({meal.name}): {final_description}\n"
            f"~{nutrition['calories']} kcal | "
            f"P: {nutrition['protein_g']:.0f}g, C: {nutrition['carbs_g']:.0f}g, F: {nutrition['fat_g']:.0f}g"
        )


async def setup(bot):
    await bot.add_cog(LogCog(bot))