import os
import itertools
import threading
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PyPDF2 import PdfFileWriter, PdfFileReader
from PIL import Image
from tqdm import tqdm

# Пустой пароль для шифрования PDF
empty_password = ''

# Функция для создания PDF файла с изображением и ссылкой
def create_pdf(image_path, url, output_file):
    c = canvas.Canvas(output_file, pagesize=letter)

    # Определите размеры страницы PDF
    page_width, page_height = letter

    # Откройте изображение с помощью Pillow
    image = Image.open(image_path)

    # Установите размер изображения в точности равным размеру страницы PDF, без сохранения пропорций
    image = image.resize((int(page_width), int(page_height)))

    # Вставляем изображение на страницу без сохранения пропорций
    c.drawImage(image_path, 0, 0, width=page_width, height=page_height, mask=[255, 255, 255, 255, 255, 255])

    # Создайте область для ссылки, охватывающую всю страницу
    c.linkURL(url, (0, 0, page_width, page_height), thickness=0)

    # Завершите создание PDF файла
    c.showPage()
    c.save()

# Функция для добавления шифрования к PDF файлу
def encrypt_pdf(input_file, output_file):
    pdf_reader = PdfFileReader(input_file)
    pdf_writer = PdfFileWriter()
    pdf_writer.appendPagesFromReader(pdf_reader)
    pdf_writer.encrypt(empty_password)

    with open(output_file, 'wb') as output_pdf:
        pdf_writer.write(output_pdf)

# Функция для обработки каждой комбинации изображения и ссылки
def process_combination(image_path, url, index):
    # Используем простой индекс для именования выходных файлов
    unencrypted_output_file = f"{output_dir}/{index}_unencrypted.pdf"
    create_pdf(image_path, url, unencrypted_output_file)

    # Шифруем созданный PDF файл с пустым паролем
    encrypted_output_file = f"{output_dir}/{index}_encrypted.pdf"
    encrypt_pdf(unencrypted_output_file, encrypted_output_file)

    # Удалите нешифрованный файл
    os.remove(unencrypted_output_file)

# Чтение ссылок из текстового файла
with open('links.txt', 'r') as file:
    links = file.read().splitlines()

# Перечисление всех изображений в папке 'picture'
image_dir = 'picture'
image_files = [os.path.join(image_dir, filename) for filename in os.listdir(image_dir)]

# Генерация всех возможных комбинаций изображений и ссылок
combinations = list(itertools.product(image_files, links))

# Создание выходной директории, если она не существует
output_dir = 'output'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Запуск многопоточной обработки комбинаций с использованием tqdm
threads = []
for index, combination in enumerate(tqdm(combinations), start=1):
    image_path, url = combination
    thread = threading.Thread(target=process_combination, args=(image_path, url, index))
    threads.append(thread)
    thread.start()

# Ожидание завершения всех потоков
for thread in threads:
    thread.join()

input("Готово!")
