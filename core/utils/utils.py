import hashlib
import random
import string
import time


def generate_counting(worker_uuid: str, arg_dict: dict, pipe_dict: dict):
    pass
    # return list(range(0, seed + 1))


def generate_ssh_key(worker_uuid: str, arg_dict: dict, pipe_dict: dict):
    pass
    # data = f"ssh-key-seed-{seed}".encode()
    # return hashlib.sha256(data).hexdigest()


def generate_random_string(worker_uuid: str, arg_dict: dict, pipe_dict: dict):
    pass
    # random.seed(seed)
    # return ''.join(random.choices(string.ascii_letters + string.digits, k=seed))

def long_task(worker_uuid: str, arg_dict: dict, pipe_dict: dict):
    seed = arg_dict["seed"]
    wip_print_pipe = pipe_dict["wip_print_pipe"]
    done_print_pipe = pipe_dict["done_print_pipe"]

    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=seed))
    for i in range(4):
        time.sleep(1)
        max_idx = int(len(random_string)*(i/4))
        wip_string = random_string[:max_idx]
        wip_print_pipe.send({"uuid": worker_uuid, "data": f"calculated {round(i/4, 2)}% of string: {wip_string}"})
    done_print_pipe.send({"uuid": worker_uuid, "data": f"calculated string: {random_string}"})


def count_from_k(worker_uuid: str, arg_dict: dict, pipe_dict: dict):
    max_cnt = arg_dict["max_cnt"]
    print_pipe = pipe_dict["print_pipe"]

    for i in range(1, max_cnt + 1):
        time.sleep(1)
        print_pipe.send({"uuid": worker_uuid, "data": f"Count to {i}"})

