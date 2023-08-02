import configparser
import logging
import pathlib
import random
import sys
import threading
import time
from typing import Type

import schedule
from pushbullet import PushBullet
from schedule import CancelJob

from dice_automation import update_profile as dice_job

last_used_salary: int


def random_salary() -> int:
    salaries: list = []
    for key, val in config_data.items('salary'):
        salaries.append(val)
    salaries.remove(last_used_salary)
    return random.choice(salaries)


def update_profile() -> Type[CancelJob]:
    salary = random_salary()
    global last_used_salary
    last_used_salary = salary
    dice_job(config_data, salary)
    return schedule.CancelJob


def read_credentials(prod: bool) -> map:
    config_path = pathlib.Path(__file__).parent.resolve().joinpath('configs', 'config.ini')
    configuration = configparser.ConfigParser()
    configuration.read(config_path)
    return configuration


def run_threaded(job_func, tag):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()


def send_notification(message: str) -> None:
    data = 'Dice Profile Updater'
    pb = PushBullet(config_data['credentials']['token'])
    push = pb.push_note(data, message)
    logging.info(message, push['iden'], push['active'])


def random_time() -> str:
    random.seed(7)
    return f"{random.randrange(9, 18):0>2d}:{random.randrange(0, 60):0>2d}:{random.randrange(0, 60):0>2d}"


def schedule_dice_editing() -> None:
    sched_time = random_time()
    message = f"profile update scheduled to: {sched_time}"
    threading.Thread(target=send_notification, args=(message,), daemon=True).start()
    schedule.every().day.at(sched_time, 'America/Los_Angeles').do(run_threaded, update_profile).tag('dice_job')


in_prod = len(sys.argv) > 1 and 'p' in sys.argv
headless = len(sys.argv) > 1 and 'h' in sys.argv
dev_stop = len(sys.argv) > 1 and 'd' in sys.argv
logging.info(f"Running mode: in production:{in_prod}; "
             f"headless browser:{headless}; "
             f"pause browser to get access to devtools:{dev_stop}.")
config_data = read_credentials(in_prod)
config_data['args'] = {'in_prod': in_prod, 'headless': headless, 'dev_stop': dev_stop}

schedule.every().day.at('00:10', 'America/Los_Angeles').do(schedule_dice_editing).tag('job_scheduler')

while True:
    schedule.run_pending()
    time.sleep(1)
