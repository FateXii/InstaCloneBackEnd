iso_profile = {

    "username": "user_iso",
    "first_name": "first_name_iso",
    "email": "email_iso@mail.com",
    "password": "pass1234",
    "bio": "This is my bio",
    "phone_number": "0781132096",
    "is_private": True,
    "country": "ZA",
}

profiles = [
    {
        'username': 'user{}'.format(i),
        'first_name': 'first_name{}'.format(i),
        'email': 'email{}@mail.com'.format(i),
        'password': 'pass1234',
        'bio': 'This user{}`s bio'.format(i),
        'phone_number': '+27781132096',
        'is_private': i > 4,
        'country': 'ZA'
    } for i in range(10)
    # {
    #     'username': 'user1',
    #     'first_name': 'first_name1',
    #     'email': 'email{}@mail.com'.format(i),
    #     'password': 'pass1234',
    #     'bio': 'This user1`s bio',
    #     'phone_number': '+27781132096',
    #     'is_private': True,
    #     'country': 'ZA'
    # },
    # {
    #     'username': 'user2',
    #     'first_name': 'first_name2',
    #     'email': 'email{}@mail.com'.format(i),
    #     'password': 'pass1234',
    #     'bio': 'This user2`s bio',
    #     'phone_number': '+27781132096',
    #     'is_private': True,
    #     'country': 'ZA'
    # },
    # {
    #     'username': 'user3',
    #     'first_name': 'first_name3',
    #     'email': 'email{}@mail.com'.format(i),
    #     'password': 'pass1234',
    #     'bio': 'This user3`s bio',
    #     'phone_number': '+27781132096',
    #     'is_private': True,
    #     'country': 'ZA'
    # },
    # {
    #     'username': 'user4',
    #     'first_name': 'first_name4',
    #     'email': 'email{}@mail.com'.format(i),
    #     'password': 'pass1234',
    #     'bio': 'This user4`s bio',
    #     'phone_number': '+27781132096',
    #     'is_private': True,
    #     'country': 'ZA'
    # },
    # {
    #     'username': 'user5',
    #     'first_name': 'first_name5',
    #     'email': 'email{}@mail.com'.format(i),
    #     'password': 'pass1234',
    #     'bio': 'This user5`s bio',
    #     'phone_number': '+27781132096',
    #     'is_private': False,
    #     'country': 'ZA'
    # },
    # {
    #     'username': 'user6',
    #     'first_name': 'first_name6',
    #     'email': 'email{}@mail.com'.format(i),
    #     'password': 'pass1234',
    #     'bio': 'This user6`s bio',
    #     'phone_number': '+27781132096',
    #     'is_private': False,
    #     'country': 'ZA'
    # },
    # {
    #     'username': 'user7',
    #     'first_name': 'first_name7',
    #     'email': 'email{}@mail.com'.format(i),
    #     'password': 'pass1234',
    #     'bio': 'This user7`s bio',
    #     'phone_number': '+27781132096',
    #     'is_private': False,
    #     'country': 'ZA'
    # },
    # {
    #     'username': 'user8',
    #     'first_name': 'first_name8',
    #     'email': 'email{}@mail.com'.format(i),
    #     'password': 'pass1234',
    #     'bio': 'This user8`s bio',
    #     'phone_number': '+27781132096',
    #     'is_private': False,
    #     'country': 'ZA'
    # },
    # {
    #     'username': 'user9',
    #     'first_name': 'first_name9',
    #     'email': 'email{}@mail.com'.format(i),
    #     'password': 'pass1234',
    #     'bio': 'This user9`s bio',
    #     'phone_number': '+27781132096',
    #     'is_private': False,
    #     'country': 'ZA'
    # }
]


posts = [
    {
        'image': 'https://www.refinery29.com/images/9552495.jpg?format=webp&width=720&height=864&quality=85',
        'caption': 'Jennifer Love Hewitt'
    },
    {
        'image': 'https://m.media-amazon.com/images/M/MV5BNjRmMThkZTItNGQ3Yy00NDc0LWE5OWMtYzkxMDRkMzI1OTcyXkEyXkFqcGdeQXVyMjQwMDg0Ng@@._V1_UY1200_CR85,0,630,1200_AL_.jpg',
        'caption': 'Olivia Wilde'
    },
    {
        'image': 'https://pyxis.nymag.com/v1/imgs/72f/f29/53ec086414eddda214051ce2ce78fef5ca-26-jodie-comer.rsquare.w1200.jpg',
        'caption': 'Jodie Comer'
    }
]
