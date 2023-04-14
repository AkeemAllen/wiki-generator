import argparse
import json
import os
import pokebase
import yaml
from snakemd import Document
from models.game_route_models import Encounters, Route, TrainerOrWildPokemon, Trainers

from utils import get_pokemon_dex_formatted_name


with open(f"temp/pokemon.json", encoding="utf-8") as pokemon_file:
    pokemon = json.load(pokemon_file)
    pokemon_file.close()


def get_markdown_image_for_item(item_name: str):
    return f"![{item_name}](../../img/items/{item_name}.png)"


def get_markdown_image_for_pokemon(pokemon_name: str):
    dex_number = pokemon[pokemon_name]["id"]
    file_name = get_pokemon_dex_formatted_name(dex_number)
    return f"![{pokemon_name}](../../img/pokemon/{file_name}.png)"


def get_link_to_pokemon_page(pokemon_name: str):
    dex_number = pokemon[pokemon_name]["id"]
    url_route = get_pokemon_dex_formatted_name(dex_number)
    return f"[{pokemon_name.capitalize()}](/pokemon/{url_route})"


def get_bottom_value_for_pokemon(
    pokemon: TrainerOrWildPokemon, is_trainer_mapping=False
):
    bottom_value = ""
    if is_trainer_mapping:
        bottom_value = f"lv. {pokemon.level}"
    else:
        bottom_value = f"{pokemon.catch_rate}%"

    return bottom_value


def generate_pokemon_entry_markdown(
    pokemon: TrainerOrWildPokemon, is_trainer_mapping=False
):
    pokemon_markdown = (
        f"{get_markdown_image_for_pokemon(pokemon.name)} <br/>"
        f"{get_link_to_pokemon_page(pokemon.name)} <br/>"
        f"{get_bottom_value_for_pokemon(pokemon, is_trainer_mapping)}"
    )

    return pokemon_markdown


def get_item_entry_markdown(item_name):
    return f"{get_markdown_image_for_item(item_name)} <br/> {item_name.replace('-', ' ').capitalize()}"


def map_pokemon_entry_to_markdown(pokemon, is_trainer_mapping=False):
    pokemon_list_markdown = map(
        lambda pokemon: f"{generate_pokemon_entry_markdown(pokemon, is_trainer_mapping)}",
        pokemon,
    )
    pokemon_list_markdown = list(pokemon_list_markdown)
    return pokemon_list_markdown


def get_encounter_table_columns(max_pokemon_on_single_route):
    table_columns = ["Area", "Pokemon"]
    if max_pokemon_on_single_route == 1:
        return table_columns

    for i in range(max_pokemon_on_single_route - 1):
        if i < 5:
            table_columns.append("&nbsp;")
    return table_columns


def get_encounter_table_rows(encounters: Encounters):
    max_number_of_pokemon_on_single_route = 0
    table_array_rows_for_encounters = []

    for encounter_type, pokemon_encounter_list in encounters.__root__.items():
        if len(pokemon_encounter_list[:-1]) > max_number_of_pokemon_on_single_route:
            max_number_of_pokemon_on_single_route = len(pokemon_encounter_list[:-1])

        mapped_encounter_list = map_pokemon_entry_to_markdown(
            pokemon_encounter_list[:-1]
        )
        extra_encounter_array = []
        extra_encounter_list = []

        if len(mapped_encounter_list) > 6:
            extra_encounter_list = mapped_encounter_list[6:]
            mapped_encounter_list = mapped_encounter_list[:6]
            extra_encounter_array = [f"", *extra_encounter_list]

        encounter_array = [
            f"{get_markdown_image_for_item(encounter_type)}<br/>"
            f"{encounter_type}<br/>{pokemon_encounter_list[-1].area_level}",
            *mapped_encounter_list,
        ]

        table_array_rows_for_encounters.append(encounter_array)
        if extra_encounter_array:
            table_array_rows_for_encounters.append(extra_encounter_array)

    return (
        table_array_rows_for_encounters,
        max_number_of_pokemon_on_single_route,
    )


def get_trainer_table_columns(max_pokemon_on_single_tainer):
    table_columns = ["Trainer", 1]
    if max_pokemon_on_single_tainer == 1:
        return table_columns

    for i in range(max_pokemon_on_single_tainer - 1):
        if i < 5:
            table_columns.append(i + 2)
    return table_columns


def get_trainer_table_rows(trainers: Trainers):
    max_number_of_pokemon_single_trainer = 0
    table_array_rows_for_trainers = []

    for trainer_name, pokemon in trainers.__root__.items():
        if len(pokemon) > max_number_of_pokemon_single_trainer:
            max_number_of_pokemon_single_trainer = len(pokemon)

        mapped_pokemon = map_pokemon_entry_to_markdown(pokemon, is_trainer_mapping=True)

        trainer_array = [
            trainer_name.replace("_", " ").capitalize(),
            *mapped_pokemon,
        ]
        table_array_rows_for_trainers.append(trainer_array)

    return (table_array_rows_for_trainers, max_number_of_pokemon_single_trainer)


