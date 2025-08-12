# main.py
import discord
from discord.ext import tasks
import time

# Import the functions we wrote in our other files.
from scraper import get_product_info
from database import initialize_db, save_price, get_lowest_price

# --- CONFIGURATION ---
# PASTE THE URL OF THE DARAZ PRODUCT YOU WANT TO TRACK HERE
PRODUCT_URL = "https://www.daraz.com.np/products/soundcore-q11i-wireless-over-ear-bluetooth-headphones-by-anker-deep-bass-60h-playtime-hi-res-audio-detachable-ear-cushions-multipoint-connection-i216841838-s1341505674.html?c=&channelLpJumpArgs=&clickTrackInfo=query%253Aheadphones%253Bnid%253A216841838%253Bsrc%253ALazadaMainSrp%253Brn%253A5faf43c8b4045a4faa11de1cc4067f62%253Bregion%253Anp%253Bsku%253A216841838_NP%253Bprice%253A4799%253Bclient%253Adesktop%253Bsupplier_id%253A1009556%253Bbiz_source%253Ahttps%253A%252F%252Fwww.daraz.com.np%252F%253Bslot%253A13%253Butlog_bucket_id%253A470687%253Basc_category_id%253A156%253Bitem_id%253A216841838%253Bsku_id%253A1341505674%253Bshop_id%253A19374%253BtemplateInfo%253A-1_A3_C%25231103_L%2523&freeshipping=0&fs_ab=1&fuse_fs=&lang=en&location=Bagmati%20Province&price=4799&priceCompare=skuId%3A1341505674%3Bsource%3Alazada-search-voucher%3Bsn%3A5faf43c8b4045a4faa11de1cc4067f62%3BoriginPrice%3A479900%3BdisplayPrice%3A479900%3BsinglePromotionId%3A50000017722045%3BsingleToolCode%3AflashSale%3BvoucherPricePlugin%3A0%3Btimestamp%3A1754966971962&ratingscore=4.487804878048781&request_id=5faf43c8b4045a4faa11de1cc4067f62&review=41&sale=192&search=1&source=search&spm=a2a0e.searchlist.list.13&stock=1" 

# PASTE YOUR DISCORD BOT'S SECRET TOKEN HERE
DISCORD_BOT_TOKEN = "DISCORD_BOT_TOKEN"

# PASTE THE CHANNEL ID WHERE YOU WANT TO RECEIVE ALERTS HERE
# This must be an integer, not a string in quotes.
DISCORD_CHANNEL_ID =1404136995847929938
# ---------------------


# Setup the connection to Discord
intents = discord.Intents.default()
client = discord.Client(intents=intents)


async def send_discord_alert(message):
    """Sends a message to the specified Discord channel."""
    try:
        # Get the channel object from the client.
        channel = client.get_channel(DISCORD_CHANNEL_ID)
        if channel:
            await channel.send(message)
            print("Discord alert sent successfully.")
        else:
            print(f"Error: Could not find channel with ID {DISCORD_CHANNEL_ID}. Make sure the ID is correct and the bot is in the server.")
    except Exception as e:
        print(f"An error occurred while sending Discord alert: {e}")


# The @tasks.loop decorator makes this function run automatically on a schedule.
# You can change the interval to `minutes=X` or `seconds=X` for testing.
@tasks.loop(hours=4)
async def check_price_task():
    """
    This is the main job. It scrapes the price, checks against the database,
    and sends an alert if it's a new low.
    """
    print("---------------------------------")
    print("Running scheduled price check...")
    
    # 1. Get current product info from the website
    title, current_price = get_product_info(PRODUCT_URL)
    
    # 2. Check if scraping was successful
    if title and title != "Title Not Found" and current_price > 0:
        print(f"Successfully scraped '{title}'. Current price: Rs. {current_price}")
        
        # 3. Get the lowest price we've ever recorded from our database
        lowest_price = get_lowest_price(title)
        
        # 4. Compare the current price to the lowest recorded price
        # The first time we check, lowest_price will be infinity, so this will always be true.
        if current_price < lowest_price:
            print(f"🚨 NEW LOWEST PRICE! It's now Rs. {current_price} (was Rs. {lowest_price})")
            message = (
                f"🚨 **Price Drop Alert!** 🚨\n\n"
                f"**{title}** is now at its lowest recorded price: **Rs. {current_price}**!\n\n"
                f"Buy it here: {PRODUCT_URL}"
            )
            # Send the alert to Discord
            await send_discord_alert(message)
        else:
            print(f"Price is not the lowest. Current: Rs. {current_price}, Lowest ever: Rs. {lowest_price}")
            
        # 5. Save the current price to the database to build our history
        save_price(title, current_price)
    else:
        print("Could not retrieve valid product information. Skipping this check.")
    print("---------------------------------")


# This event runs once when the bot successfully connects to Discord.
@client.event
async def on_ready():
    """Event that runs when the Discord bot is connected and ready."""
    print(f'Logged in as {client.user} ({client.user.id})')
    # Start the scheduled task loop.
    check_price_task.start()

# --- Main Execution Block ---
if __name__ == "__main__":
    # Before starting the bot, initialize the database.
    # This creates the 'price_tracker.db' file and the 'prices' table if they don't exist.
    initialize_db()
    
    # Check if the configuration variables have been changed from their default values.
    if PRODUCT_URL == "YOUR_PRODUCT_URL_HERE" or DISCORD_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE" or DISCORD_CHANNEL_ID == 0:
        print("!!! IMPORTANT !!!")
        print("Please open main.py and fill in your PRODUCT_URL, DISCORD_BOT_TOKEN, and DISCORD_CHANNEL_ID.")
    else:
        print("Starting bot...")
        # This command starts the bot and keeps it running.
        client.run(DISCORD_BOT_TOKEN)