def selection(characters, graveyard, num):
    new_list = list(characters + graveyard)
    new_list.sort(key=lambda x: x.score, reverse=True)
    return new_list[:num]