import aiohttp
import asyncio
import requests
from more_itertools import chunked
from models import Person, init_db, Session, engine


async def load_db(person_list):
    async with Session() as session:
        session.add_all(person_list)
        await session.commit()


async def get_inside_data(client, pers_data, mode, key):
    match mode:
        case 1:
            final_result = []
            for data in pers_data:
                coro_data = await client.get(data)
                j_data = await coro_data.json()
                final_result.append(j_data[key])
            return final_result
        case 2:
            coro_world = await client.get(pers_data)
            j_world = await coro_world.json()
            homeworld = j_world[key]
            return homeworld


async def get_person(client, person_id):
    pers = await client.get(f'https://swapi.py4e.com/api/people/{person_id}/')
    if pers.status == 200:
        j_pers = await pers.json()
        person = Person(
            birth_year=j_pers['birth_year'],
            eye_color=j_pers['eye_color'],
            films=', '.join(await get_inside_data(client, j_pers['films'], mode=1, key='title')),
            gender=j_pers['gender'],
            hair_color=j_pers['hair_color'],
            height=j_pers['height'],
            home_world=await get_inside_data(client, j_pers['homeworld'], mode=2, key='name'),
            mass=j_pers['mass'],
            name=j_pers['name'],
            skin_color=j_pers['skin_color'],
            species=', '.join(await get_inside_data(client, j_pers['species'], mode=1, key='name')),
            starships=', '.join(await get_inside_data(client, j_pers['starships'], mode=1, key='name')),
            vehicles=', '.join(await get_inside_data(client, j_pers['vehicles'], mode=1, key='name')),
        )
        return person
    else:
        return


async def async_get():
    await init_db()
    client = aiohttp.ClientSession()
    count_pers = int(requests.get('https://swapi.py4e.com/api/people/').json()['count'])
    for chunk in chunked(range(1, count_pers + 1), 10):
        pers_list = []
        for i in chunk:
            pers_list.append(get_person(client, i))
        answer = await asyncio.gather(*pers_list)
        final_list = list(filter(None, answer))
        asyncio.create_task(load_db(final_list))

    task_set = asyncio.all_tasks() - {asyncio.current_task()}
    await asyncio.gather(*task_set)
    await client.close()
    await engine.dispose()
