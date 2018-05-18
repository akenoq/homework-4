# -*- coding: utf-8 -*-

import os
import time

import unittest
from os.path import abspath

from selenium.webdriver import DesiredCapabilities, Remote
from tests.pages.mobile.auth_page import AuthPage
from tests.pages.mobile.photo_page import PhotoPage
from tests.pages.mobile.user_add_album_photo_page import UserAddAlbumPhotoPage
from tests.pages.mobile.user_album_edit_page import UserAlbumEditPage
from tests.pages.mobile.user_album_page import UserAlbumPage
from tests.pages.mobile.user_albums_page import UserAlbumsPage
from tests.pages.mobile.user_edit_album_photo_page import UserEditAlbumPhotoPage


class AlbumTest(unittest.TestCase):
    LOGIN = os.environ['LOGIN']
    PASSWORD = os.environ['PASSWORD']

    def setUp(self):
        browser = os.environ.get('BROWSER', 'FIREFOX')

        self.driver = Remote(
            command_executor='http://127.0.0.1:4444/wd/hub',
            desired_capabilities=getattr(DesiredCapabilities, browser).copy()
        )

    def tearDown(self):
        self.driver.quit()

    def auth(self):
        auth_page = AuthPage(self.driver)
        auth_page.open()

        auth_form = auth_page.form
        auth_form.set_login(self.LOGIN)
        auth_form.set_password(self.PASSWORD)
        auth_form.submit()

    def create_album(self, album_name='Test album #{}'.format(time.time())):
        create_album_page = UserAlbumEditPage(self.driver)
        create_album_page.open()

        create_form = create_album_page.form
        create_form.set_name(album_name)
        create_form.submit()

    def like_album(self, album_name):
        albums_page = UserAlbumsPage(self.driver)
        albums_page.open()

        album_item = albums_page.albums_list.find(album_name)
        album_item.like()

    def upload_photo(self, album_id, photo=abspath('tests/photos/test_photo.jpg')):
        add_photo_page = UserAddAlbumPhotoPage(self.driver, album_id)
        add_photo_page.open()
        add_photo_page.form.upload_photo(photo)

    def upload_photo_and_open(self):
        album_page = UserAlbumPage(self.driver)
        album_id = album_page.parse_album_id()

        self.upload_photo(album_id)

        album_page.open()
        photos_list = album_page.photos_list
        photos_list.first.click()

    def make_photo_cover(self):
        photo_page = PhotoPage(self.driver)
        toolbar = photo_page.toolbar
        toolbar.open()
        toolbar.make_cover()
        photo_page.confirmation.yes()

    def test_create_album(self):
        self.auth()

        album_name = 'Created test album #{}'.format(time.time())
        self.create_album(album_name)

        album = UserAlbumPage(self.driver).empty_album
        self.assertEqual(album_name, album.title)

    def test_remove_album(self):
        self.auth()

        album_name = 'Test album #{} for remove'.format(time.time())
        self.create_album(album_name)

        album_page = UserAlbumPage(self.driver)

        toolbar = album_page.toolbar
        toolbar.open()
        toolbar.delete()

        album_page.confirmation_modal.delete()

        albums_list = UserAlbumsPage(self.driver).albums_list
        self.assertFalse(albums_list.includes(album_name))

    def test_rename_album(self):
        self.auth()
        self.create_album()

        album_page = UserAlbumPage(self.driver)

        toolbar = album_page.toolbar
        toolbar.open()
        toolbar.edit()

        album_name = 'Renamed test album #{}'.format(time.time())
        edit_form = UserAlbumEditPage(self.driver).form
        edit_form.set_name(album_name)
        edit_form.submit()

        self.assertEqual(album_name, album_page.empty_album.title)

    def test_like_album(self):
        self.auth()

        album_name = 'Liked test album #{}'.format(time.time())
        self.create_album(album_name)
        self.like_album(album_name)

        albums_page = UserAlbumsPage(self.driver)
        album_item = albums_page.albums_list.find(album_name)
        self.assertEqual(1, album_item.likes_count)

        # Обновлю и еще раз проверю
        self.driver.refresh()
        album_item = albums_page.albums_list.find(album_name)
        self.assertEqual(1, album_item.likes_count)

    def test_cancel_album_like(self):
        self.auth()

        album_name = 'Liked test album #{}'.format(time.time())
        self.create_album(album_name)
        self.like_album(album_name)

        # Дизлайк
        self.like_album(album_name)

        albums_page = UserAlbumsPage(self.driver)
        album_item = albums_page.albums_list.find(album_name)
        self.assertEqual(0, album_item.likes_count)

        # Обновлю и еще раз проверю
        self.driver.refresh()
        album_item = albums_page.albums_list.find(album_name)
        self.assertEqual(0, album_item.likes_count)

    def test_add_photo(self):
        self.auth()
        self.create_album()

        album_page = UserAlbumPage(self.driver)
        album_id = album_page.parse_album_id()

        self.upload_photo(album_id)

        edit_photo = UserEditAlbumPhotoPage(self.driver)
        edit_photo.form.save()
        self.assertEqual(1, album_page.photos_list.count)

    def test_add_photo_with_description(self):
        self.auth()
        self.create_album()

        album_page = UserAlbumPage(self.driver)
        album_id = album_page.parse_album_id()

        self.upload_photo(album_id)

        edit_photo = UserEditAlbumPhotoPage(self.driver).form
        description = 'Photo description.'
        edit_photo.set_description(description)
        edit_photo.save()

        photos_list = album_page.photos_list
        self.assertEqual(1, photos_list.count)
        photos_list.first.click()
        photo = PhotoPage(self.driver).photo
        self.assertEqual(description, photo.description)

    def test_like_photo(self):
        self.auth()
        self.create_album()
        self.upload_photo_and_open()

        photo = PhotoPage(self.driver).photo
        photo.like()
        self.assertEqual(1, photo.likes_count)

        self.driver.refresh()
        self.assertEqual(1, photo.likes_count)

    def test_cancel_photo_like(self):
        self.auth()
        self.create_album()
        self.upload_photo_and_open()

        photo = PhotoPage(self.driver).photo
        photo.like()
        self.driver.refresh()

        # Отмена лайка
        photo.cancel_like()
        self.assertEqual(0, photo.likes_count)

        self.driver.refresh()
        self.assertEqual(0, photo.likes_count)

    def test_make_photo_album_cover(self):
        self.auth()
        self.create_album()

        album_page = UserAlbumPage(self.driver)
        album_id = album_page.parse_album_id()

        self.upload_photo(album_id, abspath('tests/photos/test_photo.jpg'))
        self.upload_photo(album_id, abspath('tests/photos/test_photo2.jpeg'))

        album_page.open()
        photos_list = album_page.photos_list

        # Делаю первое фото обложкой
        first_photo_item = photos_list.get(0)
        first_photo_id = first_photo_item.image_id

        first_photo_item.click()
        self.make_photo_cover()

        album_page.open()
        self.assertEqual(first_photo_id, album_page.album_header.cover_id)

        # Делаю второе фото обложкой
        second_photo_item = photos_list.get(1)
        second_photo_id = second_photo_item.image_id

        second_photo_item.click()
        self.make_photo_cover()

        album_page.open()
        self.assertEqual(second_photo_id, album_page.album_header.cover_id)