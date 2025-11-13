from requests import Response
import requests
import sys
import time
import os


class Requester:
    def __init__(self, retries: int, verbose: bool):
        self.retries = retries
        self.verbose = verbose

    @staticmethod
    def _int_to_unit(i: int) -> str:
        gb: int = 1_073_741_824
        mb: int = 1_048_576
        kb: int = 1024

        if i >= gb:
            return f'{(i / gb):.2f}Gb'
        elif i >= mb:
            return f'{(i / mb):.2f}Mb'
        elif i >= kb:
            return f'{(i / kb):.2f}Kb'
        else:
            return str(i)

    @staticmethod
    def _get_content_length(response: Response) -> int:
        return int(response.headers.get('Content-Length', '0'))

    @staticmethod
    def request(func):
        def wrapper(*args, **kwargs):
            delay = kwargs.get('delay', 0)
            time.sleep(delay)
            return func(*args, **kwargs)
        return wrapper

    @request
    def fetch(self, url: str, delay: float = 0) -> bytes:
        retries: int = self.retries

        while retries:
            try:
                response = requests.get(url)
                response.raise_for_status()
            except requests.exceptions.RequestException as err:
                print(err, file=sys.stderr)

                if err.response.status_code == 404:
                    break

                if retries := retries - 1:
                    delay = (delay + 1) * 2
                    time.sleep(delay)
            else:
                return response.content

        return b''

    @request
    def stream(self, url: str, delay: float = 0, fp: str = '', rate: int = 0) -> bytes:
        retries = self.retries
        current_chunk_size = rate

        while retries:
            existing = os.path.getsize(fp) if os.path.exists(fp) else 0
            headers = {'Range': f'bytes={existing}-', 'Connection': 'close'}

            try:
                response = requests.get(url, stream=True, timeout=(5, 60), headers=headers)

                if response.status_code == 404:
                    break

                response.raise_for_status()

                run = 0
                grabbed = 0
                length = self._get_content_length(response)
            except requests.exceptions.RequestException as err:
                if self.verbose:
                    print(err, file=sys.stderr)

                if retries := retries - 1:
                    delay = (delay + 1) * 2
                    time.sleep(delay)
            else:
                try:
                    for chunk in response.iter_content(chunk_size=current_chunk_size):
                        if not chunk:
                            continue

                        grabbed += len(chunk)

                        if self.verbose:
                            gr = self._int_to_unit(grabbed)
                            ln = self._int_to_unit(length)
                            rt = self._int_to_unit(rate)
                            print(f'\r{gr} / {ln}   {rt}', end='', flush=True)

                        if current_chunk_size < rate:
                            run += 1

                            if run >= 100:
                                current_chunk_size *= 2

                        yield chunk
                except requests.exceptions.ChunkedEncodingError as err:
                    if self.verbose:
                        print(err, file=sys.stderr)

                    rate //= 2
                except requests.exceptions.ConnectionError as err:
                    if self.verbose:
                        print(err, file=sys.stderr)

                    if retries := retries - 1:
                        delay = (delay + 1) * 2
                        time.sleep(delay)
                else:
                    break
