import os

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from tests.pages.primary.component import Component
from tests.pages.primary.page import Page


class PhotoPage(Page):
    def goto_photo_comment(self):
        self.redirect('kadyr.akhmatov/pphotos/839046221380')
        progress_roll = '.photo-layer_process'
        WebDriverWait(self.driver, 30, 0.1).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, progress_roll))
        )
        self.driver.execute_script("arguments[0].scrollIntoView(true);", self.driver.find_element_by_css_selector(
            '.photo-layer_bottom_block_w'))

    @property
    def comments(self):
        return Comments(self.driver)

    @property
    def input_comment(self):
        return InputComment(self.driver)


class Comments(Component):
    COMMENT = '//div[contains(@class, "comments_text")]'

    COMMENT_LIST_CSS_lastchild = '.comments_lst_cnt > div[id^="hook_Block"]:last-child'
    COMMENT_BOX_CSS_last = '.comments_lst_cnt > div[id^="hook_Block"]:last-child div[class="comments_i"]'
    DELETE_BTN_last = COMMENT_LIST_CSS_lastchild + ' a.comments_remove'

    DELETE_BTN = '//a[contains(@class, "comments_remove")]'
    UNDELETE_BTN = '//a[contains(@class, "delete-stub_cancel")]'

    COMMENT_SMILE = COMMENT + '/*/img'
    COMMENT_STICKER = COMMENT + '/*/div[contains(@class, "__sticker")]'

    VIDEO_CONT_CSS = 'div[data-l="t,play"]'
    VIDEO_LINK_CSS = 'a[uid = "stopEvents"]'

    ANS_MARKER_CSS = '.comments_lst_cnt > div[id^="hook_Block"]:last-child .vaTop'

    NUM_COMMENTS = ".photo-layer_bottom_block_w .widget.__no-o a[data-module='CommentWidgets'] .widget_count.js-count"

    DELETED_MARKER_CSS = '.comments_i.__deleted'

    def get_newest_comment_text(self):
        comment_text_field = self.driver.find_elements_by_xpath(self.COMMENT)[-1]
        return comment_text_field.text

    def get_newest_comment_smile(self):
        comment_field = self.driver.find_elements_by_xpath(self.COMMENT_SMILE)[-1]
        return comment_field.get_attribute("class").split(' ')

    def get_newest_comment_sticker(self):
        comment_field = self.driver.find_elements_by_xpath(self.COMMENT_STICKER)[-1]
        data_code = comment_field.get_attribute("data-code")
        return data_code

    def get_newest_comment(self):
        elem = WebDriverWait(self.driver, 30, 0.1).until(
            lambda d: d.find_element_by_css_selector(self.COMMENT_LIST_CSS_lastchild)
        )
        return elem

    def get_newest_comment_photo_attach_num(self):
        el = self.get_newest_comment()
        el = el.find_elements_by_css_selector('.collage_i')
        return len(el)

    def get_newest_comment_video_attach_num(self):
        el = self.get_newest_comment()
        el = el.find_elements_by_css_selector(self.VIDEO_CONT_CSS)
        return len(el)

    def get_newest_comment_video_attach_url(self):
        el = self.get_newest_comment()
        el = el.find_element_by_css_selector(self.VIDEO_LINK_CSS)
        return el.text

    def input_text(self, element, text):
        WebDriverWait(self.driver, 30, 0.1).until(
            lambda d: d.find_element_by_xpath(element)
        ).send_keys(text)

    def click_answer(self):
        self.driver.execute_script(
            'document.querySelectorAll(\'.comments_reply.al.tdn.fade-on-hover\')[0].className = "comments_reply al tdn"')
        new_selector_ans_btn = '.comments_reply.al.tdn'
        WebDriverWait(self.driver, 20, 0.1).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, new_selector_ans_btn))
        ).click()

    def check_answer(self):
        WebDriverWait(self.driver, 10, 0.1).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, self.ANS_MARKER_CSS))
        )
        marker = self.driver.find_element_by_css_selector(
            ".comments_lst_cnt > div[id^=\"hook_Block\"]:last-child .vaTop").text
        return marker

    def count_comments(self):
        count = int(self.driver.find_element_by_css_selector(self.NUM_COMMENTS).text)
        return count

    def delete_comment(self):
        try:
            self.driver.execute_script(
                'document.querySelectorAll(\'.fade-on-hover.comments_remove.ic10.ic10_close-g\')[0].className = "comments_remove ic10 ic10_close-g"')
            n = self.driver.find_element_by_css_selector(self.NUM_COMMENTS).text
            WebDriverWait(self.driver, 10, 0.1).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '.comments_remove'))
            ).click()
            num_after = str(int(n) - 1)
            WebDriverWait(self.driver, 10, 0.1).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, self.DELETED_MARKER_CSS))
            )
            WebDriverWait(self.driver, 10, 0.1).until(
                EC.text_to_be_present_in_element((By.CSS_SELECTOR, self.NUM_COMMENTS), num_after)
            )
        except NoSuchElementException:
            return 0

    def undelete_comment(self):
        WebDriverWait(self.driver, 20, 0.1).until(
            EC.element_to_be_clickable((By.XPATH, self.UNDELETE_BTN))
        ).click()


