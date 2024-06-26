SETTINGS_LEXICON = {
    'settings_menu': f'<b>Настройки ⚙️:</b>\n\n'
                     f'Интервал между проверками инцидентов: <b>{{pause_time}} сек</b>\n'
                     f'Часовой пояс: <b>{{time_zone}}</b>\n'
                     f'Сбор инцидентов: <b>{{is_launch}}</b>',
    'pause_time': {
        'info': '<b>Укажите новый интервал следующим сообщением.</b>\n'
                'Например: 5 (5 секунд).',
        'successfully': f'<b>Интервал между проверками инцидентов успешно изменён!</b>\n\n'
                        f'Новое значение: {{new_pause_time}} сек',
        'incorrect': '<b>Вы указали не допустимое значение для интервала!</b>\n\n'
                     'Пожалуйста, укажите целочисленное положительное значение\n'
                     'Или напишите /cancel, чтобы отменить операцию'
    },
    'time_zone': {
        'info': '<b>Укажите новый часовой пояс в диапазоне от -12 до 13.</b>\n'
                'Например: 3 (Московское).',
        'successfully': f'<b>Часовой пояс успешно изменён!</b>\n\n'
                        f'Новое значение: {{new_time_zone}}',
        'incorrect': '<b>Вы указали не допустимое значение для часового пояса!</b>\n\n'
                     'Пожалуйста, укажите целочисленное значение от -12 до 13\n'
                     'Или напишите /cancel, чтобы отменить операцию'
    },
    'reg_pass': {
        'new_pass': f'<b>Новый код регистрации успешно создан:</b> <tg-spoiler>{{new_pass}}</tg-spoiler>'
    },
    'init': {
        'settings_already_initialized': 'Настройка уже была произведена ранее.',
        'successful_init': f'Начальная настройка бота прошла успешно.\n\n'
                           f'Пароль для регистрации пользователей:\n'
                           f'<tg-spoiler>{{registration_password}}</tg-spoiler>'
    }
}
