from translate_api import translator, detect_lang, get_definition
from database import *
import random
import sys


try:
    with open("preset_words.txt", "r", encoding="utf-8-sig") as infile:
        preset_words = [(line.strip().split()[0], line.strip().split()[1]) for line in infile.readlines()]
except FileNotFoundError:
    print("Отсутствует файл 'preset_words.txt'")
    sys.exit(1)


def display_start_message(response, storage):
    response.set_text("Здравствуй! Я бот, который помогает учить английский. Я могу переводить любые слова "
                      "и фразы, а позже вы можете добавлять их в свой личный словарь, после чего тренировать "
                      "с помощью различных упражнений.\n Список и описание упражнений можно посмотреть, "
                      "нажав на кнопку \"правила\". Также вы можете все стереть и начать заново с помощью "
                      "кнопки \"стереть данные\".\nДавайте начнем!")
    response = restart_dialogue(response)

    return response, storage


def restart_dialogue(response):
    # возвращаем диалог в изначальное состояние
    # добавляем основные кнопки
    response.set_buttons([{"title": "перевести", "hide": True},
                          {"title": "тренировка", "hide": True},
                          {"title": "последние слова", "hide": True},
                          {"title": "правила", "hide": True},
                          {"title": "стереть данные", "hide": True}])
    return response


def suggest_to_translate(response, storage):
    response.set_text("Введите слово или фразу, и я пришлю вам перевод")
    return response, storage


def display_translation(response, phrase, storage):
    lang = detect_lang(phrase)
    translation = translator(phrase, lang)
    response.set_text(translation + "\n\nДобавить в словарь?")
    response.set_buttons([{"title": "да"}, {"title": "нет"}])

    if lang == "ru-en":
        storage["current_word"] = translation.split("\n\n")[0]
        storage["current_translation"] = phrase
    elif lang == "en-ru":
        storage["current_word"] = phrase
        storage["current_translation"] = translation.split("\n\n")[0]

    return response, storage


def dictionary_addition(response, answer, storage):
    if answer == "да":
        data_base = DataBase()
        data_base.create_table(storage["session_id"])
        data_base.insert_word(storage["words_num"], storage["current_word"], storage["current_translation"])
        storage["words_num"] += 1

        response.set_text("OK!")
        storage.pop("answer_awaiting")
        response = restart_dialogue(response)

        data_base.close()
    elif answer == "нет":
        response.set_text("Ну ладно(")
        storage.pop("answer_awaiting")
        response = restart_dialogue(response)
    else:
        response.set_text("Я не понимаю твой ответ")

    return response, storage


def show_dict(response, storage):
    data_base = DataBase()
    data_base.create_table(storage["session_id"])
    dictionary = data_base.read_dict()
    if not dictionary:
        response.set_text("Извините, похоже, вы еще ничего не добавили в словарь.")
    else:
        response.set_text("\n\n".join(
            ["{} - {}".format(word, translation) for index, word, translation, completion in dictionary[:50][::-1]]))

    data_base.close()

    response = restart_dialogue(response)

    return response, storage


def choose_training(response, storage):
    response.set_text("Выберите тренировку")
    response.set_buttons([{"title": "слово-перевод", "hide": True},
                          {"title": "перевод-слово", "hide": True},
                          {"title": "собери слово", "hide": True},
                          {"title": "угадай слово", "hide": True},
                          {"title": "выход из раздела", "hide": True}])
    return response, storage


def erase_question(response, storage):
    response.set_text("Удалить данные?")
    response.set_buttons([{"title": "да"}, {"title": "нет"}])
    return response, storage


def confirm_erase(response, answer, storage):
    if answer == "да":
        data_base = DataBase()
        data_base.create_table(storage["session_id"])
        data_base.delete_dict()

        response.set_text("Ваш словарь был удален")
        storage.pop("answer_awaiting")
        response = restart_dialogue(response)

        data_base.close()
    elif answer == "нет":
        storage.pop("answer_awaiting")
        response.set_text("Словарь не был удален")
        response = restart_dialogue(response)
    else:
        response.set_text("Я не понимаю твой ответ")

    return response, storage


def launch_training(response, answer, storage):
    if answer == "слово-перевод":
        return word_translation_training(response, storage)
    elif answer == "перевод-слово":
        return translation_word_training(response, storage)
    elif answer == "собери слово":
        return collect_word_training(response, storage)
    elif answer == "угадай слово":
        return guess_word_training(response, storage)
    elif "выход" in answer:
        storage.pop("answer_awaiting")
        response.set_text("Возвращаемся в основной раздел")
        response = restart_dialogue(response)
        return response, storage
    else:
        response.set_text("Я не понимаю твой ответ")
        response.set_buttons([{"title": "слово-перевод", "hide": True},
                              {"title": "перевод-слово", "hide": True},
                              {"title": "собери слово", "hide": True},
                              {"title": "угадай слово", "hide": True},
                              {"title": "выход из раздела", "hide": True}])
        return response, storage


def pick_word(storage):
    data_base = DataBase()
    data_base.create_table(storage["session_id"])

    records = [record for record in data_base.select_uncompleted_words()]  # список слов для тренировки
    word, translation = random.choice(records)

    data_base.close()

    return word, translation, records


