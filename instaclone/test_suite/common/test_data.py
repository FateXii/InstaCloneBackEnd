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
]


posts = [
    {
        'image': 'https://www.refinery29.com/' +
        'images/9552495.jpg?format=webp&width=720&height=864&quality=85',
        'caption': 'Jennifer Love Hewitt'
    },
    {
        'image': 'https://m.media-amazon.com/' +
        'images/M/' +
        'MV5BNjRmMThkZTItNGQ3Yy00NDc0LWE5OWMtYzkx' +
        'MDRkMzI1OTcyXkEyXkFqcGdeQXVyMjQwMDg0Ng@@._V1_UY1200_CR85' +
        ',0,630,1200_AL_.jpg',
        'caption': 'Olivia Wilde'
    },
    {
        'image': 'https://pyxis.nymag.com/v1/imgs/72f/f29/' +
        '53ec086414eddda214051ce2ce78fef5ca-26-jodie-comer.rsquare.w1200.jpg',
        'caption': 'Jodie Comer'
    }
]
