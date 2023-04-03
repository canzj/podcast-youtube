import logging
import os
import queue
import threading
import time

import youtube_dl


def download_manager():
    return _download_manger


def download_mp3(video_url, dest_path) -> (str, str):
    ydl_opts = {
        'format': 'bestaudio/best',
        'download_archive': os.path.join(dest_path, 'downloaded.log'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(dest_path, '%(title)s-%(upload_date)s-%(id)s.%(ext)s'),
        'quiet': True,
        'getfilename': True,  # add this option to get the filename
    }

    file_name = None
    thumbnail_url = None
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        for i in range(3):
            try:
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(video_url, download=False)
                    file_path = ydl.prepare_filename(info_dict)
                    file_name = os.path.splitext(os.path.basename(file_path))[0]
                    if 'thumbnail' in info_dict:
                        thumbnail_url = info_dict['thumbnail']
                    logging.info(f"[fetching video name] successfully, url: {video_url}")
                    break
            except Exception as e:
                logging.warning(f"[fetching video name] Attempt {i + 1} failed, URL is {video_url}: {e}")
                time.sleep(10)
        else:
            raise Exception("[fetching video name] failed after 3 retries")
        _download_manger.add_task(video_url, ydl_opts)
    return f"{file_name}.mp3", thumbnail_url


def download_file(video_url, ydl_opts: dict):
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        for i in range(3):
            try:
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])
                    logging.info(f"Downloaded {video_url} successfully")
                    break
            except Exception as e:
                logging.warning(f"Download File Attempt {i + 1} failed, URL is {video_url}: {e}")
                time.sleep(10)
        else:
            raise Exception("Download failed after 3 retries")


class DownloadManager:
    _instance = None
    _sentinel = object()  # Add a sentinel value

    def __new__(cls, thread_count=4):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.thread_count = thread_count
            cls._instance.queue = queue.Queue()
            cls._instance.threads = [threading.Thread(target=cls._instance._download_worker) for _ in
                                     range(thread_count)]
            for thread in cls._instance.threads:
                thread.start()
        return cls._instance

    def _download_worker(self):
        while True:
            task = self.queue.get(block=True)
            if task is self._sentinel:  # Check if the task is the sentinel value
                break
            video_url, ydl_opts = task
            try:
                download_file(video_url, ydl_opts)
            except Exception as e:
                logging.warning(f"Download failed: {e}, url: {video_url}, opts: {ydl_opts}, skipped")
            self.queue.task_done()

    def add_task(self, video_url, ydl_opts: dict):
        self.queue.put((video_url, ydl_opts))

    def shutdown(self):
        logging.warning("Download manager shutting down")
        for _ in range(self.thread_count):
            self.queue.put(self._sentinel)  # Put the sentinel value into the queue for each thread
        for thread in self.threads:
            thread.join()  # Wait for the threads to exit
        logging.warning("Download manager shutdown")


_download_manger = DownloadManager(thread_count=2)