def create_buttons(option, records, lang):
    answer_position = random.randint(0, 3)  # позиция правильного ответа
    buttons = [{"hide": True}, {"hide": True}, {"hide": True}, {"hide": True}]
    buttons[answer_position]["title"] = option

    temp_preset_words = [item for item in preset_words if item not in records]

    for i in range(len(buttons)):
        if "title" not in buttons[i]:
            if len(records) >= 3:  # если есть чем заполнить варианты
                fill_record = random.choice(records)
                del records[records.index((fill_record[0], fill_record[1]))]
            else:
                fill_record = random.choice(temp_preset_words)
                del temp_preset_words[temp_preset_words.index((fill_record[0], fill_record[1]))]
            buttons[i]["title"] = fill_record[1] if lang == "ru" else fill_record[0]

    return buttons


def word_translation_training(response, storage):
    word, translation, records = pick_word(storage)
    buttons = create_buttons(translation, records, "ru")

    response.set_text("Выберите верный перевод слова \"{}\"".format(word))
    response.set_buttons(buttons)
    storage["current_answer"] = translation
    storage["answer_awaiting"] = "training_answer"
    return response, storage


def translation_word_training(response, storage):
    word, translation, records = pick_word(storage)
    buttons = create_buttons(word, records, "en")

    response.set_text("Выберите верный перевод слова \"{}\"".format(translation))
    response.set_buttons(buttons)
    storage["current_answer"] = word
    storage["answer_awaiting"] = "training_answer"
    return response, storage


def collect_word_training(response, storage):
    word, _, _ = pick_word(storage)
    letters = list(word)
    random.shuffle(letters)
    response.set_text("Составьте слово из перемешанных букв:\n" + " ".join(letters))
    storage["current_answer"] = word
    storage["answer_awaiting"] = "training_answer"
    return response, storage


def guess_word_training(response, storage):
    word, translation, records = pick_word(storage)
    buttons = create_buttons(word, records, "en")

    definition = get_definition(word, "en")
    if definition:
        response.set_text("Угадайте слово по его определению:\n{}".format(definition))
        response.set_buttons(buttons)
        storage["current_answer"] = word
        storage["answer_awaiting"] = "training_answer"
    else:
        response.set_text("К сожалению, я не могу найти определение слову \"{}\"".format(word))
        response.set_buttons([{"title": "слово-перевод", "hide": True},
                              {"title": "перевод-слово", "hide": True},
                              {"title": "собери слово", "hide": True},
                              {"title": "угадай слово", "hide": True},
                              {"title": "выход из раздела", "hide": True}])
        storage["answer_awaiting"] = "training"

    return response, storage


def check_answer(response, answer, storage):
    if answer == storage["current_answer"]:
        result = "Верно!"
    else:
        result = "Неверно! Правильный ответ: {}".format(storage["current_answer"])

    storage["answer_awaiting"] = "training"
    response.set_text("{}\n\nВыберите тренировку".format(result))
    response.set_buttons([{"title": "слово-перевод", "hide": True},
                          {"title": "перевод-слово", "hide": True},
                          {"title": "собери слово", "hide": True},
                          {"title": "угадай слово", "hide": True},
                          {"title": "выход из раздела", "hide": True}])
    return response, storage


def display_rules(response, storage):
    response.set_text("Здесь написаны правила")
    response = restart_dialogue(response)
    return response, storage


def handle_dialog(request, response, user_storage):
    if request.is_new_session:
        # пользователь общается с ботом впервые
        user_storage = {"session_id": request.session_id,
                        "words_num": 0}
        data_base = DataBase()
        data_base.create_table(user_storage["session_id"])
        data_base.close()
        return display_start_message(response, user_storage)
    else:
        if "answer_awaiting" in user_storage:  # бот ожидает от пользователя какой-то определенный ответ
            if user_storage["answer_awaiting"] == "translate":
                # любая строка, которую введет пользователь, будет переведена
                user_storage["answer_awaiting"] = "dictionary_add"
                translate_item = request.command
                return display_translation(response, translate_item, user_storage)
            elif user_storage["answer_awaiting"] == "dictionary_add":  # пользователь должен решить, добавлять в словарь или нет
                answer = request.command.lower()
                return dictionary_addition(response, answer, user_storage)
            elif user_storage["answer_awaiting"] == "erase":  # пользователь решает, удалять словарь или нет
                answer = request.command.lower()
                return confirm_erase(response, answer, user_storage)
            elif user_storage["answer_awaiting"] == "training":  # пользователь должен выбрать тренировку
                answer = request.command.lower()
                return launch_training(response, answer, user_storage)
            elif user_storage["answer_awaiting"] == "training_answer":  # пользователь должен ответить на задание
                answer = request.command.lower()
                return check_answer(response, answer, user_storage)

        elif request.command.lower() == "перевести":
            user_storage["answer_awaiting"] = "translate"
            return suggest_to_translate(response, user_storage)

        elif request.command.lower() == "тренировка":
            data_base = DataBase()
            data_base.create_table(user_storage["session_id"])
            uncompleted = data_base.select_uncompleted_words()
            data_base.close()
            if not uncompleted:
                response.set_text("Вы не можете тренировать слова, так как ваш словарь пуст, "
                                  "либо же вы уже выучили все слова")
                response = restart_dialogue(response)
                return response, user_storage
            else:
                user_storage["answer_awaiting"] = "training"
                return choose_training(response, user_storage)

        elif request.command.lower() == "последние слова":
            return show_dict(response, user_storage)

        elif request.command.lower() == "правила":
            return display_rules(response, user_storage)

        elif request.command.lower() == "стереть данные":
            user_storage["answer_awaiting"] = "erase"
            return erase_question(response, user_storage)

        # если пользователь вводит что-то другое, кроме запросов, просто переводим его сообщение
        else:
            user_storage["answer_awaiting"] = "dictionary_add"
            translate_item = request.command
            return display_translation(response, translate_item, user_storage)
