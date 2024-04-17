import datetime


class AnimeElem:
    name: str
    size: float
    type_t: str
    seed: str
    leech: str
    movie_type: str
    date: datetime
    magnet: str

    def __init__(self, name: str, size: float, type_t: str, seed: str, leech: str, movie_type: str, date: datetime,
                 magnet: str):
        self.name = name
        self.size = size
        self.type_t = type_t
        self.seed = seed
        self.leech = leech
        self.movie_type = movie_type
        self.date = date
        self.magnet = magnet
