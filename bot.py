import asyncio
import io
import logging
import os
import random
from datetime import datetime
from aiohttp import web
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    LabeledPrice,
    PreCheckoutQuery,
    BufferedInputFile
)
from PIL import Image, ImageDraw, ImageFont

# Токен вашего бота поддержки
BOT_TOKEN = "8740416374:AAH-5SG5WK2lEW8Iy29pytxsFyNr0lVGebA"

# Ваш личный Telegram ID
ADMIN_ID = 6614617463

USERS_FILE = "users.txt"

# 100 разноплановых анекдотов
JOKES = [
    "— Ты кем работаешь?\n— Ландшафтным дизайнером.\n— Ого!\n— Да на бульдозере снег гребу.",
    "Вышел на пенсию. Денег нет, здоровья нет, времени полно. Сижу, кайфую.",
    "— Доктор, у меня бессонница, что делать?\n— Попробуйте считать овец.\n— Считал, дошел до миллиона, запутался, психанул, выпил кофе и пошел на работу.",
    "Уборка дома — это когда ты перекладываешь вещи с одного видного места на другое, менее заметное.",
    "Будильник звонит: «Пора вставать!»\nМозг: «Куда вставать? Лежи, мы ещё не придумали, зачем жить эту жизнь».",
    "— Почему опоздали на работу?\n— Проснулся, посмотрел в окно — погода шепчет: «Останься дома, поспи». А я с природой не спорю.",
    "В детстве думал, что взрослые покупают всё, что захотят, потому что у них много денег. Оказалось, они покупают капли в нос и обезболивающее.",
    "— Люся, ты где?\n— Я в пробке.\n— А где именно?\n— Да на кухне, штопор найти не могу!",
    "Деньги — они как чайки: прилетели, поорали, нагадили в душу и улетели.",
    "— Ты спортом занимаешься?\n— Да, у меня спортивная ходьба до холодильника с препятствиями в виде кота.",
    "Вчера случайно лёг спать вовремя. Проснулся в 4 утра с чувством, будто меня обманули.",
    "— Серега, ты чего такой грустный?\n— Да вот, зарплату дали...\n— Мало?\n— Нет, блин, много, теперь не знаю, на какую яхту наскрести — на надувную или из газеты сложить.",
    "Самый верный способ вспомнить, что ты забыл сделать — это лечь под теплое одеяло и только закрыть глаза.",
    "— Девушка, можно с вами познакомиться?\n— Мужчина, у меня дома три кота, ипотека и депрессия. Вы уверены, что вывезете этот сюжет?",
    "Купил абонемент в спортзал на год. Самое выгодное вложение: за 30 тысяч рублей я сходил туда один раз сфоткаться в зеркале.",
    "— Дорогой, тебе чай или кофе?\n— Давай кофе.\n— А нету, пей чай.",
    "На работе требуют опыт от 5 лет, возраст до 23 и стрессоустойчивость как у памятника.",
    "— Папа, а что такое альтернатива?\n— Ну смотри: решил ты разводить кур, купил цыплят, построил сарай, наводнение — все куры утонули.\n— И в чем альтернатива?\n— Утки, сынок. Надо было разводить уток.",
    "Я не ленивый. Я просто нахожусь в режиме энергосбережения.",
    "— Как твои дела?\n— Стабильно: денег нет, всё бесит, но держусь на кофе и сарказме.",
    "Стоматолог пациенту:\n— Вот и всё, зубик вырвали, с вас 5000 рублей.\n— За две секунды работы пять тысяч?!\n— Ну, если хотите, в следующий раз я могу тащить его два часа.",
    "Захожу в магазин только за хлебом — на кассе минус три тысячи и пакет с чипсами и средством для чистки ковров, которого у меня вообще нет.",
    "— Ты веришь в любовь с первого взгляда?\n— В моем возрасте уже верят в крепкий сон без похода в туалет.",
    "Планы на выходные: лежать так тихо, чтобы жизнь забыла о моем существовании и не подкинула новых проблем.",
    "— Официант, в моем супе муха!\n— Не переживайте, она не выпьет много вашего супа.",
    "Когда кот смотрит в пустой угол стены с диким ужасом, я на всякий случай тоже начинаю туда креститься.",
    "— Милый, я толстая?\n— Нет, что ты! Ты просто заметная женщина.",
    "С возрастом фраза «пойдём оторвёмся» означает поехать в строительный гипермаркет выбирать обои со скидкой.",
    "Решил начать новую жизнь с понедельника. Наступил вторник. Новая жизнь посмотрела на меня, вздохнула и ушла.",
    "— Алло, скорая? У меня депрессия!\n— Помойте посуду, вынесите мусор, погладьте шторы.\n— А это поможет?\n— Нет, но хоть дома чисто будет.",
    "Настоящая взрослая жизнь — это когда любимая сковородка радует больше, чем Новый год.",
    "— Папа, почему бабушка бегает по огороду зигзагами?\n— Кому бабушка, а кому теща! Не отвлекайся, подавай второй рожок.",
    "Женская логика: «Я обиделась на то, что ты не догадался, почему я на тебя обиделась вчера в моем сне».",
    "— Доктор, у меня болит голова.\n— А что вы вчера пили?\n— Водку, пиво, коньяк, шампанское и текилу.\n— Понятно, отравились овсяным печеньем.",
    "Работаю на трёх работах: на одной работаю, на второй устаю, на третьей сплю.",
    "— Мама, я женюсь!\n— На ком?\n— На соседке Маше!\n— Ой, только не на ней, она же страшная и готовить не умеет!\n— Мама, зато у нее в гараже «Ока» и дед самогон гонит!",
    "Каждый раз, когда я решаю начать экономить, ломается зуб, машина или жизнь.",
    "— Ты чего не спишь?\n— Да вот думаю: если помидор — это ягода, то кетчуп — это варенье?",
    "Купил умные весы. Они взвесили меня, помолчали три секунды и вывели на экран: «Пожалуйста, вставайте по одному».",
    "— Дорогой, у меня две новости: хорошая и плохая.\n— Начни с хорошей.\n— Подушка безопасности в нашей машине сработала идеально!",
    "Ничто так не бодрит с утра, как звонок будильника, прозвучавший через полтора часа после того, как ты должен был выйти.",
    "— Вы обвиняетесь в нанесении побоев сковородкой.\n— Гражданин судья, он сам налетел на нее! И так восемь раз подряд!",
    "Мой кот спит по 18 часов в сутки, потом просыпается, жрёт, орет дурным голосом и снова ложится спать. Вопрос: в какой момент эволюция свернула не туда, и почему я так не могу?",
    "— Ты кем видишь себя через 5 лет?\n— Человеком, который наконец-то выплатил кредит за телефон.",
    "Инструкция по открытию упаковки чипсов: потяните за края. Результат: чипсы на потолке, на полу, в коте, но не во рту.",
    "— Доктор, я постоянно разговариваю сам с собой.\n— Мешает?\n— Нет, но я такой душный собеседник, просто жуть.",
    "Идеальный вечер пятницы: включить фильм, открыть пиво, уснуть на пятнадцатой минуте.",
    "— Бабушка, а почему у тебя такие большие зубы?\n— Это чтобы пенсию быстрее пережевывать, внучек.",
    "У меня в голове столько мыслей, что иногда они устраивают драку за право быть первой высказанной глупостью.",
    "— Как вы расслабляетесь?\n— А я просто не напрягаюсь... Ладно, вру, ору в подушку.",
    "Идет мужик по улице, видит — на дереве висит объявление: «Продается собака. Умеет говорить, знает три языка, готовит борщ. Цена 500 рублей». Приходит по адресу, видит пса, спрашивает:\n— Ты правда говоришь?\n— Да, окончил Оксфорд, служил на границе, спасал людей из-под лавин...\nМужик в шоке поворачивается к хозяину:\n— Почему вы продаете такое сокровище за копейки?!\n— Да потому что он врет на каждом шагу! Нигде он не служил!",
    "— Доктор, сосед говорит, что за ночь может пять раз!\n— Ну так и вы говорите.",
    "Инспектор ГИБДД останавливает машину:\n— Вы превысили скорость, с вас штраф.\n— Товарищ инспектор, я спешил, чтобы бензин не кончился!",
    "— Семен Маркович, как ваше здоровье?\n— Не дождетесь!",
    "Разговаривают две собаки:\n— Мой хозяин такой умный, дрессированный!\n— Это как?\n— Ну вот я подхожу, лапу поднимаю — он мне кусок мяса дает.",
    "— Официант, почему в моем салате греческий только сыр?\n— Потому что оливки объявили дефолт и ушли.",
    "На приеме у психиатра:\n— Доктор, мне кажется, за мной постоянно кто-то следит.\n— И давно это началось?\n— С тех пор, как меня условно-досрочно освободили.",
    "— Вовочка, кто открыл Америку?\n— Колумб.\n— А кто написал войну и мир?\n— Толстой.\n— А кто разбил окно в коридоре?\n— Этого Колумб с Толстым точно не делали, честное слово!",
    "— Бабуль, я в армию ухожу!\n— Ой, внучек, а тебя там кормить-то будут? Давай я тебе мешок картошки с собой запеку.",
    "Идут два охотника по лесу. Вдруг навстречу медведь. Один бросает ружье и начинает затягивать шнурки на кроссовках.\nВторой ему шепчет:\n— Ты дурак? Ты все равно не побежишь быстрее медведя!\n— А мне и не надо быстрее медведя. Мне главное — бежать быстрее тебя.",
    "— Алло, это прачечная?\n— Это министерство культуры!",
    "В одесском трамвае:\n— Мужчина, вы сходите на следующей?\n— Сходят с ума, а я выхожу!\n— Ну так выходите скорее, не сводите меня с ума!",
    "— Девушка, а вашей маме зять не нужен?\n— Нет, у нас еще прошлый в подвале картошку перебирает.",
    "В самолете стюардесса выходит в салон:\n— Уважаемые пассажиры, кто-нибудь умеет управлять самолетом?\nТишина. Мужик поднимает руку:\n— Я в детстве бумажные запускал, пойдет?",
    "Два студента перед экзаменом:\n— Ты что-нибудь учил?\n— Нет, а ты?\n— Тоже нет.\n— Отлично, сдаем на коллективный разум.",
    "На птичьем рынке:\n— Мужик, продай хомяка!\n— Это не хомяк, это медвежонок, которого ты у меня в прошлом году купил!",
    "— Доктор, скажите честно: я жить буду?\n— Будете. Но вам это не понравится.",
    "— Товарищ сержант, рядовой Иванов по вашему приказу прибыл!\n— А почему через забор?\n— Так короче, товарищ сержант!",
    "— Слышал, ты машину купил?\n— Да, в кредит на 15 лет.\n— И как?\n— Теперь бензин нюхаю только по праздникам.",
    "Отец смотрит дневник сына:\n— Так, по физике 2, по химии 2, по физкультуре 2... А по пению 5?! Этот оболтус еще и поет?!",
    "— Почему вы не хотите работать в нашей компании?\n— Знаете, в графе «испытательный срок» у вас написано «пожизненно».",
    "Идет слон по пустыне, видит муравья:\n— Муравей, ты чего такой злой?\n— Отойди, слон, не до тебя, я качаюсь!",
    "— Дорогой, я сдала на права с десятого раза!\n— Молодец. Теперь машину продаем, покупаем танк.",
    "Жена мужу:\n— Ты совсем со мной не разговариваешь!\n— Люся, если я начну говорить, мы подеремся на первой же запятой.",
    "— Абрам, почему ты носишь часы на правой руке?\n— Потому что на левой у меня дырка на носке видна, когда я на них смотрю.",
    "Пациент выходит из кабинета врача:\n— Доктор, а эти таблетки точно помогут?\n— Мужчина, если не помогут, вернетесь — я вам другие нарисую.",
    "— Официант, это блюдо пахнет коньяком!\nОфициант отходит на шаг:\n— А сейчас?",
    "Разговаривают два кота на заборе:\n— Ты своего хозяина на сколько баллов оцениваешь?\n— На троечку: гладит нормально, но открывает банку с паштетом возмутительно медленно.",
    "— Ты кем в детстве мечтал стать?\n— Космонавтом.\n— А стал?\n— Сижу на балконе, курю, смотрю на звезды. В принципе, близко.",
    "Инспектор ДПС водителю:\n— Дыхните в трубочку.\n— Не буду, у меня астма.\n— Ладно, тогда пройдите по прямой линии.\n— Не могу, у меня плоскостопие.\n— Ну ладно, выходите из машины.\n— Не могу, я в стельку!",
    "На экзамене по вождению:\n— Вы сбили манекен на пешеходном переходе. Ваши действия?\n— Спрячу в багажник и поеду дальше?",
    "— Мой муж бросил пить, курить и ругаться матом!\n— Святой человек!\n— Нет, инсульт разбил.",
    "— Что вы делали в банке в три часа ночи с ломом в руках?\n— Проверял прочность несущих конструкций на общественных началах.",
    "Приходит мужик в магазин обуви:\n— Дайте мне ботинки на два размера меньше.\n— Зачем? Вам же жать будет!\n— Понимаете: дома жена пилит, на работе начальник зверь, дети двоечники. Единственная радость в жизни — прийти домой и снять эти чертовы ботинки!",
    "— Батюшка, а в пост интернет можно?\n— Можно, сын мой, только без картинок со скоромным.",
    "Учительница:\n— Дети, кто знает, как называется существо, которое питается исключительно растительной пищей?\nВовочка с задней парты:\n— Студент на стипендии!",
    "— Алло, полиция? В мою квартиру ломится грабитель!\n— А вы дома?\n— Да!\n— Ну так откройте, человеку неудобно через форточку лезть.",
    "Встречаются два старых одессита:\n— Моня, как твои дела с диетой?\n— Прекрасно! За неделю потерял триста рублей и покой.",
    "— Доктор, я постоянно мерзну!\n— Так застегните ширинку, сквозит же.",
    "Жена читает гороскоп:\n— Милый, тут написано, что на этой неделе тебя ждет большая удача!\nМуж из гаража:\n— Если ты наконец нашла второй носок от пары — это действительно чудо.",
    "— Дорогая, что у нас на ужин?\n— Котлеты из того, что ты вчера принес с рыбалки.\n— Но я вчера ничего не поймал!\n— Вот именно. Приятного аппетита.",
    "Кот смотрит на миску с сухим кормом, потом на хозяина:\n— Ты серьезно? Опять коричневые сухари? Я ради этого будил тебя в пять утра?!",
    "— Почему в шахматах королева ходит как угодно, а король только на одну клетку?\n— Потому что доска похожа на кухню, а трон один.",
    "— Скажите, в этом отеле есть Wi-Fi?\n— Только в холле и только если верить в чудеса.",
    "Судья:\n— Подсудимый, вы признаете себя виновным в краже сковороды?\n— Гражданин судья, какая сковорода? Я просто хотел погреть руки об ее ручку!",
    "— Молодой человек, вам билет в театр на балкон или в партер?\n— Мне в буфет, пожалуйста.",
    "Встречаются два карася в пруду:\n— Слышал, Михалыч червяка на крючке съел?\n— И что?\n— Да на сковородку поехал на гастроли.",
    "— Папа, а правда, что от интернета тупеют?\n— Гы-гы, сынок, лол, флекс, краш.",
    "В кабинете у терапевта:\n— На что жалуетесь?\n— На жизнь, доктор.\n— Это не ко мне, это к патологоанатому, он единственный, кто не торопит.",
    "— Дорогой, ты помнишь, какой сегодня день?\n— Конечно! Пятница!\n— Нет, сегодня день нашей свадьбы!\n— Одно другому не мешает, наливай."
]

