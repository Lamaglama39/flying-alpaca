import pygame
import sys
import random
import os
import math
import threading
from gtts import gTTS
import tempfile

# 初期化
pygame.init()
pygame.mixer.init()  # サウンド機能の初期化

# ピクセル表現のための設定
PIXEL_SIZE = 4  # ピクセルの大きさ
ORIGINAL_WIDTH, ORIGINAL_HEIGHT = 200, 150  # 元の解像度
WIDTH, HEIGHT = ORIGINAL_WIDTH * PIXEL_SIZE, ORIGINAL_HEIGHT * PIXEL_SIZE  # 実際の画面サイズ

# ピクセル化された画面を作成
pixel_surface = pygame.Surface((ORIGINAL_WIDTH, ORIGINAL_HEIGHT))
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("アルパカジャンプ")

# 色の定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
BROWN = (139, 69, 19)
BLUE = (135, 206, 235)
DARK_BLUE = (25, 25, 50)  # 夜空の色
DARK_GREEN = (0, 50, 0)   # 夜の草原の色
MOON_COLOR = (220, 220, 200)  # 月の色
CLOUD_COLOR = (100, 100, 130)  # 夜の雲の色
PINK = (255, 192, 203)    # ピンク色
CREAM = (255, 253, 208)   # クリーム色
LIGHT_PINK = (255, 223, 223)  # 薄いピンク色

# 日本語の数え方の配列
japanese_numbers = [
    "Ippiki",    # 一匹
    "Nihiki",    # 二匹
    "Sanbiki",   # 三匹
    "Yonhiki",   # 四匹
    "Gohiki",    # 五匹
    "Roppiki",   # 六匹
    "Nanahiki",  # 七匹
    "Happiki",   # 八匹
    "Kyuhiki",   # 九匹
    "Juppiki"    # 十匹
]

# 音声キャッシュ
sound_cache = {}
sound_cache_lock = threading.Lock()
sound_generation_thread = None

