import time

from mcap.reader import make_reader


class Iterator:
    def __init__(self, fs):
        self.summarys = {}
        self.fs = fs
        self.opened_file = []


    def create_iterator(self, file_path, topic_list, queue):
        f = self.fs.opent(file_path, mode="rb")
        reader = make_reader(f)
        if file_path in self.summarys:
            reader._summary = self.summarys[file_path]
        else:
            summary = reader.get_summary()
            self.summarys[file_path] = summary
        self.opened_file.append(f)
        try:
            iterator = reader.iter_messages(topics=topic_list)
            message = next(iterator)
            if message[2]:
                log_time = message[2].log_time
            else:
                log_time = 0
            queue.put((log_time, time.time(), message, iterator))
        except Exception:
            f.close()
            self.opened_file.remove(f)
            raise

    def __iter__(self):
        return self

    def __next__(self):
        if self.queue.empty():
            for f in self.opened_file:
                f.close()
            raise StopIteration
        else:
            log_time, recv_time, message, iterator = self.queue.get()
        try:
            next_message = next(iterator)
            if next_message[2]:
                log_time = next_message[2].log_time
            else:
                log_time += 1
            self.queue.put((log_time, time.time(), next_message, iterator))
        except Exception:
            pass
        return message