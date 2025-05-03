from PIL import Image, ImageDraw, ImageFont
from copy import deepcopy

GIFT_LIST = ['香クッキ', '碧洋', '次ゲーム', 'ベアXX', '同人誌', 'ワイングラス', 'ワンピ', '名画']
SPHERE_LIST = ['純真', '希望', '知恵', '慈愛', '誠実', '勇気', '意志', '光明']
IMG_WIDTH = 228  # 含边框
FRAME_WIDTH = 4
FONT_SIZE = 80  # 磅, 1磅=4/3像素
FONT_HEIGHT = int(FONT_SIZE * 1.9)


def make_gift_image(gift_dict: dict, output_fp):

    # 基本信息
    gift_list = GIFT_LIST
    female_dict, male_dict = deepcopy(gift_dict['female']), deepcopy(gift_dict['male'])
    female_limited_list = [char for char_list in female_dict.values() for char in char_list[1]]
    male_limited_list = [char for char_list in male_dict.values() for char in char_list[1]]
    # 合并常设和限定角色list
    for gift in gift_list:
        female_dict[gift] = female_dict[gift][0] + female_dict[gift][1]
        male_dict[gift] = male_dict[gift][0] + male_dict[gift][1]
    max_female_char_num = max(list(map(lambda x: len(female_dict[x]), gift_list)))
    max_male_char_num = max(list(map(lambda x: len(male_dict[x]), gift_list)))
    max_char_num = max_female_char_num + max_male_char_num

    # 绘制灰色底图
    gray_bgHeight = len(gift_list) * IMG_WIDTH - (len(gift_list) - 1) * FRAME_WIDTH + FONT_HEIGHT
    gray_bgWidth = IMG_WIDTH * (max_char_num + 1) - FRAME_WIDTH * (max_char_num - 2)
    gray_bgImg = Image.new("RGB", (gray_bgWidth, gray_bgHeight), "gray")

    # 绘制蓝色底图以产生外边框效果
    blue_bgHeight = gray_bgHeight - 2 * FRAME_WIDTH
    blue_bgWidth = gray_bgWidth - 2 * FRAME_WIDTH
    blue_bgImg = Image.new("RGB", (blue_bgWidth, blue_bgHeight), (222, 235, 246))
    gray_bgImg.paste(blue_bgImg, (FRAME_WIDTH, FRAME_WIDTH))

    # 绘制内部灰色底图
    gray_inner_bgHeight = len(gift_list) * IMG_WIDTH - (len(gift_list) - 1) * FRAME_WIDTH
    gray_inner_bgWidth = gray_bgWidth
    gray_inner_bgImg = Image.new("RGB", (gray_inner_bgWidth, gray_inner_bgHeight), "gray")
    gray_bgImg.paste(gray_inner_bgImg, (0, 0))

    # 绘制内部蓝色底图以产生边框效果
    blue_inner_bgHeight = gray_inner_bgHeight - 2 * FRAME_WIDTH
    blue_inner_bgWidth = gray_inner_bgWidth - 2 * FRAME_WIDTH
    blue_inner_bgImg = Image.new("RGB", (blue_inner_bgWidth, blue_inner_bgHeight), (222, 235, 246))
    gray_bgImg.paste(blue_inner_bgImg, (FRAME_WIDTH, FRAME_WIDTH))

    # 放入礼物
    gift_x = IMG_WIDTH * max_male_char_num - FRAME_WIDTH * (max_male_char_num - 1)
    for gift in gift_list:
        gift_idx = gift_list.index(gift)
        gift_path = './frame_image/' + gift + '.jpg'
        gift_img = Image.open(gift_path)
        gift_y = (IMG_WIDTH - FRAME_WIDTH) * gift_idx
        gray_bgImg.paste(gift_img, (gift_x, gift_y))

    # 放入人物
    for gift in gift_list:
        gift_idx = gift_list.index(gift)
        # 女性雀士
        female_list = female_dict[gift]
        for char in female_list:
            char_idx = female_list.index(char)
            char_path = './frame_image/' + char + '.png'
            char_img = Image.open(char_path)
            x = gift_x + IMG_WIDTH + (IMG_WIDTH - FRAME_WIDTH) * char_idx
            y = (IMG_WIDTH - FRAME_WIDTH) * gift_idx
            # 判断是否为期间限定雀士
            if char in female_limited_list:
                yellow_char_bgImg = Image.new("RGB", (IMG_WIDTH, IMG_WIDTH), (255, 204, 102))
                gray_bgImg.paste(yellow_char_bgImg, (x, y))
            gray_bgImg.paste(char_img, (x, y), char_img)  # 第三个参数作为遮罩
        # 男性雀士
        male_list = male_dict[gift]
        for char in male_list:
            char_idx = male_list.index(char)
            char_path = './frame_image/' + char + '.png'
            char_img = Image.open(char_path)
            x = gift_x - (IMG_WIDTH - FRAME_WIDTH) * (char_idx + 1) - FRAME_WIDTH
            y = (IMG_WIDTH - FRAME_WIDTH) * gift_idx
            # 判断是否为期间限定雀士
            if char in male_limited_list:
                yellow_char_bgImg = Image.new("RGB", (IMG_WIDTH, IMG_WIDTH), (255, 204, 102))
                gray_bgImg.paste(yellow_char_bgImg, (x, y))
            gray_bgImg.paste(char_img, (x, y), char_img)

    # 添加说明
    font = ImageFont.truetype(font='STXINWEI.TTF', size=FONT_SIZE)
    draw = ImageDraw.Draw(gray_bgImg)
    x = gift_x + 20
    y = len(gift_list) * IMG_WIDTH - (len(gift_list) - 1) * FRAME_WIDTH \
        + 2 * FRAME_WIDTH + (FONT_HEIGHT - FONT_SIZE * 4 / 3) / 2  # 1磅=4/3像素
    text_str = '*注：藤田佳奈的喜好礼物为游戏机系列，契约礼物为经典名画'
    draw.text(xy=(x, y), text=text_str, fill='orangered', font=font)
    draw.text(xy=(x + 1, y + 1), text=text_str, fill='orangered', font=font)

    gray_bgImg.save(output_fp)


