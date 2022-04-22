ranks = dict()
ranks[-1000000000] = 'Слабенький'
ranks[-5] = 'Новичок'
ranks[15] = 'Я русский'
ranks[30] = '5 по русскому'
ranks[50] = 'Участник школьного этапа по русскому языку'
ranks[75] = 'Призёр ОГЭ по русскому языку'
ranks[100] = 'Победитель региона по русскому языку'
ranks[200] = 'Призёр ВСОШ по русскому'
ranks[500] = 'Абсолютный победитель русского медвежонка'

def get_rank(points : int):
    if points >= 500:
        return ranks[500]
    last = 'Невероятно слабый чел'
    for [x, y] in ranks.items():
        if x > points:
            return last
        last = y