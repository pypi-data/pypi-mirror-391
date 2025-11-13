from asyncio import sleep
from tweetcaptureplus.utils.webdriver import get_driver
from tweetcaptureplus.utils.utils import is_valid_tweet_url, get_tweet_file_name, add_corners
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
from os import remove, environ
from os.path import exists


class TweetCapturePlus:
    driver = None
    driver_path = None
    gui = False
    night_mode = 1
    wait_time = 5
    chrome_opts = []
    lang = None
    test = False
    show_parent_tweets = False
    parent_tweets_limit = 0
    show_mentions_count = 0
    overwrite = False
    radius = 15
    cookies = None

    hide_link_previews = False
    hide_photos = False
    hide_videos = False
    hide_gifs = False
    hide_quotes = False

    __web = 1

    def __init__(
        self,
        night_mode=1,
        test=False,
        show_parent_tweets=False,
        parent_tweets_limit=-1,
        show_mentions_count=0,
        overwrite=True,
        radius=0,
        gui=False,
    ):
        self.set_night_mode(night_mode)
        self.test = test
        self.gui = gui
        self.show_parent_tweets = show_parent_tweets
        self.parent_tweets_limit = parent_tweets_limit
        self.show_mentions_count = show_mentions_count
        self.overwrite = overwrite
        self.radius = radius
        if environ.get("AUTH_TOKEN") != None:
            self.cookies = [{"name": "auth_token", "value": environ.get("AUTH_TOKEN")}]

    async def screenshot(
        self,
        url,
        path=None,
        night_mode=1,
        show_parent_tweets=None,
        parent_tweets_limit=None,
        show_mentions_count=None,
        overwrite=None,
    ):
        self.set_night_mode(night_mode)

        if is_valid_tweet_url(url) is False:
            raise Exception("Invalid tweet url")

        if not isinstance(path, str) or len(path) == 0:
            path = get_tweet_file_name(url)

        if exists(path):
            if (self.overwrite if overwrite is None else overwrite) is False:
                raise Exception("File already exists")
            else:
                remove(path)

        url = is_valid_tweet_url(url)
        if self.lang:
            url += "?lang=" + self.lang

        driver = await get_driver(self.chrome_opts, self.driver_path, self.gui)
        if driver is None:
            raise Exception("webdriver cannot be initialized")
        try:
            driver.get(url)
            driver.add_cookie(
                {
                    "name": "night_mode",
                    "value": str(self.night_mode),
                }
            )
            if self.cookies:
                for cookie in self.cookies:
                    driver.add_cookie(cookie)
            driver.get(url)
            main_tweet_xpath = """//article[@role='article' and @tabindex='-1']"""
            main_tweet_comment_box_xpath = ".//ancestor::button[@data-testid = 'tweetButtonInline']/../../../../../../../../../../.."
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, main_tweet_xpath)))
            try:
                if self.cookies:
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, main_tweet_comment_box_xpath)))
            except:
                pass
            self.__hide_global_items(driver)
            driver.execute_script("!!document.activeElement ? document.activeElement.blur() : 0")
            if self.test is True:
                driver.save_screenshot(f"web{self.__web}.png")
                self.__web += 1
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, main_tweet_xpath)))
            elements, main = self.__get_tweets(
                driver,
                (self.show_parent_tweets if show_parent_tweets is None else show_parent_tweets),
                (self.parent_tweets_limit if parent_tweets_limit is None else parent_tweets_limit),
                (self.show_mentions_count if show_mentions_count is None else show_mentions_count),
            )
            if len(elements) == 0:
                raise Exception("Tweets not found")
            else:
                for i, element in enumerate(elements):
                    self.__hide_media(
                        element,
                        self.hide_link_previews,
                        self.hide_photos,
                        self.hide_videos,
                        self.hide_gifs,
                        self.hide_quotes,
                    )
            self.__increase_container_height(driver)
            if len(elements) == 1:
                driver.execute_script("window.scrollTo(0, 0);")
                x, y, width, height = driver.execute_script(
                    "var rect = arguments[0].getBoundingClientRect(); return [rect.x, rect.y, rect.width, rect.height];",
                    elements[0],
                )
                await sleep(0.1)
                await self.save_long_screenshot(driver, elements[0], path)
                new_im = Image.open(path)
                new_im = add_corners(new_im, self.radius)
                new_im.save(path, quality=100)
                new_im.close()
            else:
                filenames = []
                for element in elements:
                    filename = "tmp_%s_tweetcapture.png" % element.id
                    driver.execute_script("arguments[0].scrollIntoView();", element)
                    x, y, width, height = driver.execute_script(
                        "var rect = arguments[0].getBoundingClientRect(); return [rect.x, rect.y, rect.width, rect.height];",
                        element,
                    )
                    await sleep(0.1)
                    await self.save_long_screenshot(driver, element, filename)
                    filenames.append(filename)
                width = 0
                height = 0
                images = []
                for filename in filenames:
                    im = Image.open(filename)
                    if width == 0:
                        width = im.size[0]
                    height += im.size[1]
                    images.append(im)
                c = (255, 255, 255)
                if self.night_mode == 1:
                    c = (21, 32, 43)
                elif self.night_mode == 2:
                    c = (0, 0, 0)
                new_im = Image.new("RGB", (width, height), c)
                y = 0
                for im in images:
                    new_im.paste(im, (0, y))
                    y += im.size[1]
                    im.close()
                    remove(im.filename)

                new_im = add_corners(new_im, self.radius)
                new_im.save(path, quality=100)
                new_im.close()

            driver.quit()
        except Exception as err:
            driver.quit()
            raise err
        return path

    def set_wait_time(self, time):
        if 1.0 <= time <= 10.0:
            self.wait_time = time

    def get_night_mode(self):
        return self.night_mode

    def set_night_mode(self, night_mode):
        if 0 <= night_mode <= 2:
            self.night_mode = night_mode

    def add_chrome_argument(self, option):
        self.chrome_opts.append(option)

    def set_lang(self, lang):
        self.lang = lang

    def set_chromedriver_path(self, path):
        self.driver_path = path

    def set_cookies(self, cookies):
        if isinstance(cookies, list):
            self.cookies = cookies

    def __hide_global_items(self, driver):
        HIDE_ITEMS_XPATH = [
            "/html/body/div/div/div/div[2]/main/div/div/div/div/div/div[1]",  # Post top bar
            ".//ancestor::button[@data-testid = 'tweetButtonInline']/../../../../../../../../../../..",  # Authenticated, comment box
            "//span[contains(text(), 'Who can reply?')]/../../../../..",  # Who can reply box
            """//a[@data-testid="logged_out_read_replies_pivot"]""",  # Unauthenticated, read replies
            """//div[@data-testid='BottomBar']""",  # Unauthenticated, sign-in bar
        ]
        for item in HIDE_ITEMS_XPATH:
            try:
                element = driver.find_element(By.XPATH, item)
                driver.execute_script(
                    """
                arguments[0].style.display="none";
                """,
                    element,
                )
            except:
                continue

    def hide_all_media(self):
        self.hide_link_previews = True
        self.hide_photos = True
        self.hide_videos = True
        self.hide_gifs = True
        self.hide_quotes = True

    def hide_media(self, link_previews=None, photos=None, videos=None, gifs=None, quotes=None):
        if link_previews is not None:
            self.hide_link_previews = link_previews
        if photos is not None:
            self.hide_photos = photos
        if videos is not None:
            self.hide_videos = videos
        if gifs is not None:
            self.hide_gifs = gifs
        if quotes is not None:
            self.hide_quotes = quotes

    def __hide_media(self, element, link_previews, photo, video, gif, quote):
        LINKPREVIEW_XPATH = ".//ancestor::div[@data-testid = 'card.layoutLarge.media']/ancestor::div[contains(@id, 'id__')][1]"
        MEDIA_XPATH = ".//ancestor::div[@data-testid = 'tweetPhoto']/ancestor::div[contains(@id, 'id__')]/div[1]"
        QUOTE_XPATH = ".//ancestor::div[contains(@class, 'r-desppf')]/ancestor::div[contains(@id, 'id__')][1]"
        media_elements = element.find_elements(By.XPATH, MEDIA_XPATH)
        if link_previews is True:
            link_preview_elements = element.find_elements(By.XPATH, LINKPREVIEW_XPATH)
            for link_preview_element in link_preview_elements:
                element.parent.execute_script(
                    """
                arguments[0].style.display="none";
                """,
                    link_preview_element,
                )
        if quote is True:
            quote_elements = element.find_elements(By.XPATH, QUOTE_XPATH)
            for quote_element in quote_elements:
                element.parent.execute_script(
                    """
                arguments[0].style.display="none";
                """,
                    quote_element,
                )
        if len(media_elements) > 0:
            for el in media_elements:
                if video is True:
                    sel = el.find_elements(By.XPATH, ".//video[contains(@src, 'blob:')]")
                    if len(sel) > 0:
                        element.parent.execute_script(
                            """
                        arguments[0].style.display="none";
                        """,
                            el,
                        )
                        continue
                    sel = el.find_elements(By.XPATH, ".//source[contains(@src, 'blob:')]")
                    if len(sel) > 0:
                        element.parent.execute_script(
                            """
                        arguments[0].style.display="none";
                        """,
                            el,
                        )
                        continue
                if gif is True:
                    sel = el.find_elements(By.XPATH, ".//video[not(contains(@src, 'blob:'))]")
                    if len(sel) > 0:
                        element.parent.execute_script(
                            """
                        arguments[0].style.display="none";
                        """,
                            el,
                        )
                        continue
                if gif is True:
                    sel = el.find_elements(By.XPATH, ".//video[not(contains(@src, 'blob:'))]")
                    if len(sel) > 0:
                        element.parent.execute_script(
                            """
                        arguments[0].style.display="none";
                        """,
                            el,
                        )
                        continue
                if photo is True:
                    sel = el.find_elements(By.XPATH, ".//div[contains(@data-testid, 'videoPlayer')]")
                    if len(sel) == 0:
                        element.parent.execute_script(
                            """
                        arguments[0].style.display="none";
                        """,
                            el,
                        )
                        continue

    # Return: (elements, main_element_index)
    def __get_tweets(self, driver, show_parents, parent_tweets_limit, show_mentions_count):
        els = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "(//ancestor::article)/..")))

        elements = []
        for element in els:
            try:
                if len(element.find_elements(By.XPATH, ".//article[contains(@data-testid, 'tweet')]")) > 0:
                    # sponsored tweet pass
                    if element.find_elements(By.XPATH, ".//span[text()='Ad']"):  # Check for span with value "Ad"
                        continue
                    elements.append(element)
            except:
                continue
        length = len(elements)
        if length > 0:
            if length == 1:
                return elements, 0
            else:
                main_element = -1
                for i, element in enumerate(elements):
                    main_tweet_details = element.find_elements(By.XPATH, ".//div[contains(@class, 'r-1471scf')]")
                    if len(main_tweet_details) == 1:
                        main_element = i
                        break
                if main_element == -1:
                    return [], -1
                else:
                    r = main_element + 1
                    r2 = r + show_mentions_count
                    s1 = 0
                    if parent_tweets_limit > 0 and len(elements[s1:main_element]) > parent_tweets_limit:
                        s1 = main_element - parent_tweets_limit
                    if show_parents and show_mentions_count > 0:
                        if len(elements[r:]) > show_mentions_count:
                            return (elements[s1:r] + elements[r:r2]), main_element
                        return elements[s1:], main_element
                    elif show_parents:
                        if main_element == 0:
                            return elements[0:1], 0
                        else:
                            return elements[s1:r], main_element
                    elif show_mentions_count > 0:
                        author_handle = elements[main_element].find_elements(By.TAG_NAME, "span")[3].text
                        f_elements = elements[s1:r] + [el for el in elements[r:] if any(author_handle in span.text for span in el.find_elements(By.TAG_NAME, "span")[5:])]
                        if len(f_elements) > show_mentions_count:
                            return f_elements[s1:r2], main_element
                        return f_elements, main_element
                    else:
                        return elements[main_element:r], 0
        return [], -1

    def set_gui(self, gui):
        self.gui = True if gui is True else False

    def __increase_container_height(self, driver):
        # Wait for the element to be available
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//main[@role='main']")))

        # Get the current min-height value
        current_height = element.value_of_css_property("height")

        # Remove the 'px' suffix and convert the value to an integer
        current_height_value = int(current_height.replace("px", ""))

        # Increase the min-height by 1000px
        new_min_height = current_height_value + 1000

        # override by CSS while keeping the change minimal.
        driver.execute_script("arguments[0].style.setProperty('min-height', '{}px', 'important');".format(new_min_height), element)

        WebDriverWait(driver, getattr(self, "wait_time", 5)).until(lambda d: (lambda v: int(float(v.replace("px", ""))) >= new_min_height if isinstance(v, str) and v.endswith("px") else False)(d.execute_script("return window.getComputedStyle(arguments[0]).getPropertyValue('min-height');", element)))

    async def save_long_screenshot(self, driver, element, path):
        # Get the location and size of the element
        start_y = element.location["y"]
        size = element.size

        # Calculate the total height of the element
        total_height = size["height"]

        # Get the current viewport height
        viewport_height = driver.execute_script("return window.innerHeight")

        # Check if the element's height is longer than the viewport height
        if total_height < viewport_height:
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.TAG_NAME, "body")))
            element.screenshot(path)
            return

        image_list = []
        scroll_height = 200
        for i in range(0, total_height, scroll_height):
            driver.execute_script(f"window.scrollTo(0, {start_y + i});")
            await sleep(0.1)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            element.screenshot("screenshot_{}.png".format(i))
            image = Image.open("screenshot_{}.png".format(i))
            cropped_image = image.crop((0, 0, size["width"], scroll_height))
            cropped_image.save("screenshot_{}.png".format(i))
            image_list.append(Image.open("screenshot_{}.png".format(i)))

        # Stitch the images together
        final_image = Image.new("RGB", (size["width"], total_height))
        y_offset = 0
        for image in image_list:
            # Crop the image to the size of the element
            final_image.paste(image, (0, y_offset))
            y_offset += scroll_height
            image.close()
            remove("screenshot_{}.png".format(y_offset - image.size[1]))

        # Save the final image
        final_image.save(path)
