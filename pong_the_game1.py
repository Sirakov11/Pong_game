from shutil import move
import pygame,sys
from pygame.locals import*
import random
pygame.init()

# Базови параметри
width = 700
height = 500
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Pong")

fps = 60


white = (255, 255, 255)
black = (50, 50, 50)

paddle_width, paddle_height = 20, 100
ball_radius = 7

# Шрифт
score_font = pygame.font.SysFont("Ink Free", 50)
class Paddle:
    paddle_vel = 4 # Скоростта, с която се мести платформата
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        # Инициализираме 
        self.width = width
        self.height = height
        # Запазваме първоначалните кординати на платформата, защото ще ни трябват при reset - а
        self.original_x = self.x
        self.original_y = self.y
        # Рисуваме платформата под формата на издължен правоъгълник
    def draw(self, window):
        pygame.draw.rect(
            window, white, (self.x, self.y, self.width, self.height))
        # Имаме флаг, който играе ролята на индикатор на посоката, в която да се движи платформата
    def move(self, flag = 1):
        if flag == 1:
            self.y -= self.paddle_vel
        elif flag == 0:
            self.y += self.paddle_vel
        # Платформата отива на своята първоначалната позиция
    def reset(self):
        self.x = self.original_x
        self.y = self.original_y
        self.height = paddle_height
    



class Ball:
    max_vel = 8
    # Максимална скорост
    def __init__(self, x, y, radius):
        self.x = self.original_x = x # Запазваме първоначалните кординати на топката, защото ще ни трябват при reset - а
        self.y = self.original_y = y
        self.radius = radius
        self.x_vel = self.max_vel
        self.y_vel = 0
        self.last_hit = "left" # Индикатор, който ще ни посочи коя от двете платоформи е изтреляла топчето преди то да стигне до суперсилата
        self.power_taken = False # Индикатор, който проверява дали топчето е стигнало до суперсилата
    def draw(self, window):
        pygame.draw.circle(window, white, (self.x, self.y), self.radius) # Рисуваме топчето

    def move(self):
        self.x += self.x_vel # Движение на топчето. Топчето се движи в зависимост от скоростта
        self.y += self.y_vel

    def reset(self):
        self.x = self.original_x
        self.y = self.original_y
        self.y_vel = 0 # Скоростта се умножава по -1, защото топката се движи в противоположната посока
        self.x_vel *= -1
    def hit_power(self, rand_x, rand_y):
        # Накратко проверявам дали топката минава през някой от ъглите на квадратчето 
        if rand_x <= self.x and rand_y <= self.y and rand_x + 15 >= self.x and rand_y + 15 >= self.y:
            self.power_taken = True    
        if rand_x <= self.x + 15 and rand_y <= self.y and rand_x + 15 >= self.x + 15 and rand_y + 15 >= self.y:
            self.power_taken = True 
        if rand_x <= self.x and rand_y <= self.y + 15 and rand_x + 15 >= self.x and rand_y + 15 >= self.y + 15:
            self.power_taken = True 
        if rand_x <= self.x + 15 and rand_y <= self.y + 15 and rand_x + 15 >= self.x + 15 and rand_y + 15 >= self.y + 15:
            self.power_taken = True 
 


