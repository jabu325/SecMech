import asyncio
import os
import threading
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
import firebase_admin
from firebase_admin import credentials, db

# ==========================
# 🔧 CONFIGURATION & INITIALIZATION
# ==========================
# Global variables for the listener thread to communicate with the main async thread
global_application = None
global_loop = None 

# ⚠️ Using hardcoded token for immediate running, but environment variable is safer!
BOT_TOKEN = "8452170301:AAFU6SY6oUXuW6z5VTSWozEkR1CwAR-q3V8"
FIREBASE_URL = os.environ.get("FIREBASE_URL", "https://lightbulb-ef4f6-default-rtdb.firebaseio.com/")
CRED_PATH = os.environ.get("CRED_PATH", "firebase_service_key.json") 

try:
    cred = credentials.Certificate(CRED_PATH)
    firebase_admin.initialize_app(cred, {"databaseURL": FIREBASE_URL})
except FileNotFoundError:
    print(f"Error: Firebase credential file not found at '{CRED_PATH}'. Please check your path.")
    exit(1)


# ==========================
# 🤖 HANDLERS HELPERS
# ==========================

def get_subscription_keyboard():
    """Generates the subscription InlineKeyboardMarkup."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Intrusion (IR)", callback_data="filter_IR_ONLY"),
            InlineKeyboardButton("Motion (PIR)", callback_data="filter_PIR_ONLY")
        ],
        [
            InlineKeyboardButton("Both (IR & PIR)", callback_data="filter_ALL")
        ],
        # INTEGRATION: Restart/Start Over Button
        [
            InlineKeyboardButton("◀️ Start Over", callback_data="cmd_subscribe") 
        ]
    ])


# ==========================
# 🤖 HANDLERS
# ==========================

# Handler for /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text(
            "👋 Hello! I'm your Smart Security Bot.\n"
            "I’ll notify you when motion is detected.\n"
            "Use /subscribe to choose your alert preferences. 🚨"
        )

# Handler for /subscribe command (Presents buttons)
async def subscribe_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    reply_markup = get_subscription_keyboard()

    await update.message.reply_text(
        "🔔 Select which types of events you want to be notified about:",
        reply_markup=reply_markup
    )


# Handler for button presses (Callback Queries)
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = str(query.message.chat_id)
    data = query.data
    
    # Check if the button pressed is a filter button
    if data.startswith("filter_"):
        
        filter_setting = data.split("_", 1)[1]
        
        # 💾 Store the user's preference in Firebase
        user_ref = db.reference(f"/user_profiles/{chat_id}")
        user_ref.update({
            "subscribed": True,
            "filter": filter_setting
        })
        
        # Determine confirmation message
        if filter_setting == "IR_ONLY":
            msg = "✅ You are now subscribed to **Intrusion (IR)** alerts only!"
        elif filter_setting == "PIR_ONLY":
            msg = "✅ You are now subscribed to **Motion (PIR)** alerts only!"
        else:
            msg = "✅ You are now subscribed to **ALL** Intrusion and Motion alerts!"
            
        # Edit the original message to show the final choice and REMOVE BUTTONS
        await query.edit_message_text(text=msg, parse_mode='Markdown', reply_markup=None)
        
    # INTEGRATION: Logic for the "Start Over" button
    elif data == "cmd_subscribe":
        await query.edit_message_text(
            "🔔 Please select your alert preference again:",
            reply_markup=get_subscription_keyboard() # Re-show the full keyboard
        )


# ==========================
# 👂 FIREBASE LISTENER LOGIC
# ==========================

def format_intrusion_message(data):
    """Formats the data dictionary and determines the sensor type."""
    sensor = data.get("sensor", "Unknown")
    state = data.get("state", 0)
    # timestamp is removed from message format for brevity, but could be added back
    device = data.get("device", "")

    state_str = "TRIGGERED" if state else "IDLE"
    msg = (
        f"🚨 Intrusion Detected!\n"
        f"Device: {device}\n"
        f"Sensor: {sensor}\n"
        f"State: {state_str}\n"
    )
    # Returns message and the simplified sensor type ("IR" or "PIR") for filtering
    return msg, sensor.split('(')[0].strip().upper() 


def intrusion_event_handler(event):
    """
    Called by Firebase SDK instantly when data changes. Runs in a separate thread.
    """
    if event.event_type == 'put' and event.path == '/':
        return

    if not global_application or not global_loop:
        return

    try:
        new_entry_data = event.data
        if not isinstance(new_entry_data, dict):
             return
             
        msg, event_sensor_type = format_intrusion_message(new_entry_data)
        
        # 1. Get the list of all user profiles
        profiles_ref = db.reference("/user_profiles")
        user_profiles = profiles_ref.get()
        
        if not user_profiles:
            return

        # 2. Iterate through profiles and check filters
        for chat_id_str, profile in user_profiles.items():
            chat_id = int(chat_id_str)
            
            user_filter = profile.get("filter", "ALL") 
            is_subscribed = profile.get("subscribed", False)
            
            if not is_subscribed:
                continue

            # Check if the event should be sent based on the user's filter setting
            send_alert = False
            if user_filter == "ALL":
                send_alert = True
            elif user_filter == "IR_ONLY" and event_sensor_type == "IR":
                send_alert = True
            elif user_filter == "PIR_ONLY" and event_sensor_type == "PIR":
                send_alert = True

            if send_alert:
                # Use run_coroutine_threadsafe to safely schedule the async function
                coro = global_application.bot.send_message(chat_id=chat_id, text=msg, parse_mode='Markdown')
                
                try:
                    asyncio.run_coroutine_threadsafe(coro, global_loop)
                except Exception as loop_e:
                    print(f"Error submitting message task to loop for chat {chat_id}: {loop_e}")

    except Exception as e:
        print(f"Error processing Firebase event: {e}")


def start_firebase_listener(app_instance):
    """Starts the synchronous Firebase listener in a separate thread."""
    ref = db.reference("/intrusions")
    ref.listen(intrusion_event_handler) 
    print("Firebase listener started (non-blocking).")


# ==========================
# MAIN
# ==========================
def main():
    
    async def post_init(_app):
        global global_application, global_loop
        
        global_application = _app
        global_loop = asyncio.get_running_loop() 
        
        thread = threading.Thread(
            target=start_firebase_listener, 
            args=(_app,), 
            daemon=True
        )
        thread.start()
        print("Telegram bot initialized and Firebase listener thread started.")

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init) 
        .build()
    )
    
    # HANDLERS
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("subscribe", subscribe_prompt))
    application.add_handler(CallbackQueryHandler(button_callback))

    application.run_polling(poll_interval=1)

if __name__ == "__main__":
    main()