# Награды: (Название, шанс, цвет карточки RGB)
ROULETTE_DATA = [
    ("👑 Королевская Утка", 0.005, (255, 215, 0)),    # Золотой (0.5%)
    ("🧰 2 Кейса", 0.030, (148, 0, 211)),             # Фиолетовый (3.0%)
    ("🦆 Скин Утки", 0.065, (30, 144, 255)),          # Синий (6.5%)
    ("🍭 5000 Леденцов", 0.250, (255, 105, 180)),     # Розовый (25.0%)
    ("🪙 5000 Монет", 0.250, (255, 215, 0)),          # Желтый (25.0%)
    ("💨 Ничего / Удачи!", 0.400, (105, 105, 105))     # Серый (40.0%)
]

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Кнопки для администратора
admin_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👥 Список игроков"), KeyboardButton(text="📊 Статистика")],
        [KeyboardButton(text="☕ Кофе автору + Рулетка (20 ⭐)"), KeyboardButton(text="😂 Анекдот")],
        [KeyboardButton(text="📖 Подсказка по командам")]
    ],
    resize_keyboard=True
)

# Кнопки для обычных игроков
user_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="☕ Кофе автору + Рулетка (20 ⭐)")],
        [KeyboardButton(text="ℹ️ Об игре"), KeyboardButton(text="😂 Анекдот")]
    ],
    resize_keyboard=True
)

