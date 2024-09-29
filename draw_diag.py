import os
import sys
from pathlib import Path
from typing import Any, Literal

from diagrams.c4 import _format_node_label
from diagrams import Cluster, Diagram
from diagrams.digitalocean.compute import Containers
from yaml import safe_load

os.environ["PATH"] += os.pathsep + "C:\\Program Files\\Graphviz\\bin\\"

REPLACEMENTS = {
    "postgres": "postgresql",
    "pgadmin": "postgresql",
}


class AutoNode(Containers):

    def __init__(self, service_image: str, *args, **kwargs):
        service_image = self._format_service_image(service_image)
        self._find_icon(service_image)
        super().__init__(*args, **kwargs)

    def _find_icon(self, service_image: str):
        """Поиск иконки сервиса"""
        file_match = None  # Переменная для хранения найденного файла
        max_match_length = 0  # Количество букв в совпадении
        resources_path = Path(self._load_icon()).parent.parent.parent

        # Выбираем все png файлы в папке resources
        for file in resources_path.rglob("*.png"):
            icon_name = file.name.rsplit(".", 1)[0]
            if len(icon_name) > 1 and icon_name in service_image:
                # Проверка на совпадение имени файла с именем сервиса
                if file_match is None or len(icon_name) > max_match_length:
                    file_match = file
                    max_match_length = len(icon_name)

        if file_match is not None:
            base_path, provider, category, icon_name = file_match.as_posix().rsplit("/", 3)
            self._icon = icon_name
            self._icon_dir = f"resources/{provider}/{category}"
            self._provider = provider

    @staticmethod
    def _format_service_image(service_image: str) -> str:
        """Format the service image to the correct format for diagrams"""
        for k, v in REPLACEMENTS.items():
            service_image = service_image.replace(k, v)
        return service_image


def get_docker_compose(file_path: Path) -> dict[str, Any]:
    with file_path.open("r", encoding="utf-8") as f:
        return safe_load(f)


def create_networks(compose: dict) -> dict[str, list[dict]]:
    networks: dict = {"default": []}  # Список сетей
    for name, config in compose["services"].items():
        if config.get("networks"):
            if isinstance(config["networks"], list):
                network = config["networks"][0]  # Берем первую сеть
            elif isinstance(config["networks"], dict):
                network = list(config["networks"].keys())[0]
            else:
                continue
            networks.setdefault(network, [])
            networks[network].append({"name": name, **config})
        else:
            networks["default"].append({"name": name, **config})
    return networks


def create_diagram(
    file_path: Path,
    show: bool = False,
    direction: Literal["TB", "LR", "BT", "RL"] = "TB",
    curvestyle: Literal["ortho", "curved"] = "curved",
    strict: bool = True,
) -> None:
    compose = get_docker_compose(file_path)
    networks = create_networks(compose)
    image_path = (file_path.parent / file_path.name.rsplit(".", 1)[0]).absolute().as_posix()

    with Diagram(
        name="Docker Compose Diagram",
        filename=image_path,
        show=show,
        direction=direction,
        curvestyle=curvestyle,
        strict=strict,
    ):
        for network_name, network_services in networks.items():
            with Cluster(network_name):
                for service in network_services:
                    # Создание сервиса
                    node = AutoNode(
                        service["image"],
                        _format_node_label(
                            service["name"],
                            ", ".join(service.get("ports", [])),
                            description="",
                        ),
                    )
                    compose["services"][service["name"]]["node"] = node

        # Добавление связи между сервисами
        for service, config in compose["services"].items():
            for link in config.get("links", []):
                _ = config["node"] >> compose["services"][link]["node"]
            for depend_on in config.get("depends_on", []):
                _ = config["node"] >> compose["services"][depend_on]["node"]


if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        filename = Path(filename).resolve()

        for value in sys.argv[2:]:
            if "=" in value:
                key, valid = value.split("=", 1)
                REPLACEMENTS[key] = valid

    else:
        print("Set the file name")
        sys.exit(1)

    if not filename.is_file():
        print(f"File {filename} not found")
        sys.exit(1)

    create_diagram(filename)
