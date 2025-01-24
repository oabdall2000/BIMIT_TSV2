from time import sleep

from libs_copy import download_pretrained_weights

if __name__ == "__main__":
    """
    Download all pretrained weights
    """
    for task_id in [ 730, 731, 732, 733]:
        download_pretrained_weights(task_id)
        sleep(5)
