from tweetcaptureplus import TweetCapturePlus
import asyncio

tweet = TweetCapturePlus()
asyncio.run(
    tweet.screenshot(
        "https://x.com/elonmusk/status/1519480761749016577",
        "night_mode_default.png",
        night_mode=0,
    )
)
asyncio.run(
    tweet.screenshot(
        "https://x.com/elonmusk/status/1519480761749016577",
        "night_mode_dim.png",
        night_mode=1,
    )
)
asyncio.run(
    tweet.screenshot(
        "https://x.com/elonmusk/status/1519480761749016577",
        "night_mode_lights_out.png",
        night_mode=2,
    )
)