class Draw:
    # Конструктор
    def __init__(self, window, paddles, ball, left_score, right_score, x, y):
        self.window = window
        self.paddles = paddles
        self.ball = ball
        self.left_score = left_score
        self.right_score = right_score
        self.x = x
        self.y = y
    def draw(self):
        window.fill(black)
        # Рисуваме суперсилата
        pygame.draw.rect(
            window, "blue", (self.x, self.y, 15, 15))
        # Рисуваме резултата
        left_score_text = score_font.render(f"{self.left_score}", 1, white)
        right_score_text = score_font.render(f"{self.right_score}", 1, white)
        window.blit(left_score_text, (width//4 - left_score_text.get_width()//2, 20))
        window.blit(right_score_text, (width * (3/4) - right_score_text.get_width()//2, 20))
        # Рисуваме платформите
        for paddle in self.paddles:
            paddle.draw(window)

        pygame.draw.line(window, white, (width//2,0), (width//2, height), 5)
        # Рисуваме топката
        self.ball.draw(window)
        pygame.display.update()

class Collision:
    def __init__(self, ball, left_paddle, right_paddle):
        self.ball = ball
        self.left_paddle = left_paddle
        self.right_paddle = right_paddle

    def collision(self):
        # Следващите 2 реда код правят топката да отскача от най-долната и най-горната част на полето
        if self.ball.y + self.ball.radius >= height or self.ball.y - self.ball.radius <= 0:
            self.ball.y_vel *= -1
        # Проверява от коя платформа е отскочила топката
        if self.ball.power_taken:
            self.ball.power_taken = False
            if self.ball.last_hit == "left":
                self.left_paddle.height += 10
            else:
                self.right_paddle.height += 10
        # Този if показва дали топката се насочва към лявата платоформа
        if self.ball.x_vel < 0:
        # Следващите if - ове следят за удрянето на топката в платфрормата; Тя не трябва да минава през платформата
            if self.ball.y <= self.left_paddle.y + self.left_paddle.height:
                if self.ball.y >= self.left_paddle.y:
                    if self.ball.x - self.ball.radius <= self.left_paddle.x + self.left_paddle.width:
                        self.ball.x_vel *= -1
                        middle_y = self.left_paddle.y + self.left_paddle.height / 2 # Променлива, която приема най-централния y
                        difference_in_y = middle_y - self.ball.y # Изчисляваме разликата между y на топката и y на платоформата
                        reduction_factor = (self.left_paddle.height / 2) / self.ball.max_vel # Изместването между платформата и топката
                        y_vel = difference_in_y / reduction_factor
                        # Получаваме скоростта като от максималното изместване разделим на редуциращия фактор
                        self.ball.y_vel = -1 * y_vel
                        self.ball.last_hit = "left"
        # Тук важи същото само, че за дясната платформа
        else:
            if self.ball.y <= self.right_paddle.y + self.right_paddle.height:
                if self.ball.y >= self.right_paddle.y :
                    if self.ball.x + self.ball.radius >= self.right_paddle.x:
                        self.ball.x_vel *= -1
                        middle_y = self.right_paddle.y + self.right_paddle.height / 2
                        difference_in_y = middle_y - self.ball.y
                        reduction_factor = (self.right_paddle.height / 2) / self.ball.max_vel
                        y_vel = difference_in_y / reduction_factor
                        self.ball.y_vel = -1 * y_vel
                        self.ball.last_hit = "right"


class Paddle_movement:
    def __init__(self, left_paddle, right_paddle):
        self.left_paddle = left_paddle
        self.right_paddle = right_paddle
        
    def paddle_movement(self, keys):
        if self.left_paddle.y - self.left_paddle.paddle_vel >= 0:
            if keys[pygame.K_w]: # W - означава нагоре
                self.left_paddle.move(flag = 1)
        if self.left_paddle.y + self.left_paddle.paddle_vel + self.left_paddle.height <= height:
            if keys[pygame.K_s]: # S - надолу
                self.left_paddle.move(flag = 0)
        if self.right_paddle.y - self.right_paddle.paddle_vel >= 0:
            if keys[pygame.K_UP]: # Горна стрелкичка - нагоре
                self.right_paddle.move(flag = 1)
        if self.right_paddle.y + self.right_paddle.paddle_vel + self.right_paddle.height <= height:
            if keys[pygame.K_DOWN]: # Долна стрелкичка - надолу
                self.right_paddle.move(flag = 0)


def main():
    run = True
    clock = pygame.time.Clock()
    # Променливи, които присвоявам на класовете
    left_paddle = Paddle(10, height//2 - paddle_height //
                         2, paddle_width, paddle_height)
    right_paddle = Paddle(width - 10 - paddle_width, height //
                          2 - paddle_height//2, paddle_width, paddle_height)
    ball = Ball(width // 2, height // 2, ball_radius)

    movement = Paddle_movement(left_paddle, right_paddle)
    left_score = 0
    right_score = 0
    col = Collision(ball, left_paddle, right_paddle)
    # Рандъм параметрите на суперсилата
    rand_x = random.randint(paddle_width + 10, width - paddle_width - 10)
    rand_y = random.randint(0, height - 10)
    while run:
        # Всички атрибути се рисуват на екрана
        paint = Draw(window, [left_paddle, right_paddle], ball, left_score, right_score, rand_x, rand_y)
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        keys = pygame.key.get_pressed() # Служи за да може да натиснем зададените от нас бутони
        movement.paddle_movement(keys)
        paint.draw()
        ball.move()
        col.collision()
        ball.hit_power(rand_x, rand_y)
        # Проверява дали топката е излязла от полето за да присъдят точка на съответния играч
        if ball.x < 0:
            right_score += 1
            ball.reset()
        elif ball.x > width:
            left_score += 1
            ball.reset()
        paint.draw()
        win = 0
        # Показва на кого да се присъди победата
        if left_score == 10:
            win = 1
            rand_x = random.randint(paddle_width + 10, width - paddle_width - 10)
            rand_y = random.randint(0, height - 10)
            left_score = 0
            right_score = 0
            window_text = "Left player wins!"
        elif right_score == 10:
            rand_x = random.randint(paddle_width + 10, width - paddle_width - 10)
            rand_y = random.randint(0, height - 10)
            win = 1
            left_score = 0
            right_score = 0
            window_text = "Right player wins!"
        if win == 1:
            text = score_font.render(window_text, 1, white)
            window.blit(text, (width//2 - text.get_width() //
                            2, height//2 - text.get_height()//2))
            # Рисува текста за победа
            pygame.display.update()
            ball.reset()
            left_paddle.reset()
            right_paddle.reset()
            pygame.time.delay(3000)


    pygame.quit()


if __name__ == '__main__':
    main()