def save_user(user_id, username, full_name):
    try:
        users = {}
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if ":" in line:
                        p = line.split(":", 1)
                        users[p[0].strip()] = p[1].strip()

        uname = f"@{username}" if username else "нет username"
        users[str(user_id)] = f"{uname} | {full_name or 'Аноним'}"

        with open(USERS_FILE, "w", encoding="utf-8") as f:
            for uid, info in users.items():
                f.write(f"{uid}:{info}\n")
    except Exception as e:
        logging.error(f"Ошибка сохранения: {e}")

# Генерация GIF рулетки с плавной остановкой на выигранном призе
def generate_roulette_gif(winning_item_title: str) -> io.BytesIO:
    width, height = 480, 160
    card_w, card_h = 130, 110
    card_gap = 15
    total_step = card_w + card_gap

    names = [item[0] for item in ROULETTE_DATA]
    color_map = {item[0]: item[2] for item in ROULETTE_DATA}

    tape = [random.choice(names) for _ in range(18)]
    winning_index = 18
    tape.append(winning_item_title)
    tape += [random.choice(names) for _ in range(6)]

    target_center_x = width // 2
    final_offset = (winning_index * total_step) + (card_w // 2) - target_center_x

    frames = []
    font = ImageFont.load_default()

    total_frames = 26
    for f in range(total_frames):
        progress = f / (total_frames - 1)
        ease = 1 - (1 - progress) ** 2.8
        current_offset = int(final_offset * ease)

        img = Image.new("RGB", (width, height), (22, 24, 30))
        draw = ImageDraw.Draw(img)

        draw.rectangle([5, 5, width - 6, height - 6], outline=(50, 55, 70), width=2)

        for i, title in enumerate(tape):
            x1 = 20 + i * total_step - current_offset
            x2 = x1 + card_w
            y1 = 25
            y2 = y1 + card_h

            if x2 < -60 or x1 > width + 60:
                continue

            color = color_map.get(title, (100, 100, 100))
            draw.rounded_rectangle([x1, y1, x2, y2], radius=8, fill=(35, 38, 48), outline=color, width=2)

            words = title.split()
            line1 = " ".join(words[:2]) if len(words) > 1 else title
            line2 = " ".join(words[2:]) if len(words) > 2 else ""

            draw.text((x1 + 10, y1 + 35), line1, fill=(240, 240, 240), font=font)
            if line2:
                draw.text((x1 + 10, y1 + 55), line2, fill=color, font=font)

        # Центральный указатель стрелки
        cx = width // 2
        draw.polygon([(cx - 9, 8), (cx + 9, 8), (cx, 24)], fill=(255, 69, 0))
        draw.polygon([(cx - 9, height - 8), (cx + 9, height - 8), (cx, height - 24)], fill=(255, 69, 0))
        draw.line([(cx, 24), (cx, height - 24)], fill=(255, 69, 0), width=2)

        frames.append(img)

    for _ in range(5):
        frames.append(frames[-1])

    output = io.BytesIO()
    frames[0].save(
        output,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=90,
        loop=0
    )
    output.seek(0)
    return output

# Команда /start
@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    save_user(message.from_user.id, message.from_user.username, message.from_user.full_name)

    if message.from_user.id == ADMIN_ID:
        await message.answer(
            "👑 **Панель администратора готова к работе!**\n\n"
            "Используйте кнопки под строкой ввода для управления ботом.",
            reply_markup=admin_keyboard,
            parse_mode="Markdown"
        )
        return

    await message.answer(
        "👋 Привет! Это официальная служба поддержки игры **Bouncy Pickaxe**.\n\n"
        "💬 Напишите сюда свой вопрос, баг или отзыв — разработчик ответит прямо в этом чате!\n\n"
        "☕ Нажмите **«☕ Кофе автору + Рулетка (20 ⭐)»**, чтобы угостить автора кофе и испытать удачу в визуальной рулетке!",
        reply_markup=user_keyboard,
        parse_mode="Markdown"
    )

# 1. Отправка инвойса на 20 звёзд
@dp.message(F.text.in_(["☕ Кофе автору + Рулетка (20 ⭐)", "/coffee", "/donate"]))
async def coffee_invoice(message: types.Message):
    save_user(message.from_user.id, message.from_user.username, message.from_user.full_name)

    prices = [LabeledPrice(label="Чашка кофе разработчику + Рулетка", amount=20)]

    await bot.send_invoice(
        chat_id=message.chat.id,
        title="☕ Чашка кофе разработчику",
        description=(
            "Спасибо за поддержку игры Bouncy Pickaxe на 20 ⭐!\n\n"
            "В подарок вы моментально крутите рулетку с призами:\n"
            "• 👑 Королевская Утка (0.5%)\n"
            "• 🧰 2 Кейса (3%)\n"
            "• 🦆 Скин Утки (6.5%)\n"
            "• 🍭 5000 Леденцов (25%)\n"
            "• 🪙 5000 Монет (25%)\n"
            "• 💨 Ничего / Удачи!"
        ),
        payload="coffee_roulette_visual",
        currency="XTR",
        prices=prices,
        provider_token=""
    )

# 2. Подтверждение платежа
@dp.pre_checkout_query()
async def process_pre_checkout(pre_checkout: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout.id, ok=True)

# 3. Успешная оплата: генерация анимации и выдача уведомлений
@dp.message(F.successful_payment)
async def process_roulette_spin(message: types.Message):
    user = message.from_user
    save_user(user.id, user.username, user.full_name)

    prizes, weights, _ = zip(*[(item[0], item[1], item[2]) for item in ROULETTE_DATA])
    dropped_prize = random.choices(prizes, weights=weights, k=1)[0]

    wait_msg = await message.answer("☕ **Спасибо за поддержку!** ❤️\n🎰 *Заряжаем барабан рулетки...*", parse_mode="Markdown")

    loop = asyncio.get_event_loop()
    gif_bytes = await loop.run_in_executor(None, generate_roulette_gif, dropped_prize)
    gif_file = BufferedInputFile(gif_bytes.getvalue(), filename="roulette.gif")

    caption_text = (
        f"🎰 **РУЛЕТКА ОСТАНОВИЛАСЬ!**\n\n"
        f"🎯 Выпало: **{dropped_prize}**\n\n"
    )
    if "Ничего" in dropped_prize:
        caption_text += "В этот раз не повезло, но разработчик искренне благодарен за поддержку игры!"
    else:
        caption_text += "🎉 Поздравляем! Разработчик уже получил ваш выигрыш и выдаст награду прямо в этом чате."

    await wait_msg.delete()
    await message.answer_animation(animation=gif_file, caption=caption_text, parse_mode="Markdown")

    # Уведомление вам с готовой кнопкой/шаблоном для ответа
    admin_alert = (
        "🚨 **ДОНАТ 20 ЗВЁЗД + РУЛЕТКА!** 🚨\n\n"
        f"👤 **Игрок:** {user.full_name} (@{user.username or 'нет username'})\n"
        f"🆔 **ID:** `{user.id}`\n"
        f"💰 **Оплата:** 20 ⭐ Telegram Stars\n"
        f"🎁 **Выпало:** {dropped_prize}\n\n"
        "👉 Чтобы начислить приз или написать игроку, используйте:\n`/send " + str(user.id) + " Ваш текст`"
    )
    await bot.send_message(chat_id=ADMIN_ID, text=admin_alert, parse_mode="Markdown")

# Об игре
@dp.message(F.text.in_(["ℹ️ Об игре", "/about", "/game"]))
async def about_game(message: types.Message):
    text = (
        "⛏ **Bouncy Pickaxe** — динамичная аркадная игра!\n\n"
        "✨ *Советы:* прыгайте выше, собирайте бонусы и прокачивайте кирку.\n"
        "🐞 Если игра крашнулась или нашли баг — напишите прямо сюда текст со скриншотом!"
    )
    await message.answer(text, parse_mode="Markdown")

# Помощь администратору
@dp.message(F.chat.id == ADMIN_ID, F.text.in_(["📖 Подсказка по командам", "/help", "/admin"]))
async def show_help(message: types.Message):
    help_text = (
        "🛠 **Панель управления администратора:**\n\n"
        "👥 `/users` — список зарегистрированных игроков\n"
        "📊 `/stats` — число игроков в базе\n"
        "💬 `/send <ID> <сообщение>` — написать игроку по ID\n"
        "📢 `/broadcast <сообщение>` — рассылка всем игрокам\n"
        "😂 `/joke` — анекдот\n\n"
        "💡 *Как ответить:* нажмите Reply на сообщение игрока или используйте команду `/send ID текст`"
    )
    await message.answer(help_text, parse_mode="Markdown")

# Статистика
@dp.message(F.chat.id == ADMIN_ID, F.text.in_(["📊 Статистика", "/stats"]))
async def get_stats(message: types.Message):
    if not os.path.exists(USERS_FILE):
        await message.answer("📊 База пуста (0 пользователей).")
        return

    with open(USERS_FILE, "r", encoding="utf-8") as f:
        count = sum(1 for line in f if ":" in line)

    await message.answer(f"📊 Всего игроков в базе: **{count}**", parse_mode="Markdown")

# Список игроков
@dp.message(F.chat.id == ADMIN_ID, F.text.in_(["👥 Список игроков", "/users"]))
async def list_users(message: types.Message):
    if not os.path.exists(USERS_FILE):
        await message.answer("👥 В базе пока нет игроков.")
        return

    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f if ":" in l]

        if not lines:
            await message.answer("👥 В базе пока нет игроков.")
            return

        text = f"👥 **Список пользователей (всего {len(lines)}):**\n\n"
        for line in lines[-40:]:
            parts = line.split(":", 1)
            uid = parts[0].strip()
            info = parts[1].strip()
            text += f"• `{uid}` — {info}\n"

        text += "\nНаписать игроку: `/send <ID> <текст>`"
        await message.answer(text, parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"❌ Ошибка чтения: {e}")

