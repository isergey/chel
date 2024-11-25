from time import monotonic

from junimarc.ftdb.kvdb import KvDb


def test_kvdb():
    # db:KvDb[str, str] = KvDb('kv.db')
    # for i in range(1000000):
    #     k = str(i)
    #     v = str(i)
    #     db.set(k, v)
    # db.save()

    db:KvDb[int, int] = KvDb('kv_int_int.db', key_type='int', value_type='int')
    for i in range(1000000):
        db.set(i, i)
    db.save()

    # db1:KvDb[str, str] = KvDb('kv_int_int.db')
    # db1.load()
    #
    # print(db1.get('111'))



def record_time(function):
    def wrap(*args, **kwargs):
        start_time = monotonic()
        function_return = function(*args, **kwargs)
        print(f"Run time {monotonic() - start_time} seconds")
        return function_return
    return wrap


@record_time
def test():
    test_kvdb()


# @record_time
# def main():
#     with open('/tmp/content', "wb") as w:
#         r = Reader("/home/sergey/GolandProjects/gomarc/chelreglib.ISO")
#         i = 0
#         for record in r.read():
#             i += 1
#             if i % 10000 == 0:
#                 print(i)
#
#
if __name__ == '__main__':
    test()
    # main()
