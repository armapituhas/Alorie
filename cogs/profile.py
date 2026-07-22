import discord
from discord.ext import commands
from discord import app_commands
import aiosqlite
from database import DB_PATH

ACTIVITY_MULTIPLIERS = {
    "rarely": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
}


class ProfileCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    
    @app_commands.command(name="calcgoal", description="Estimate your daily calorie needs")
    @app_commands.describe(
        weight_kg="Your weight in kilograms",
        height_cm="Your height in centimeters",
        age="Your age",
        sex="Used for the calorie formula",
        activity="How active you are day-to-day",
        goal="Do you want to maintain, lose, or gain weight?"
    )
    @app_commands.choices(sex=[
        app_commands.Choice(name="Male", value="male"),
        app_commands.Choice(name="Female", value="female"),
    ])
    @app_commands.choices(activity=[
        app_commands.Choice(name="Rarely (little no to exercise)", value="rarely"),
        app_commands.Choice(name="Light (exercise 1-3 days/week)", value="light"),
        app_commands.Choice(name="Moderate (exercise 3-5 days/week)", value="moderate"),
        app_commands.Choice(name="Active (exercise 6-7 days/week)", value="active"),
        app_commands.Choice(name="Very active (hard exercise + physical job)", value="very_active"),
    ])
    @app_commands.choices(goal=[
        app_commands.Choice(name="Maintain weight", value="maintain"),
        app_commands.Choice(name="Lose weight", value="lose"),
        app_commands.Choice(name="Gain weight", value="gain"),
    ])
    async def calcgoal(self, interaction: discord.Interaction, weight_kg: float, height_cm: float,
                       age: int, sex: app_commands.Choice[str], activity: app_commands.Choice[str],
                       goal: app_commands.Choice[str]):
        if sex.value == "male":
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
        else:
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

        tdee = bmr * ACTIVITY_MULTIPLIERS[activity.value]

        if goal.value == "lose":
            target = tdee - 650
        elif goal.value == "gain":
            target = tdee + 500
        else:
            target = tdee

        target = round(target)

        user_id = str(interaction.user.id)
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("""
            INSERT INTO goals (user_id, daily_calories, mode)
            VALUES (?, ?, 'daily')
            ON CONFLICT(user_id) DO UPDATE SET daily_calories = excluded.daily_calories, mode = 'daily'
            """, (user_id, target))
            await db.commit()

        await interaction.response.send_message(
            f"Estimated maintenance calories: ~{round(tdee)} kcal/day\n"
            f"Your goal ({goal.name.lower()}): ~{target} kcal/day\n\n"
            f"This has been set as your daily goal - check anytime with '/today' .\n"
            f"_Note: this is a rough estimate based on standard formulas, not personalized medical advice._"
        
        )


async def setup(bot):
    await bot.add_cog(ProfileCog(bot))