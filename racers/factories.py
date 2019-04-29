import factory
import random
from .models import Racer
from faker import Faker
from companies.factories import CompanyFactory
fake = Faker()

def get_racer_number():
    "Return a unique Racer number."
    racer_numbers =  [i for i in range(999)]
    racers = Racer.objects.all()
    racer_number = random.choice(racer_numbers)

    while Racer.objects.filter(racer_number=racer_number).exists():
        racer_number = random.choice(racer_numbers)

    return racer_number

def get_random_gender():
    "Return a random gender from available choices."
    lt_choices = [x[0] for x in Racer.GENDER_OPTIONS]
    return random.choice(lt_choices)

def get_random_category():
    "Return a random category from available choices."
    lt_choices = [x[0] for x in Racer.RACER_CATEGORY_OPTIONS]
    return random.choice(lt_choices)

def create_nick_name():
    "Return a random category from available choices."
    gets_nickname = random.randrange(10)
    if gets_nickname >= 7:
        nickname = fake.word()
    else:
        nickname = ""
    return nickname

class RacerFactory(factory.DjangoModelFactory):
    company = factory.SubFactory(CompanyFactory)
    racer_number = factory.LazyFunction(get_racer_number)
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    nick_name = factory.LazyFunction(create_nick_name)
    city = factory.Faker('city')
    gender = factory.LazyFunction(get_random_gender)
    category = factory.LazyFunction(get_random_category)

    class Meta:
        model = Racer
