"""
An example of receiving new mails of all emails in (near) realtime. There can still be a big delay of around 10-30 seconds, most of that time is out of our control
"""

from autolook_api import AlApiClient, Error, l
from autolook_api import alapi
import asyncio
import dotenv
import os
import time

from autolook_api.error import TimedOutError

async def main():
    dotenv.load_dotenv()

    alacctoken = os.getenv("ALACCTOKEN")

    alcli = AlApiClient(alacctoken, debug=False)
    
    try:
        await alcli.start()

        balance = await alcli.get_balance()
        print(f"Balance:", balance)
        if balance <= 0:
            l().error("Balance is zero, can't continue!")
            return
        
        api_info = await alcli.get_api_info()
        print(f"Stock domains:", api_info.stock_domains)
        
        # Buy or set any owned email address to realtime
        email = await alcli.buy_email("outlook.com")
        l().info(f"Bought new email: '{email}'")

        l().info(f"Setting email: '{email}' to realtime")
        await alcli.set_email_states(email, realtime=True)
        
        # If not needed anymore, can disable realtime like this:
        # await alcli.set_email_states(email, realtime=False)
        
        l().info(f"Waiting till a new email gets received (timeout 600 seconds)")
        
        time_start = time.perf_counter()
        new_mails = None
        try:
            new_mails = await alcli.get_all_new_mails_loop(
                timeout_secs=600, autobuy_locked=True, no_body_raw=True, parse_links=True,
            )
            l().debug(f"Found {len(new_mails)} new mails after: {time.perf_counter() - time_start}")

            await alcli.set_mails_states([mail["almailid"] for (_, mail) in new_mails], read=True)
            
            for (email, mail) in new_mails:
                # email is the email address that received the mail
                l().debug(f"- Mail NEW: ({email}) {mail.__str__()}")
        except TimedOutError as e:
            l().debug(f"Did not find any new mails after: {e.after_seconds} seconds")

        print("---\nDone")
        
    except Error as e:
        l().error(f"{e}", exc_info=True)
    except Exception as e:
        l().error(f"Unexpected: {e}", exc_info=True)
    except KeyboardInterrupt as e:
        l().info("User signaled shutdown, exiting...")
    finally:
        await alcli.close()


if __name__ == "__main__":
    asyncio.run(main())
