from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import requests
import os
from time import sleep
from PIL import Image
from plot_image import make_gift_image, make_sphere_image
import pickle
from requests.packages import urllib3

urllib3.disable_warnings()

FRAME_WIDTH = 4
IMG_WIDTH = 220     # 不含边框
gift_filename = './plot/紫礼物250503.jpg'      # 每次运行前修改
sphere_filename = './plot/宝玉250503.jpg'      # 每次运行前修改


# 修正png大小
def resize_img(filename):
    input_img = Image.open(filename)
    output_img = input_img.resize((IMG_WIDTH, IMG_WIDTH), Image.ANTIALIAS)
    output_img.save(filename)


# 为png文件添加边框
def add_frame(input_fp, output_fp, color='gray', width=FRAME_WIDTH):
    input_img = Image.open(input_fp)
    w, h = input_img.width, input_img.height
    w += 2 * width
    h += 2 * width
    output_img = Image.new('RGBA', (w, h), color)
    output_img.paste(input_img, (width, width))
    output_img.save(output_fp)


def get_soup(url: str, headers: dict):
    req = Request(url=url, headers=headers)
    resp = urlopen(req)
    content = resp.read()
    soup = BeautifulSoup(content, 'html.parser')
    return soup


if __name__ == '__main__':

    my_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}
    url_prefix = 'https://mahjongsoul.club'
    type_dict = {'常設': 0, '期間限定': 1}

    # 读取现有人物信息字典
    gift_dict_filename = 'gift_dict.pkl'
    sphere_dict_filename = 'sphere_dict.pkl'
    with open(gift_dict_filename, 'rb') as f:
        gift_dict = pickle.load(f)
    with open(sphere_dict_filename, 'rb') as f:
        sphere_dict = pickle.load(f)

    current_char = []
    for char_type in ['female', 'male']:
        for gift in gift_dict[char_type]:
            for i in range(2):
                current_char.extend(gift_dict[char_type][gift][i])

    # 从雀魂db获取男性雀士list和女性雀士list
    for sex in ['female', 'male']:
        char_list_url = url_prefix + '/characters/list/' + sex
        char_list_soup = get_soup(char_list_url, my_headers)
        char_tag = char_list_soup.find('div', class_='view-content')
        for char_name_tag, char_type_tag in zip(
                char_tag.find_all('td', class_='views-field views-field-title'),
                char_tag.find_all('td', class_='views-field views-field-field-availability-er')):

            if char_type_tag.find('a'):     # 排除卫星角色
                char_name = str(char_name_tag.find('a').contents[0])
                char_type = str(char_type_tag.find('a').contents[0])
                # 补充新雀士信息和大头照
                if char_name not in current_char:
                    print(f'新{char_type}雀士: {char_name}')
                    char_href = char_name_tag.find('a').get('href')
                    char_url = url_prefix + char_href
                    char_page_soup = get_soup(char_url, my_headers)
                    # 契约信息
                    item_list = []
                    char_basic_info_field = char_page_soup.find('div', id='block-views-bonditem-block-14')
                    char_basic_info_list = char_basic_info_field.find('div', class_='first last odd').find_all('div')
                    for tag in char_basic_info_list:
                        tag_name = tag.get_text().strip().split(':')[0]
                        if tag_name == 'Bond':
                            item_list = [str(item_tag.contents[0]) for item_tag in tag.find_all('a')]
                            break
                    assert len(item_list) == 5      # 检验是否定位到bond字段
                    sphere_1, sphere_2, gift = item_list[0], item_list[1], item_list[2]
                    gift = 'ワイングラス' if gift == 'グラス' else gift      # 雀魂db命名变化
                    gift = 'ベアXX' if gift == 'ベアX' else gift
                    gift = '次ゲーム' if gift == '次世代' else gift
                    print(f'契约材料: {sphere_1}, {sphere_2}, {gift}')
                    gift_dict[sex][gift][type_dict[char_type]].append(char_name)
                    sphere_dict[sex][sphere_1][type_dict[char_type]].append(char_name)
                    sphere_dict[sex][sphere_2][type_dict[char_type]].append(char_name)
                    # 爬取大头照
                    img_page_field = char_page_soup.find('div', id='block-views-slick-x-block-28').find('div', class_='view-content')
                    img_page_tag_list = img_page_field.find_all('li')
                    for img_page_tag in img_page_tag_list:
                        img_page_type = img_page_tag.find('div', class_='views-field views-field-title').find('a').contents[0]
                        img_page_href = img_page_tag.find('div', class_='views-field views-field-title').find('a').get('href')
                        if img_page_type == '初期':
                            img_page_url = url_prefix + img_page_href
                            img_page_soup = get_soup(img_page_url, my_headers)
                            img_dressups = img_page_soup.find('div', id='block-views-slick-x-block-23',
                                                              class_='block block-views')
                            img_link = img_dressups.find('div', class_='view-content').find('a').get('href')
                            keep_request, cnt = True, 1
                            while keep_request:
                                print(f'Download picture for {char_name} (Attempt {cnt})')
                                try:
                                    img = requests.get(img_link, headers=my_headers)
                                    keep_request = False
                                except:
                                    sleep(2)
                                    cnt += 1
                            filename = 'image/' + char_name + '.png'
                            with open(filename, 'wb') as fp:
                                fp.write(img.content)
                            resize_img(filename)
                            framed_filename = 'frame_image/' + char_name + '.png'
                            add_frame(filename, framed_filename)
                            # 即时保存礼物和宝玉pickle文件
                            with open(gift_dict_filename, 'wb') as f:
                                pickle.dump(gift_dict, f)
                            with open(sphere_dict_filename, 'wb') as f:
                                pickle.dump(sphere_dict, f)
                            break

    # 绘制紫礼物图和宝玉图
    make_gift_image(gift_dict, gift_filename)
    make_sphere_image(sphere_dict, sphere_filename)