def make_sphere_image(sphere_dict: dict, output_fp):

    # 基本信息
    sphere_list = SPHERE_LIST
    female_original_dict = {sphere: char_list[0] for sphere, char_list in sphere_dict['female'].items()}
    male_original_dict = {sphere: char_list[0] for sphere, char_list in sphere_dict['male'].items()}
    female_limited_dict = {sphere: char_list[1] for sphere, char_list in sphere_dict['female'].items()}
    male_limited_dict = {sphere: char_list[1] for sphere, char_list in sphere_dict['male'].items()}

    max_female_char_num = max(
        list(map(lambda x: max(len(female_original_dict[x]), len(female_limited_dict[x])), sphere_list)))
    max_male_char_num = max(list(map(lambda x: max(len(male_original_dict[x]), len(male_limited_dict[x])), sphere_list)))
    max_char_num = max_female_char_num + max_male_char_num
    sphere_x = IMG_WIDTH * max_male_char_num - FRAME_WIDTH * (max_male_char_num - 1)  # 参考点: 宝玉所在列的x坐标

    # 灰色底图
    gray_bgHeight = len(sphere_list) * IMG_WIDTH * 2 - (len(sphere_list) * 2 - 1) * FRAME_WIDTH  # 每个宝玉占两行
    gray_bgWidth = IMG_WIDTH * (max_char_num + 1) - FRAME_WIDTH * (max_char_num - 2)  # 宝玉边框与人物边框不重合
    gray_bgImg = Image.new("RGB", (gray_bgWidth, gray_bgHeight), "gray")

    # 蓝色背景
    blue_bgHeight = gray_bgHeight - 2 * FRAME_WIDTH
    blue_bgWidth = gray_bgWidth - 2 * FRAME_WIDTH
    blue_bgImg = Image.new("RGB", (blue_bgWidth, blue_bgHeight), (222, 235, 246))
    gray_bgImg.paste(blue_bgImg, (FRAME_WIDTH, FRAME_WIDTH))

    # 绘制内部边框优化视觉效果
    frame_gray_height, frame_blue_height = IMG_WIDTH * 2 - FRAME_WIDTH, IMG_WIDTH * 2 - FRAME_WIDTH * 3
    frame_gray_width_female = (IMG_WIDTH - FRAME_WIDTH) * max_female_char_num + FRAME_WIDTH
    frame_blue_width_female = (IMG_WIDTH - FRAME_WIDTH) * max_female_char_num - FRAME_WIDTH
    frame_gray_width_male = (IMG_WIDTH - FRAME_WIDTH) * max_male_char_num + FRAME_WIDTH
    frame_blue_width_male = (IMG_WIDTH - FRAME_WIDTH) * max_male_char_num - FRAME_WIDTH
    frame_gray_width_sphere = IMG_WIDTH + FRAME_WIDTH * 2
    frame_blue_width_sphere = IMG_WIDTH
    for sphere_idx, sphere in enumerate(sphere_list):
        # 灰色底图
        frame_gray_x_female, frame_gray_x_male, frame_gray_x_sphere = sphere_x + IMG_WIDTH, 0, sphere_x - FRAME_WIDTH
        frame_gray_y = (IMG_WIDTH - FRAME_WIDTH) * 2 * sphere_idx
        frame_gray_female = Image.new("RGB", (frame_gray_width_female, frame_gray_height), "gray")
        frame_gray_male = Image.new("RGB", (frame_gray_width_male, frame_gray_height), "gray")
        frame_gray_sphere = Image.new("RGB", (frame_gray_width_sphere, frame_gray_height), "gray")
        gray_bgImg.paste(frame_gray_female, (frame_gray_x_female, frame_gray_y))
        gray_bgImg.paste(frame_gray_male, (frame_gray_x_male, frame_gray_y))
        gray_bgImg.paste(frame_gray_sphere, (frame_gray_x_sphere, frame_gray_y))
        # 内部蓝色贴图产生边框效果
        frame_blue_x_female, frame_blue_x_male, frame_blue_x_sphere = sphere_x + IMG_WIDTH + FRAME_WIDTH, FRAME_WIDTH, sphere_x
        frame_blue_y = (IMG_WIDTH - FRAME_WIDTH) * 2 * sphere_idx + FRAME_WIDTH
        frame_blue_female = Image.new("RGB", (frame_blue_width_female, frame_blue_height), (222, 235, 246))
        frame_blue_male = Image.new("RGB", (frame_blue_width_male, frame_blue_height), (222, 235, 246))
        frame_blue_sphere = Image.new("RGB", (frame_blue_width_sphere, frame_blue_height), (222, 235, 246))
        gray_bgImg.paste(frame_blue_female, (frame_blue_x_female, frame_blue_y))
        gray_bgImg.paste(frame_blue_male, (frame_blue_x_male, frame_blue_y))
        gray_bgImg.paste(frame_blue_sphere, (frame_blue_x_sphere, frame_blue_y))

    # 放入宝玉
    for sphere_idx, sphere in enumerate(sphere_list):
        sphere_path = './frame_image/' + sphere + '.jpg'
        sphere_img = Image.open(sphere_path)
        sphere_y = (IMG_WIDTH - FRAME_WIDTH) * sphere_idx * 2 + int(IMG_WIDTH * 0.5)
        gray_bgImg.paste(sphere_img, (sphere_x, sphere_y))

    # 放入人物
    for sphere_idx, sphere in enumerate(sphere_list):
        # 女性常驻雀士
        female_original_list = female_original_dict[sphere]
        for char_idx, char in enumerate(female_original_list):
            char_path = './frame_image/' + char + '.png'
            char_img = Image.open(char_path)
            x = sphere_x + IMG_WIDTH + (IMG_WIDTH - FRAME_WIDTH) * char_idx
            y = (IMG_WIDTH - FRAME_WIDTH) * sphere_idx * 2
            gray_bgImg.paste(char_img, (x, y), char_img)  # 第三个参数作为遮罩
        # 女性限定雀士
        female_limited_list = female_limited_dict[sphere]
        for char_idx, char in enumerate(female_limited_list):
            char_path = './frame_image/' + char + '.png'
            char_img = Image.open(char_path)
            x = sphere_x + IMG_WIDTH + (IMG_WIDTH - FRAME_WIDTH) * char_idx
            y = (IMG_WIDTH - FRAME_WIDTH) * (sphere_idx * 2 + 1)
            yellow_char_bgImg = Image.new("RGB", (IMG_WIDTH, IMG_WIDTH), (255, 204, 102))
            gray_bgImg.paste(yellow_char_bgImg, (x, y))
            gray_bgImg.paste(char_img, (x, y), char_img)  # 第三个参数作为遮罩

        # 男性常驻雀士
        male_original_list = male_original_dict[sphere]
        for char_idx, char in enumerate(male_original_list):
            char_path = './frame_image/' + char + '.png'
            char_img = Image.open(char_path)
            x = sphere_x - (IMG_WIDTH - FRAME_WIDTH) * (char_idx + 1) - FRAME_WIDTH
            y = (IMG_WIDTH - FRAME_WIDTH) * sphere_idx * 2
            gray_bgImg.paste(char_img, (x, y), char_img)  # 第三个参数作为遮罩
        # 男性限定雀士
        male_limited_list = male_limited_dict[sphere]
        for char_idx, char in enumerate(male_limited_list):
            char_path = './frame_image/' + char + '.png'
            char_img = Image.open(char_path)
            x = sphere_x - (IMG_WIDTH - FRAME_WIDTH) * (char_idx + 1) - FRAME_WIDTH
            y = (IMG_WIDTH - FRAME_WIDTH) * (sphere_idx * 2 + 1)
            yellow_char_bgImg = Image.new("RGB", (IMG_WIDTH, IMG_WIDTH), (255, 204, 102))
            gray_bgImg.paste(yellow_char_bgImg, (x, y))
            gray_bgImg.paste(char_img, (x, y), char_img)  # 第三个参数作为遮罩

    gray_bgImg.save(output_fp)