# Анекдоты
@dp.message(F.text.in_(["😂 Анекдот", "/joke", "/anekdot", "/шутка"]))
async def send_joke(message: types.Message):
    save_user(message.from_user.id, message.from_user.username, message.from_user.full_name)
    joke = random.choice(JOKES)
    await message.answer(joke)

# Прямая отправка игроку по ID
@dp.message(F.chat.id == ADMIN_ID, Command("send"))
async def send_by_id(message: types.Message):
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.answer("Формат: `/send <ID> <текст>`", parse_mode="Markdown")
        return

    target_id = args[1].strip()
    msg_text = args[2].strip()

    try:
        await bot.send_message(chat_id=target_id, text=f"👨‍💻 **Ответ от службы поддержки:**\n\n{msg_text}", parse_mode="Markdown")
        await message.answer("✅ Доставлено!")
    except Exception as e:
        await message.answer(f"❌ Не удалось доставить: {e}")

# Рассылка всем
@dp.message(F.chat.id == ADMIN_ID, Command("broadcast"))
async def broadcast_msg(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Формат: `/broadcast <текст рассылки>`", parse_mode="Markdown")
        return

    text = args[1].strip()
    if not os.path.exists(USERS_FILE):
        await message.answer("База пользователей пуста.")
        return

    with open(USERS_FILE, "r", encoding="utf-8") as f:
        users = [l.split(":", 1)[0].strip() for l in f if ":" in l]

    sent = 0
    for uid in users:
        try:
            await bot.send_message(chat_id=uid, text=f"📢 **Новости игры Bouncy Pickaxe:**\n\n{text}", parse_mode="Markdown")
            sent += 1
            await asyncio.sleep(0.05)
        except Exception:
            pass

    await message.answer(f"✅ Рассылка доставлена {sent} из {len(users)} игроков.")

# Ответ через Reply администратора
@dp.message(F.chat.id == ADMIN_ID, F.reply_to_message)
async def reply_handler(message: types.Message):
    target_id = None
    reply = message.reply_to_message

    if reply.forward_from:
        target_id = reply.forward_from.id
    elif reply.text and "ID: `" in reply.text:
        try:
            target_id = reply.text.split("ID: `")[1].split("`")[0]
        except Exception:
            pass

    if target_id:
        try:
            await bot.send_message(
                chat_id=target_id,
                text=f"👨‍💻 **Ответ службы поддержки:**\n\n{message.text or 'Ответ во вложении'}"
            )
            if message.photo:
                await bot.send_photo(chat_id=target_id, photo=message.photo[-1].file_id)
            elif message.document:
                await bot.send_document(chat_id=target_id, document=message.document.file_id)
            await message.answer("✅ Ответ передан игроку!")
        except Exception as e:
            await message.answer(f"❌ Ошибка отправки: {e}")
    else:
        await message.answer("⚠️ Не удалось определить ID игрока. Ответьте командой:\n`/send <ID> <текст>`", parse_mode="Markdown")

# Входящие сообщения игроков
@dp.message(F.chat.id != ADMIN_ID)
async def handle_user_ticket(message: types.Message):
    save_user(message.from_user.id, message.from_user.username, message.from_user.full_name)

    time_now = datetime.now().strftime("%H:%M:%S")
    await message.answer(f"✅ Ваше сообщение получено в {time_now}! Разработчик ответит вам прямо в этом чате.")

    user_info = (
        f"📩 **Новое обращение в поддержку!**\n"
        f"Имя: {message.from_user.full_name}\n"
        f"Username: @{message.from_user.username or 'скрыт'}\n"
        f"ID: `{message.from_user.id}`\n"
        f"Время: {time_now}\n"
        f"➖➖➖➖➖➖➖➖➖➖\n"
        f"👇 *Текст сообщения:*"
    )

    try:
        await bot.send_message(chat_id=ADMIN_ID, text=user_info, parse_mode="Markdown")
        await message.copy_to(chat_id=ADMIN_ID)
    except Exception as e:
        logging.error(f"Ошибка пересылки: {e}")

# Веб-сервер для Render и UptimeRobot
async def health_check(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    print("Бот поддержки запущен!")
    await start_web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
