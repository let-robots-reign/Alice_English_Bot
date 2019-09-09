def handle_dialog(request, response, user_storage):
    if request.is_new_session:
        user_storage = {}
        # пользователь общается с ботом впервые
        return setting_up(response), user_storage
    else:
        # обрабатываем ответы пользователя
        if "lang" not in user_storage:
            if request.command.lower() == "русский":
                user_storage["lang"] = "ru"
            elif request.command.lower() == "english":
                user_storage["lang"] = "en"
            return display_start_message(response, user_storage), user_storage

        elif "answer_awaiting" in user_storage:  # бот ожидает от пользователя какой-то определенный ответ
            if user_storage["answer_awaiting"] == "translate":
                # любая строка, которую введет пользователь, будет переведена
                user_storage["answer_awaiting"] = "dictionary_add"
                return display_translation(response, user_storage), user_storage
            elif user_storage["answer_awaiting"] == "dictionary_add":  # пользователь должен решить, добавлять в словарь или нет
                return dictionary_addition(response, user_storage), user_storage
            elif user_storage["answer_awaiting"] == "erase":
                return erase_question(response), user_storage

        elif request.command.lower() == "перевести":
            user_storage["answer_awaiting"] = "translate"
            return suggest_to_translate(response), user_storage

        elif request.command.lower() == "словарь":
            return display_dictionary(response, user_storage), user_storage

        elif request.command.lower() == "правила":
            return display_rules(response), user_storage

        elif request.command.lower() == "стереть данные":
            user_storage["answer_awaiting"] = "erase"
            return


def setting_up(response):
    response.set_text("Выберите язык, на котором я буду с вами говорить.\n\n"
                      "Choose the language I will speak.")
    response.set_buttons([{"title": "Русский", "hide": True},
                          {"title": "English", "hide": True}])
    return response


def display_start_message(response, storage):
    if "lang" not in storage:
        response.set_text("Вы еще не выбрали язык, на котором я буду говорить.\n\n"
                          "You haven't chosen the language I'll be speaking.")
    elif storage["lang"] == "ru":
        response.set_text("Здравствуй! Я бот, который помогает учить английский. Я могу переводить любые слова "
                          "и фразы, а позже вы можете добавлять их в свой личный словарь, после чего тренировать "
                          "с помощью различных упражнений.\n Список и описание упражнений можно посмотреть, "
                          "нажав на кнопку \"правила\". Также вы можете все стереть и начать заново с помощью "
                          "кнопки \"стереть данные\".\nДавайте начнем!")
    elif storage["lang"] == "en":
        response.set_text("Hello! I'm a bot that is constructed for learning English. I can translate any word or "
                          "phrase for you, and after that you can add it to your dictionary and learn with several "
                          "types of trainings whenever you want.\nYou can look up the list of trainings via /rules "
                          "command. Also, you can reset all your data and start from the beginning using /reset "
                          "command.\nLet's get started!")

    if "lang" not in storage:
        response.set_buttons([{"title": "Русский", "hide": True},
                              {"title": "English", "hide": True}])
    else:
        response.set_buttons([{"title": "перевести", "hide": True},
                              {"title": "тренировка", "hide": True},
                              {"title": "словарь", "hide": True},
                              {"title": "правила", "hide": True},
                              {"title": "стереть данные", "hide": True}])

    return response


def suggest_to_translate(response):
    response.set_text("Введите слово или фразу, и я пришлю вам перевод")


def display_translation(response, storage):
    pass


def dictionary_addition(response, user_storage):
    pass


def erase_question(response):
    pass


def display_dictionary(response, storage):
    pass


def display_rules(response):
    pass
