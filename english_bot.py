from translate_api import translator, detect_lang
from database import *


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
    storage["current_word"] = phrase
    storage["current_translation"] = "\n\n".join(translation.split("\n\n")[:-1])
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
        response.set_text("Последние добавленные слова:"
                          "\n".join(
            ["{} - {}".format(word, translation) for index, word, translation in dictionary[:50][::-1]]))

    data_base.close()

    response = restart_dialogue(response)

    return response, storage


def erase_question(response, storage):
    response.set_text("Удалить данные?")
    response.set_buttons([{"title": "да"}, {"title": "нет"}])
    return response, storage


def confirm_erase(response, answer, storage):
    if answer == "да":
        response.set_text("OK! Удалил")
        storage.pop("answer_awaiting")
        response = restart_dialogue(response)
    elif answer == "нет":
        response.set_text("Ну ладно( не буду удалять")
        storage.pop("answer_awaiting")
        response = restart_dialogue(response)
    else:
        response.set_text("Я не понимаю твой ответ")

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
            elif user_storage["answer_awaiting"] == "erase":
                user_storage["answer_awaiting"] = "confirm_erase"
                return erase_question(response, user_storage)
            elif user_storage["answer_awaiting"] == "confirm_erase":
                answer = request.command.lower()
                return confirm_erase(response, answer, user_storage)

        elif request.command.lower() == "перевести":
            user_storage["answer_awaiting"] = "translate"
            return suggest_to_translate(response, user_storage)

        elif request.command.lower() == "последние слова":
            return show_dict(response, user_storage)

        elif request.command.lower() == "правила":
            return display_rules(response, user_storage)

        elif request.command.lower() == "стереть данные":
            user_storage["answer_awaiting"] = "erase"
            return
