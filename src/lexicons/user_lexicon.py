MENU_LEXICON = {
    'get_last_incidents': 'Получить последние инциденты 📜',
    'get_incident_by_id': 'Получить инцидент по id / ключу 🔍',
    'account': 'Личный кабинет 💼',
    'settings': 'Настройки ⚙️',
    'users': 'Пользователи 👥'
}

USER_LIST_LEXICON = {
    'user_info_kb': {
        'close_session': 'Завершить сессию',
        'generate_new_password': 'Выдать новый пароль',
        'delete_user': 'Удалить пользователя',
        'back_to_user_list': 'Назад'
    },
    'answers': {
        'user': {
            'session_closed': 'ℹ️ <b>Администратор принудительно завершил Вашу сессию</b>',
            'new_password_created': f'ℹ️ <b>Администратор выдал Вам новый пароль:</b> <tg-spoiler>{{new_password}}</tg-spoiler>\n'
                                    f'Войти в систему можно, прописав /login\n\n'
                                    f'⚠️ Сообщение с паролем удалится через 5 мин, <b>сохраните пароль!</b>',
            'new_password_created_hidden': f'<b>Администратор выдал Вам новый пароль.</b>\n\n'
                                           f'Пароль скрыт в целях безопасности.\n'
                                           f'Войти в систему можно, прописав /login',
            'user_deleted': 'ℹ️ <b>Администратор удалил Вас из системы.</b>'
        },
        'admin': {
            'session_closed': f'ℹ️ <b>Сессия для пользователя {{username}} успешно завершена!</b>',
            'new_password_created': f'ℹ️ <b>Новый пароль для пользователя {{username}} успешно создан!</b>\n'
                                    f'Его сессия была завершена.',
            'confirm_user_deletion': f'Вы уверены, что хотите <b>удалить пользователя</b> {{username}}?',
            'user_deleted': f'ℹ️ <b>Пользователь {{username}} успешно удалён!</b>'
        }
    }
}
