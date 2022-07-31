SITE_URL = "http://localhost:3000/"
EMAIL_VERIFICATION_PATH = "register/verify/?id={}&token={}"
PASSWORD_RESET_PATH = "password-reset/?id={}&token={}"
EMAIL_VERIFICATION_MESSAGE = \
    {
        "subject": "Подтвердите ваш почтовый адрес",
        "message": f"Спасибо за регистрацию на сайте That1Mango. Перейдите по ссылке, чтобы продолжить регистрацию.\n"
                   f"{SITE_URL}{EMAIL_VERIFICATION_PATH}\n"
                   f"Не отвечайте на это письмо, оно сгенерировано автоматически."
    }
PASSWORD_RESET_MESSAGE = \
    {
        "subject": "Сброс пароля",
        "message": f"Подтвердите сброс пароля на сайте That1Mango. Перейдите по ссылке, чтобы сбросить пароль.\n"
                   f"{SITE_URL}{PASSWORD_RESET_PATH}\n"
                   f"Не отвечайте на это письмо, оно сгенерировано автоматически."
    }
