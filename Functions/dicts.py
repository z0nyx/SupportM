import disnake

dict_prime_times = {
    1: '6:00-12:00',
    2: '12:00-18:00',
    3: '18:00-00:00',
    4: '00-6:00',
    0: 'Отсутствует'
}

yes_no_dict = {
    1: "Активен",
    0: "Отсутствует"
}

dict_bool = {
    True: "🟢",
    False: "⚪"
}


def generate_support_profile_post(
        guild: disnake.Guild,
        member: disnake.Member
):
    post = {
        "guild_id": guild.id,
        "member_id": member.id,
        "voice": 0,  # скок войс актива
        "prime_voice": 0,  # скок по прайм тайму. Онли неделя
        "verify": 0,  # верификаций. Всего
        "verify_week": 0,  # верификации. За неделю.
        "prime_time": 0,  # когда прайм тайм
        "rating": 0,  # рейтинг
        "rating_count": 0  # кол-во отзывов
    }
    # Сбрасывается раз в неделю: верификации за неделю, время насиженное в прайм тайм
    return post

