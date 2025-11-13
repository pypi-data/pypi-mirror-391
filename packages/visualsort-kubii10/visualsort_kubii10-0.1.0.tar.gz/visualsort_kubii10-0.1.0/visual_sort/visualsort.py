import random, time, pygame

n = 10
def shuffle_numbers(n):
    return [random.randint(0, 30) for _ in range(n)]
operation_count = 0

screen_width = 1800
screen_height = 600

pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Random Bars Visualization")
screen.fill((0, 0, 0))


def shuffle_info():
    screen.fill((0, 0, 0))
    font = pygame.font.Font(None, 36)
    text = font.render(f"Shuffling {n} numbers", True, (255, 255, 255))
    text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2))
    screen.blit(text, text_rect)
    pygame.display.flip()
    time.sleep(1)

def visualise(n, array, highlight=None):
    font = pygame.font.Font(None, 36)
    screen.fill((0, 0, 0))
    for i in range(n):
        global operation_count
        operation_count += 1
        if highlight and i in highlight:
            color = (0, 255, 0) 
        else:
            color = (255, 255, 255)
        pygame.draw.rect(
            screen,
            color,
            ((screen_width / 2 - n * 10 / 2) + i * 10, screen_height / 2 - array[i] * 5, 5, array[i] * 5)
        )
    
    text = font.render(f"Total operations: {operation_count}", True, (255, 255, 255))
    screen.blit(text, (10, 10))
    
    pygame.display.flip()

def radix_sort(array):
    max1 = max(array)
    exp = 1
    while max1 // exp > 0:
        counting_sort(array, exp)
        exp *= 10

def counting_sort(array, exp):
    n = len(array)
    output = [0] * n
    count = [0] * 10

    for i in range(n):
        index = (array[i] // exp) % 10
        count[index] += 1

    for i in range(1, 10):
        count[i] += count[i - 1]

    for i in range(n - 1, -1, -1):
        index = (array[i] // exp) % 10
        output[count[index] - 1] = array[i]
        count[index] -= 1

    for i in range(n):
        array[i] = output[i]
        print(array)
        time.sleep(0.01)
        visualise(n, array, highlight=(i,))

def bubble_sort(array):
    for i in range(len(array)):
        for j in range(0, len(array) - i - 1):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
            if array[j] > array[j + 1]:
                array[j], array[j + 1] = array[j + 1], array[j]
                print(array)
                visualise(n, array, highlight=(j, j + 1))

def insert_sort(array):
    for i in range(1, len(array)):
        key = array[i]
        j = i - 1
        while j >= 0 and key < array[j]:
            array[j + 1] = array[j]
            j -= 1
        array[j + 1] = key

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        visualise(n, array, highlight=(j + 1,))
        time.sleep(0.01)

random_numbers = shuffle_numbers(n)
shuffle_info()
bubble_sort(random_numbers)

random_numbers = shuffle_numbers(n)
shuffle_info()
radix_sort(random_numbers)

random_numbers = shuffle_numbers(n)
shuffle_info()
insert_sort(random_numbers)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
print(operation_count)
