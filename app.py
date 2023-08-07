import configparser
import logging
import pathlib
import random
import sys
import threading
import time
from typing import Type

import schedule
from schedule import CancelJob
from pushbullet import PushBullet

from dice_automation import update_profile as dice_job

last_used_salary: int
config: configparser.ConfigParser


def setup_logging(in_prod: bool) -> None:
    if in_prod:
        log_path = pathlib.Path('/app/dua/log/app.log')
    else:
        log_path = pathlib.Path(__file__).parent.resolve().joinpath('log', 'app.log')
    log_path.touch(511, exist_ok=True)
    logging.basicConfig(filename=log_path, filemode='w',
                        format='%(asctime)s %(levelname)s [%(filename)s, line %(lineno)d, %(funcName)s()] %(message)s',
                        datefmt='%d-%b-%y %H:%M:%S', level=logging.DEBUG)


def read_config(in_prod: bool) -> configparser.ConfigParser:
    if in_prod:
        config_path = pathlib.Path('/app/dua/configs/config.ini')
    else:
        config_path = pathlib.Path(__file__).parent.resolve().joinpath('configs', 'config.ini')
    if not config_path.exists():
        logging.error('Error reading config, file not exists')
    conf = configparser.ConfigParser()
    conf.read(config_path)
    logging.info(f"Checking conf info, token:{conf['credentials']['token']}")
    return conf


def get_configuration(in_prod: bool) -> configparser.ConfigParser:
    headless, dev_stop = False, False
    if len(sys.argv) > 0:
        headless = 'h' in sys.argv
        dev_stop = 'd' in sys.argv
    logging.info(f"Running mode: in production:{in_prod}; "
                 f"headless browser:{headless}; "
                 f"pause browser to get access to devTools:{dev_stop}.")
    conf = read_config(in_prod)
    # noinspection PyTypeChecker
    conf['args'] = {'in_prod': in_prod,
                    'headless': headless, 'dev_stop': dev_stop}
    return conf


def random_salary() -> int:
    salaries: list = []
    for key, val in config.items('salary'):
        salaries.append(int(val))
    salaries.remove(last_used_salary)
    return random.choice(salaries)


def update_profile() -> Type[CancelJob]:
    salary = random_salary()
    global last_used_salary
    last_used_salary = salary
    job_res: bool = dice_job(config, salary) or False
    message: str = f"Dice profile update {'complete' if job_res else 'failed'}."
    threading.Thread(target=send_notification,
                     args=(message,), daemon=True).start()
    return schedule.CancelJob


def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()


def send_notification(message: str) -> None:
    data = 'Dice Profile Updater'
    pb = PushBullet(config['credentials']['token'])
    push = pb.push_note(data, message)
    logging.info(f"{message}, id: {push['iden']}, active: {push['active']}")


def random_time() -> str:
    random.seed(7)
    return f"{random.randrange(9, 18):0>2d}:{random.randrange(0, 60):0>2d}:{random.randrange(0, 60):0>2d}"


def schedule_dice_editing() -> None:
    sched_time = random_time()
    message = f"profile update scheduled to: {sched_time}"
    logging.info(message)
    threading.Thread(target=send_notification,
                     args=(message,), daemon=True).start()
    schedule.every().day.at(sched_time, 'America/Los_Angeles').do(run_threaded,
                                                                  update_profile).tag('dice_job')


prod = len(sys.argv) > 0 and 'p' in sys.argv
setup_logging(prod)
config = get_configuration(prod)

schedule.every().day.at(
    '09:00', 'America/Los_Angeles').do(schedule_dice_editing).tag('job_scheduler')

while True:
    schedule.run_pending()
    time.sleep(1)