class InputComment(Component):
    INPUT = '//div[@name="st.dM"]'
    SUBMIT_BTN = '//div[@class="comments_add-controls"]/button[@data-l="t,submit"]'
    SAVE_BTN = '//button[contains(@class, "comments_add-controls_save")]'

    SMILE_BTN = '//span[contains(@class, "comments_smiles_trigger")]'
    SMILE_TAB = '//a[@data-l="t,smilesTab"]'

    STICKER_TAB = '//a[@data-l="t,stickersTab"]'

    ATTACH_BTN = '//span[contains(@class, "comments_attach_trigger")]'

    NUM_COMMENTS = ".photo-layer_bottom_block_w .widget.__no-o a[data-module='CommentWidgets'] .widget_count.js-count"

    VIDEO_BTN_CSS = 'a[data-l="t,videoLink"]'
    VIDEO_CARD_CSS = '.vid-card_n'

    COUNTER_LIMIT_CSS = '.comments_add-itx .txt-counter'
    COMMENTS_ADD_ERR_CSS = '.comments_add-error'

    def send(self):
        n = self.driver.find_element_by_css_selector(self.NUM_COMMENTS).text

        WebDriverWait(self.driver, 10, 0.1).until(
            EC.element_to_be_clickable((By.XPATH, self.SUBMIT_BTN))
        ).click()

        num_after = str(int(n) + 1)
        try:
            WebDriverWait(self.driver, 10, 0.1).until(
                EC.text_to_be_present_in_element((By.CSS_SELECTOR, self.NUM_COMMENTS), num_after)
            )
        except TimeoutException:
            return 0

    def input_focus(self):
        WebDriverWait(self.driver, 20, 0.1).until(
            EC.element_to_be_clickable((By.XPATH, self.INPUT))
        ).click()

    def input_attach_focus(self):
        self.driver.execute_script("arguments[0].scrollIntoView(true);", self.driver.find_element_by_css_selector(
            '.comments_lst_cnt > div[id^="hook_Block"]:last-child'))

    def input_text(self, text):
        WebDriverWait(self.driver, 30, 0.1).until(
            lambda d: d.find_element_by_xpath(self.INPUT)
        ).send_keys(text)

    def submit(self):
        n = self.driver.find_element_by_css_selector(self.NUM_COMMENTS).text
        WebDriverWait(self.driver, 10, 0.1).until(
            EC.element_to_be_clickable((By.XPATH, self.SAVE_BTN))
        ).click()
        num_after = str(int(n) + 1)
        WebDriverWait(self.driver, 10, 0.1).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, self.NUM_COMMENTS), num_after)
        )

    def go_to_newest_com(self):
        comment_added_msg_css = '.tip.__bot.inverted.tipDiscussion.__active .tip_cnt'
        WebDriverWait(self.driver, 10, 0.1).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, comment_added_msg_css))
        ).click()

    def get_comment_limit_counter(self):
        elem = WebDriverWait(self.driver, 10, 0.1).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, self.COUNTER_LIMIT_CSS))
        )
        return elem.text

    def counter_interact_add(self, current_counter):
        counter_after = str(int(current_counter) - 1)
        self.input_text('1')
        try:
            WebDriverWait(self.driver, 20, 0.1).until(
                EC.text_to_be_present_in_element((By.CSS_SELECTOR, self.COUNTER_LIMIT_CSS), counter_after)
            )
            return 1
        except TimeoutException:
            return 0

    def counter_interact_del(self, current_counter):
        from selenium.webdriver.common.keys import Keys
        counter_after = str(int(current_counter) + 1)
        self.input_text(Keys.BACKSPACE)
        try:
            WebDriverWait(self.driver, 20, 0.1).until(
                EC.text_to_be_present_in_element((By.CSS_SELECTOR, self.COUNTER_LIMIT_CSS), counter_after)
            )
            return 1
        except TimeoutException:
            return 0

    def add_comment_text(self, text):
        self.input_focus()
        self.input_text(text)
        try:
            self.send()
        except TimeoutError:
            return False

    def get_comments_add_err(self):
        elem = WebDriverWait(self.driver, 5, 0.1).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, self.COMMENTS_ADD_ERR_CSS))
        )
        return elem.text

    def insert_text(self, text):
        script_insert_text = 'document.querySelectorAll(\'div[name="st.dM"]\')[0].innerText = "{}"'.format(text[1:])
        self.driver.execute_script(script_insert_text)
        self.input_text('1')
        WebDriverWait(self.driver, 10, 0.1).until(
            EC.text_to_be_present_in_element((By.XPATH, self.INPUT), text)
        )

    def try_add_comment_text(self, text):
        self.input_focus()
        self.insert_text(text)
        try:
            self.send()
        except TimeoutError:
            return False

    def add_answer_text(self, text):
        self.input_text(text)
        self.submit()
        self.go_to_newest_com()

    def click_smile_btn(self):
        WebDriverWait(self.driver, 20, 0.1).until(
            EC.element_to_be_clickable((By.XPATH, self.SMILE_BTN))
        ).click()

    def click_attach_btn(self):
        WebDriverWait(self.driver, 4, 0.1).until(
            EC.element_to_be_clickable((By.XPATH, self.ATTACH_BTN))
        ).click()

    def choose_smile(self, smile_class):
        smile = '//ul[@class="comments_smiles_lst"]/*/img[contains(@class, "' + smile_class + '")]'
        self.click_smile_btn()
        WebDriverWait(self.driver, 10, 0.1).until(
            EC.element_to_be_clickable((By.XPATH, self.SMILE_TAB))
        ).click()
        WebDriverWait(self.driver, 10, 0.1).until(
            EC.element_to_be_clickable((By.XPATH, smile))
        ).click()

    def choose_random_sticker(self):
        self.click_smile_btn()
        WebDriverWait(self.driver, 10, 0.1).until(
            EC.element_to_be_clickable((By.XPATH, self.STICKER_TAB))
        ).click()
        sticker = WebDriverWait(self.driver, 20, 0.1).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '.comments_smiles_cnt .usmile.__sticker'))
        )
        code = sticker.get_attribute("data-code")
        sticker.click()
        return code

    def choose_photo(self):
        self.click_attach_btn()
        script_visualise_input = 'document.querySelector(\'span.comments_attach_trigger input[title="Добавить фото"]\').hidden = false'
        self.driver.execute_script(script_visualise_input)
        PHOTO_PC_INPUT_CSS = 'span.comments_attach_trigger input[title="Добавить фото"]'

        self.driver.find_element_by_css_selector(PHOTO_PC_INPUT_CSS).send_keys(
            os.path.join(os.getcwd(), 'tests/photos/test_photo.jpg'))

    def click_css(self, css):
        WebDriverWait(self.driver, 20, 0.1).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, css))
        ).click()

    def choose_video(self):
        self.click_attach_btn()
        self.click_css(self.VIDEO_BTN_CSS)
        self.click_css(self.VIDEO_CARD_CSS)

    def wait_progress_bar(self):
        progress_bar = '.progress.__bottom.__slim'
        WebDriverWait(self.driver, 20, 0.1).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, progress_bar))
        )

    def wait_img_preview_display(self):
        preview_img = 'div[data-module="AttachPreview"] .attach-photo_img.preview-image'
        WebDriverWait(self.driver, 10, 0.1).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, preview_img))
        )

    def wait_video_preview_display(self):
        preview_video = 'div[data-module="AttachPreview"] .vid-card_img.preview-image'
        WebDriverWait(self.driver, 10, 0.1).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, preview_video))
        )

    def add_comment_smile(self, smile_class):
        self.input_attach_focus()
        self.choose_smile(smile_class)
        self.send()

    def add_comment_sticker(self):
        self.input_attach_focus()
        code = self.choose_random_sticker()
        return code

    def add_one_photo(self):
        self.input_attach_focus()
        self.choose_photo()

    def add_video(self):
        self.input_attach_focus()
        self.choose_video()