# 音声を動的に生成する関数
def generate_sound(count):
    global sound_cache, sound_generation_thread
    
    # すでにキャッシュにあれば何もしない
    with sound_cache_lock:
        if count in sound_cache:
            return
    
    try:
        # 数に応じた日本語の数え方を取得
        if count <= 10:
            number_text = japanese_numbers[count - 1]
        else:
            # 10以上の場合も日本語風に読む
            # 例: 11 -> Ju Ippiki (十一匹)
            # 例: 21 -> Ni Ju Ippiki (二十一匹)
            tens = (count // 10) % 10
            ones = count % 10
            
            if tens == 1:
                tens_text = "Ju"  # 十
            elif tens > 1:
                tens_text = japanese_numbers[tens - 1].split("hiki")[0] + " Ju"  # 二十、三十など
            else:
                tens_text = ""
                
            if ones == 0:
                ones_text = ""
            else:
                ones_text = " " + japanese_numbers[ones - 1]
                
            number_text = f"{tens_text}{ones_text}"
            
            # 100以上の場合
            hundreds = count // 100
            if hundreds > 0:
                if hundreds == 1:
                    hundreds_text = "Hyaku"  # 百
                else:
                    hundreds_text = japanese_numbers[hundreds - 1].split("hiki")[0] + " Hyaku"  # 二百、三百など
                number_text = f"{hundreds_text} {number_text}"
                
            # 空白を調整
            number_text = number_text.strip()
        
        # 「アルパカが〇〇匹」というテキストを作成
        text = f"Alpaca ga {number_text}"
        
        # 一時ファイルを作成
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            temp_path = temp_file.name
        
        # 音声を生成して一時ファイルに保存
        tts = gTTS(text, lang='en')
        tts.save(temp_path)
        
        # 音声をロードしてキャッシュに保存
        with sound_cache_lock:
            sound_cache[count] = pygame.mixer.Sound(temp_path)
        
        # 一時ファイルを削除（Windowsでは使用中のファイルは削除できないため、後で削除）
        try:
            os.remove(temp_path)
        except:
            pass
            
    except Exception as e:
        print(f"音声生成エラー（{count}）: {e}")

# 音声を非同期で生成する関数
def generate_sound_async(count):
    global sound_generation_thread
    
    # すでにキャッシュにあれば何もしない
    with sound_cache_lock:
        if count in sound_cache:
            return
    
    # 別スレッドで音声を生成
    sound_generation_thread = threading.Thread(target=generate_sound, args=(count,))
    sound_generation_thread.daemon = True
    sound_generation_thread.start()

# 先行して最初の10個の音声を生成
def preload_initial_sounds():
    for i in range(1, 11):
        generate_sound(i)

# ピクセル化された描画を行う関数
def draw_pixel_rect(surface, color, rect):
    x, y, w, h = rect
    for i in range(w):
        for j in range(h):
            surface.set_at((x + i, y + j), color)

def draw_pixel_circle(surface, color, center, radius):
    x0, y0 = center
    for x in range(x0 - radius, x0 + radius + 1):
        for y in range(y0 - radius, y0 + radius + 1):
            if 0 <= x < ORIGINAL_WIDTH and 0 <= y < ORIGINAL_HEIGHT:
                if (x - x0)**2 + (y - y0)**2 <= radius**2:
                    surface.set_at((x, y), color)

# 画像のロード
def load_image(name, scale=1.0):
    try:
        image_path = os.path.join('images', name)
        image = pygame.image.load(image_path)
        if scale != 1.0:
            new_size = (int(image.get_width() * scale), int(image.get_height() * scale))
            image = pygame.transform.scale(image, new_size)
        return image
    except pygame.error as e:
        print(f"画像の読み込みに失敗しました: {name}")
        print(f"エラー: {e}")
        # 画像が見つからない場合は代替の四角形を返す
        surf = pygame.Surface((50, 50))
        surf.fill((255, 0, 0))  # 赤い四角形
        return surf

# 画像がない場合のためのダミー画像を作成
def create_dummy_images():
    # アルパカのダミー画像
    alpaca_img = pygame.Surface((20, 25), pygame.SRCALPHA)
    pygame.draw.ellipse(alpaca_img, WHITE, (0, 6, 16, 12))  # 体
    pygame.draw.rect(alpaca_img, WHITE, (10, 0, 4, 8))  # 首
    pygame.draw.ellipse(alpaca_img, WHITE, (8, 0, 8, 6))  # 頭
    pygame.draw.rect(alpaca_img, BLACK, (2, 14, 2, 6))  # 前足
    pygame.draw.rect(alpaca_img, BLACK, (12, 14, 2, 6))  # 後ろ足
    
    # 柵のダミー画像
    fence_img = pygame.Surface((10, 15), pygame.SRCALPHA)
    pygame.draw.rect(fence_img, BROWN, (0, 0, 2, 15))  # 左の柱
    pygame.draw.rect(fence_img, BROWN, (8, 0, 2, 15))  # 右の柱
    pygame.draw.rect(fence_img, BROWN, (0, 4, 10, 2))  # 上の横木
    pygame.draw.rect(fence_img, BROWN, (0, 10, 10, 2))  # 下の横木
    
    # 画像を保存
    os.makedirs('images', exist_ok=True)
    pygame.image.save(alpaca_img, 'images/alpaca.png')
    pygame.image.save(fence_img, 'images/fence.png')

# 画像ファイルがなければダミー画像を作成
if not os.path.exists('images/alpaca.png') or not os.path.exists('images/fence.png'):
    create_dummy_images()

# 画像のロード
alpaca_img = load_image('alpaca.png')
fence_img = load_image('fence.png')

# アルパカのクラス
class Alpaca:
    def __init__(self, x):
        self.image = alpaca_img
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.x = x
        self.y = ORIGINAL_HEIGHT - self.height - 10  # 地面からの高さ
        self.jumping = False
        self.jump_time = 0
        self.jump_duration = 90  # ジャンプの持続時間（フレーム数）
        self.jump_height = 30  # ジャンプの最大高さ（ピクセル解像度に合わせて調整）
        # 速度をランダムに設定（0.5〜1.0の範囲）
        self.horizontal_speed = 0.5 + random.random() * 0.5
        self.passed_fence = False
        self.original_y = self.y  # 元の高さを記録
        self.original_x = self.x  # 元のX位置を記録
        
    def draw(self, surface):
        surface.blit(self.image, (int(self.x), int(self.y)))
        
    def jump(self):
        if not self.jumping:
            self.jumping = True
            self.jump_time = 0
            self.original_y = self.y  # ジャンプ開始時の高さを記録
            self.original_x = self.x  # ジャンプ開始時のX位置を記録
            
    def update(self):
        if self.jumping:
            # サインカーブを使ってふわふわとしたジャンプを実現
            self.jump_time += 1
            progress = self.jump_time / self.jump_duration  # 0から1の進行度
            
            if progress <= 1.0:
                # サインカーブの前半部分を使用（0から180度）
                jump_factor = math.sin(progress * math.pi)
                self.y = self.original_y - jump_factor * self.jump_height
                
                # ジャンプ中は常に前方に進む（一定速度で）- 速度を半分程度に調整
                self.x += self.horizontal_speed * 0.75  # ジャンプ中の前進速度を調整
            else:
                # ジャンプ終了
                self.jumping = False
                self.y = self.original_y
        else:
            # 通常移動
            self.x += self.horizontal_speed
        
    def get_rect(self):
        return pygame.Rect(int(self.x) + 2, int(self.y) + 2, self.width - 4, self.height - 4)

# 柵のクラス
class Fence:
    def __init__(self):
        self.image = fence_img
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.x = ORIGINAL_WIDTH // 2 - self.width // 2  # 画面中央に配置
        self.y = ORIGINAL_HEIGHT - self.height - 10  # 地面からの高さ
        
    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

# ゲームの状態
class Game:
    def __init__(self):
        self.alpacas = []
        self.fence = Fence()
        self.score = 0
        self.font = pygame.font.SysFont(None, 18)  # フォントサイズを大きくして読みやすく
        self.spawn_timer = 0
        self.spawn_interval = 150  # フレーム単位でのアルパカの生成間隔
        self.last_played_sound = 0  # 最後に再生した音声のスコア
        
        # 夜空の星を生成（位置、サイズ）
        self.stars = []
        for _ in range(30):  # 星の数を減らして解像度に合わせる
            x = random.randint(0, ORIGINAL_WIDTH)
            y = random.randint(0, ORIGINAL_HEIGHT - 20)
            size = random.random() + 0.5  # 0.5〜1.5の範囲
            self.stars.append([(x, y), size])
            
        # 雲を生成
        self.clouds = []
        for _ in range(3):  # 雲の数を減らして解像度に合わせる
            x = random.randint(0, ORIGINAL_WIDTH)
            y = random.randint(10, 40)
            size = random.randint(8, 16)
            self.clouds.append([x, y, size])
        
        # 次のスコアの音声を先読み
        self.preload_next_sounds()
        
    def spawn_alpaca(self):
        self.alpacas.append(Alpaca(-20))  # 画面左外から登場
        
    def update(self):
        # アルパカの生成
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_alpaca()
            self.spawn_timer = 0
            # 難易度調整（間隔を少しずつ短くする）
            self.spawn_interval = max(100, self.spawn_interval - 1)  # 最小間隔を長めに
        
        # 雲を動かす
        for cloud in self.clouds:
            cloud[0] -= 0.1  # 雲をゆっくり左に動かす
            if cloud[0] < -cloud[2] * 2:
                cloud[0] = ORIGINAL_WIDTH + cloud[2]
                cloud[1] = random.randint(10, 40)
        
        # アルパカの更新
        for alpaca in self.alpacas[:]:
            alpaca.update()
            
            # スコア加算（アルパカが柵を通過したとき）
            if not alpaca.passed_fence and alpaca.x > self.fence.x + self.fence.width:
                alpaca.passed_fence = True
                self.score += 1
                
                # スコアに応じた音声を再生
                if self.score != self.last_played_sound:
                    self.play_count_sound(self.score)
                    self.last_played_sound = self.score
                    
                    # 次のスコアの音声を先読み
                    self.preload_next_sounds()
                
            # 画面外のアルパカを削除
            if alpaca.x > ORIGINAL_WIDTH + 20:
                self.alpacas.remove(alpaca)
                
            # 衝突判定
            if self.check_collision(alpaca, self.fence):
                self.alpacas.remove(alpaca)
                return False  # ゲームオーバー
                
        return True  # ゲーム続行
    
    def check_collision(self, alpaca, fence):
        # 衝突判定
        alpaca_rect = alpaca.get_rect()
        fence_rect = fence.get_rect()
        return alpaca_rect.colliderect(fence_rect)
    
    def play_count_sound(self, count):
        # カウントに対応する音声を再生
        with sound_cache_lock:
            if count in sound_cache:
                sound_cache[count].play()
            else:
                # 音声がまだ生成されていない場合は生成
                generate_sound_async(count)
    
    def preload_next_sounds(self):
        # 次のスコアの音声を先読み
        next_score = self.score + 1
        generate_sound_async(next_score)
        generate_sound_async(next_score + 1)
        generate_sound_async(next_score + 2)
    
    def draw(self, surface):
        # 背景
        # 夜空の背景（濃い青）
        surface.fill(DARK_BLUE)  # 暗い青色で夜空を表現
        
        # 星をランダムに描画
        for star in self.stars:
            pos, size = star
            draw_pixel_circle(surface, WHITE, pos, int(size))
        
        # 月を描画
        draw_pixel_circle(surface, MOON_COLOR, (ORIGINAL_WIDTH - 20, 20), 8)
        draw_pixel_circle(surface, DARK_BLUE, (ORIGINAL_WIDTH - 24, 17), 8)  # 三日月風の影
        
        # 雲を描画（ピクセル風に）
        for cloud in self.clouds:
            x, y, size = cloud
            draw_pixel_rect(surface, CLOUD_COLOR, (int(x), int(y), size, size // 2))
            draw_pixel_rect(surface, CLOUD_COLOR, (int(x + size // 2), int(y - size // 4), size // 2, size // 2))
        
        # 地面（暗い緑）
        draw_pixel_rect(surface, DARK_GREEN, (0, ORIGINAL_HEIGHT - 10, ORIGINAL_WIDTH, 10))  # 暗い緑色の地面
        
        # 柵の描画
        self.fence.draw(surface)
        
        # アルパカの描画
        for alpaca in self.alpacas:
            alpaca.draw(surface)
        
        # スコア表示（中央上部に配置）
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        # 背景を追加して読みやすく
        score_bg = pygame.Surface((score_text.get_width() + 4, score_text.get_height() + 4))
        score_bg.fill(DARK_BLUE)
        surface.blit(score_bg, (ORIGINAL_WIDTH//2 - score_text.get_width()//2 - 2, 4))
        surface.blit(score_text, (ORIGINAL_WIDTH//2 - score_text.get_width()//2, 6))

# メインゲームループ
def main():
    # 最初の音声をバックグラウンドで先読み
    preload_thread = threading.Thread(target=preload_initial_sounds)
    preload_thread.daemon = True
    preload_thread.start()
    
    clock = pygame.time.Clock()
    game = Game()
    running = True
    game_active = True
    
    # ゲームオーバー時の星を生成
    game_over_stars = []
    for i in range(30):
        x = random.randint(0, ORIGINAL_WIDTH)
        y = random.randint(0, ORIGINAL_HEIGHT)
        size = random.random() + 0.5
        game_over_stars.append([(x, y), size])
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game_active:
                    # 最も柵に近いアルパカをジャンプさせる
                    closest_alpaca = None
                    min_distance = float('inf')
                    
                    for alpaca in game.alpacas:
                        if not alpaca.passed_fence:
                            distance = game.fence.x - alpaca.x
                            if 0 < distance < min_distance and distance < 60:  # 距離制限を調整
                                min_distance = distance
                                closest_alpaca = alpaca
                    
                    if closest_alpaca:
                        closest_alpaca.jump()
                        
                elif event.key == pygame.K_r and not game_active:
                    # リスタート
                    game = Game()
                    game_active = True
                # エンターキーとRキーを明確に区別
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    # エンターキーの処理（必要に応じて）
                    pass
        
        # ピクセル画面をクリア
        pixel_surface.fill((0, 0, 0))
        
        if game_active:
            game_active = game.update()
            game.draw(pixel_surface)
        else:
            # ゲームオーバー画面
            pixel_surface.fill(DARK_BLUE)
            
            # 星をランダムに描画（ゲームオーバー画面でも）
            for star in game_over_stars:
                pos, size = star
                draw_pixel_circle(pixel_surface, WHITE, pos, int(size))
            
            # ゲームオーバーのテキスト表示
            font = pygame.font.SysFont(None, 24)  # フォントサイズを大きくして読みやすく
            game_over_text = font.render("Game Over", True, WHITE)
            score_text = font.render(f"Score: {game.score}", True, WHITE)
            restart_text = font.render("Press R to Restart", True, WHITE)
            
            # 「おやすみなさい」のメッセージを追加
            if game.score > 10:
                goodnight_font = pygame.font.SysFont(None, 18)
                goodnight_text = goodnight_font.render("Good Night...", True, WHITE)
                pixel_surface.blit(goodnight_text, (ORIGINAL_WIDTH//2 - goodnight_text.get_width()//2, ORIGINAL_HEIGHT//2 + 30))
            
            # テキストを直接描画
            pixel_surface.blit(game_over_text, (ORIGINAL_WIDTH//2 - game_over_text.get_width()//2, ORIGINAL_HEIGHT//2 - 20))
            pixel_surface.blit(score_text, (ORIGINAL_WIDTH//2 - score_text.get_width()//2, ORIGINAL_HEIGHT//2))
            pixel_surface.blit(restart_text, (ORIGINAL_WIDTH//2 - restart_text.get_width()//2, ORIGINAL_HEIGHT//2 + 20))
        
        # ピクセル画面を実際の画面サイズに拡大
        pygame.transform.scale(pixel_surface, (WIDTH, HEIGHT), screen)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
