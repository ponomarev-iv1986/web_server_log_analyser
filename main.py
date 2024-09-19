import json
import logging
import os.path
from collections import Counter
from re import search
from typing import Any


def get_requests(path_to_file: str) -> list[dict[str, Any]]:
    list_requests = []
    errors = 0
    pattern = (
        r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - - '
        r'(\[.+\]) "(.+?)" (\d{3}) (\d+) "(.+?)" "(.+?)" (\d+)'
    )
    with open(path_to_file, 'r', encoding='utf-8') as file:
        for line in file:
            try:
                match_object = search(pattern, line)
                ip = match_object.group(1)
                date = match_object.group(2)
                method = match_object.group(3).split()[0]
                url = match_object.group(6)
                duration = int(match_object.group(8))
                request = dict(
                    ip=ip,
                    date=date,
                    method=method,
                    url=url,
                    duration=duration,
                )
                list_requests.append(request)
            except AttributeError:
                errors += 1
    if errors:
        logging.warning(f'Не удалось распарсить {errors} строк. Не верный формат.')
    return list_requests


def get_total_stat(requests: list[dict[str, Any]]) -> dict[str, int]:
    method_list = [request['method'] for request in requests]
    return dict(Counter(method_list))


def get_top_ips(requests: list[dict[str, Any]]) -> dict[str, int]:
    ip_list = [request['ip'] for request in requests]
    ip_count = dict(Counter(ip_list))
    sorted_ip_count = sorted(ip_count.items(), key=lambda item: item[1], reverse=True)
    return dict(sorted_ip_count[:3])


def get_top_longest(requests: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sorted_requests = sorted(
        requests, key=lambda request: request['duration'], reverse=True
    )
    return sorted_requests[:3]


def generate_statistic(path_to_log_file: str) -> None:
    requests = get_requests(path_to_log_file)
    total_requests = len(requests)
    total_stat = get_total_stat(requests)
    top_ips = get_top_ips(requests)
    top_longest = get_top_longest(requests)
    result = dict(
        top_ips=top_ips,
        top_longest=top_longest,
        total_stat=total_stat,
        total_requests=total_requests,
    )
    filename = os.path.basename(path_to_log_file).split('.')[0]
    with open(
        os.path.join(os.path.dirname(path_to_log_file), f'{filename}.json'),
        'w',
        encoding='utf-8',
    ) as file:
        print(json.dumps(result, indent=4), file=file)


def main():
    path = input('Введите путь до файла или директории: ')
    if os.path.isfile(path):
        generate_statistic(path)
    elif os.path.isdir(path):
        files = os.listdir(path)
        for file in files:
            generate_statistic(os.path.join(path, file))
    else:
        raise ValueError('Не верный путь до файла, или директории')


if __name__ == '__main__':
    main()
