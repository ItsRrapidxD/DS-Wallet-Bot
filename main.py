import os, sys
os.system("pip install discord.py-self")
import discord
from discord.ext import commands
import requests
import json
import config
import colorama
from colorama import Fore

intents = discord.Intents.default()
draxon = commands.Bot(command_prefix="!", intents=intents, self_bot=True)

@draxon.event
async def on_ready():
    os.system('cls' if os.name == 'nt' else 'clear')    
    print(f"""{Fore.RESET}
{Fore.CYAN}Logged In User's Account{Fore.RESET}
{Fore.YELLOW}Username: {draxon.user.name}{Fore.RESET}
{Fore.YELLOW}ID: {draxon.user.id}{Fore.RESET}
""")
    
async def send_transaction(ctx, currency, addy, value):
    try:
        value = float(value.strip('$'))
        message = await ctx.send(f"<a:Loading_blue:1321799199179673610> **Sending {value}$ To :-** {addy}")
        
        # API and currency-specific details
        currency_data = {
            "ltc": {
                "url": "https://api.tatum.io/v3/litecoin/transaction",
                "address": config.LTC_ADDRESS,
                "private_key": config.LTC_PRIVATE_KEY,
                "price_api": "https://api.coingecko.com/api/v3/simple/price?ids=usd&vs_currencies=ltc"
            },
            "eth": {
                "url": "https://api.tatum.io/v3/ethereum/transaction",
                "address": config.ETH_ADDRESS,
                "private_key": config.ETH_PRIVATE_KEY,
                "price_api": "https://api.coingecko.com/api/v3/simple/price?ids=usd&vs_currencies=eth"
            },
            "sol": {
                "url": "https://api.tatum.io/v3/solana/transaction",
                "address": config.SOL_ADDRESS,
                "private_key": config.SOL_PRIVATE_KEY,
                "price_api": "https://api.coingecko.com/api/v3/simple/price?ids=usd&vs_currencies=sol"
            },
            "usdt": {
                "url": "https://api.tatum.io/v3/ethereum/transaction",
                "address": config.USDT_ADDRESS,
                "private_key": config.USDT_PRIVATE_KEY,
                "price_api": "https://api.coingecko.com/api/v3/simple/price?ids=tether&vs_currencies=usd"
            },
        }
        
        if currency not in currency_data:
            await ctx.send(f"Currency `{currency}` is not supported.")
            return

        # Fetch current price
        price_response = requests.get(currency_data[currency]["price_api"])
        price_response.raise_for_status()
        usd_price = list(price_response.json().values())[0]["usd"]
        topay = usd_price * value

        # Prepare payload
        payload = {
            "fromAddress": [
                {
                    "address": currency_data[currency]["address"],
                    "privateKey": currency_data[currency]["private_key"]
                }
            ],
            "to": [
                {
                    "address": addy,
                    "value": round(topay, 8)
                }
            ],
            "fee": "0.00005",
            "changeAddress": currency_data[currency]["address"]
        }
        
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "x-api-key": config.API_KEY
        }

        # Send transaction request
        response = requests.post(currency_data[currency]["url"], json=payload, headers=headers)
        response_data = response.json()

        # Check for success
        if "txId" in response_data:
            await message.edit(content=f'<:draxon_tick:1321005791632687115> **Successfully Sent {value}$ To {addy}**\nTransaction ID: {response_data["txId"]}')
        else:
            await ctx.send(f'<:draxon_cross:1321005898713399317> **Failed to send {currency.upper()} because:** {response_data.get("message", "Unknown error")}')
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

# Commands

@draxon.command(aliases=['h'])
async def help(ctx):
    embed = discord.Embed(
        title="Draxon Wallet Help",
        description="List of available commands",
        color=discord.Color.dark_gray()
    )
    embed.add_field(
        name="`!sendltc <address> <amount>`",
        value="Send LTC to a specified address.",
        inline=False
    )
    embed.add_field(
        name="`!sendeth <address> <amount>`",
        value="Send ETH to a specified address.",
        inline=False
    )
    embed.add_field(
        name="`!sendsol <address> <amount>`",
        value="Send SOL to a specified address.",
        inline=False
    )
    embed.add_field(
        name="`!sendusdt <address> <amount>`",
        value="Send USDT to a specified address.",
        inline=False
    )
    embed.add_field(
        name="`!help` or `!h`",
        value="Show this help message.",
        inline=False
    )
    embed.set_footer(text="Draxon Selfbot - Use responsibly")
    
    await ctx.send(embed=embed)

@draxon.command(aliases=["pay", "sendltc"])
async def sendltc(ctx, addy, value):
    await send_transaction(ctx, "ltc", addy, value)

@draxon.command(aliases=["sendeth"])
async def sendeth(ctx, addy, value):
    await send_transaction(ctx, "eth", addy, value)

@draxon.command(aliases=["sendsol"])
async def sendsol(ctx, addy, value):
    await send_transaction(ctx, "sol", addy, value)

@draxon.command(aliases=["sendusdt"])
async def sendusdt(ctx, addy, value):
    await send_transaction(ctx, "usdt", addy, value)

# Run the bot
draxon.run("config.TOKEN")