def create_encounter_table(route_name: str, route_directory: str, encounters):
    doc = Document("wild_encounters")
    doc.add_header(f"{route_name.replace('_', ' ').capitalize()}", 1)

    table_rows, max_number_of_pokemon_on_single_route = get_encounter_table_rows(
        encounters
    )

    table_columns = get_encounter_table_columns(max_number_of_pokemon_on_single_route)

    doc.add_table(
        table_columns,
        table_rows,
    )

    doc.output_page(f"{route_directory}/")


def create_trainer_table(route_name: str, route_directory: str, trainers):
    doc = Document("trainers")
    doc.add_header(f"{route_name.replace('_', ' ').capitalize()}", 1)

    table_rows, max_number_of_pokemon_on_single_trainer = get_trainer_table_rows(
        trainers
    )
    table_columns = get_trainer_table_columns(max_number_of_pokemon_on_single_trainer)

    doc.add_table(table_columns, table_rows)

    doc.output_page(f"{route_directory}/")


def generate_move_string(moves):
    move_string = ""
    for move in moves:
        move_string += f"<li>{move.title()}</li>"

    return f"<ul>{move_string}</ul>"


def create_important_trainer_table(
    route_name: str, route_directory: str, trainers: Trainers
):
    doc = Document("important_trainers")
    doc.add_header(f"{route_name.replace('_', ' ').capitalize()}", 1)

    table_rows, max_number_of_pokemon_on_single_trainer = get_trainer_table_rows(
        trainers
    )

    table_columns = get_trainer_table_columns(max_number_of_pokemon_on_single_trainer)
    doc.add_table(table_columns, table_rows)

    for trainer_name, trainer_pokemon in trainers.__root__.items():
        doc.add_header(trainer_name.capitalize())
        table_rows = []
        for pokemon in trainer_pokemon:
            table_rows.append(
                [
                    generate_pokemon_entry_markdown(pokemon, is_trainer_mapping=True),
                    get_item_entry_markdown(pokemon.item),
                    pokemon.nature.title(),
                    pokemon.ability.title(),
                    generate_move_string(pokemon.moves),
                ]
            )
        doc.add_table(
            [trainer_name, "Item", "Nature", "Ability", "Moves"],
            table_rows,
        )

    doc.output_page(f"{route_directory}/")


def main(wiki_name: str):
    with open(f"dist/{wiki_name}/mkdocs.yml", "r") as mkdocs_file:
        mkdocs_yaml_dict = yaml.load(mkdocs_file, Loader=yaml.FullLoader)
        mkdocs_file.close()

    with open(f"temp/routes.json", encoding="utf-8") as routes_file:
        routes = json.load(routes_file)
        routes = Route.parse_raw(json.dumps(routes))
        routes_file.close()

    mkdoc_routes = mkdocs_yaml_dict["nav"][2]["Routes"]
    for route_name, route_properties in routes.__root__.items():
        route_directory = f"dist/{wiki_name}/docs/routes/{route_name}"
        if not os.path.exists(route_directory):
            os.makedirs(route_directory)

        formatted_route_name = route_name.replace("_", " ").capitalize()
        route_entry = {}
        route_entry[formatted_route_name] = []

        if route_properties.wild_encounters:
            create_encounter_table(
                route_name, route_directory, route_properties.wild_encounters
            )
            route_entry[formatted_route_name].append(
                {"Wild Encounters": f"routes/{route_name}/wild_encounters.md"}
            )

        if route_properties.trainers:
            create_trainer_table(route_name, route_directory, route_properties.trainers)
            route_entry[formatted_route_name].append(
                {"Trainers": f"routes/{route_name}/trainers.md"}
            )

        if route_properties.important_trainers:
            create_important_trainer_table(
                route_name, route_directory, route_properties.important_trainers
            )
            route_entry[formatted_route_name].append(
                {"Important Trainers": f"routes/{route_name}/important_trainers.md"}
            )

        if route_entry not in mkdoc_routes:
            print(route_entry)
            mkdoc_routes.append(route_entry)

    mkdocs_yaml_dict["nav"][2]["Routes"] = mkdoc_routes

    with open(f"dist/{wiki_name}/mkdocs.yml", "w") as mkdocs_file:
        yaml.dump(mkdocs_yaml_dict, mkdocs_file, sort_keys=False, indent=4)
        mkdocs_file.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-wn",
        "--wiki-name",
        help="Specify the name of the wiki to download data from",
        type=str,
    )

    args = parser.parse_args()

    main(args.wiki_name)