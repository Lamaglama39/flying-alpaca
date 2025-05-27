import pygame
import os

# Pygameの初期化
pygame.init()

# 画像サイズの設定（ドット絵風に小さく）
alpaca_width, alpaca_height = 20, 25
fence_width, fence_height = 10, 15

# 色の定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)
LIGHT_BROWN = (205, 133, 63)
BEIGE = (245, 222, 179)
DARK_BROWN = (101, 67, 33)
PINK = (255, 192, 203)
GRAY = (200, 200, 200)
TAN = (210, 180, 140)
CREAM = (255, 253, 208)

# imagesディレクトリの作成
os.makedirs('images', exist_ok=True)

# アルパカの画像を作成（ドット絵風）
alpaca_img = pygame.Surface((alpaca_width, alpaca_height), pygame.SRCALPHA)

# ピクセルサイズ（ドット絵風）
pixel_size = 1  # 1ピクセル単位で描画

# アルパカの体（ドット絵風）
# 体
pygame.draw.rect(alpaca_img, CREAM, (4, 10, 12, 8))

# 首と頭
pygame.draw.rect(alpaca_img, CREAM, (12, 4, 4, 6))
pygame.draw.rect(alpaca_img, CREAM, (10, 2, 8, 4))

# 耳
pygame.draw.rect(alpaca_img, CREAM, (9, 1, 2, 2))
pygame.draw.rect(alpaca_img, CREAM, (17, 1, 2, 2))

# 目
pygame.draw.rect(alpaca_img, BLACK, (11, 3, 1, 1))
pygame.draw.rect(alpaca_img, BLACK, (16, 3, 1, 1))

# 鼻
pygame.draw.rect(alpaca_img, BLACK, (13, 5, 2, 1))

# 足
pygame.draw.rect(alpaca_img, CREAM, (6, 18, 2, 6))
pygame.draw.rect(alpaca_img, CREAM, (12, 18, 2, 6))

# 柵の画像を作成（ドット絵風）
fence_img = pygame.Surface((fence_width, fence_height), pygame.SRCALPHA)

# 柵の柱
pygame.draw.rect(fence_img, BROWN, (0, 0, 2, fence_height))  # 左の柱
pygame.draw.rect(fence_img, BROWN, (fence_width - 2, 0, 2, fence_height))  # 右の柱

# 柵の横木
pygame.draw.rect(fence_img, LIGHT_BROWN, (0, 4, fence_width, 2))  # 上の横木
pygame.draw.rect(fence_img, LIGHT_BROWN, (0, 10, fence_width, 2))  # 下の横木

# 画像を保存
pygame.image.save(alpaca_img, 'images/alpaca.png')
pygame.image.save(fence_img, 'images/fence.png')

print("画像が正常に作成されました。")
pygame.quit()
