#encoding: utf-8
from django.contrib.auth.models import Group
from django.db.models.signals import post_syncdb
import ask_librarian.models


def init_app(sender, **kwargs):
    # Your specific logic here
    print 'Init ask_librarian module'                      # print sends to sys.stdout
#    while 1:
#        try:
#            reply  = raw_input('Enter a number>')   # raw_input reads sys.stdin
#        except EOFError:
#            break                                   # raises an except on eof
#        else:                                       # input given as a string
#            num = int(reply)
#            print "%d squared is %d" % (num, num ** 2)
#            break
#    print 'Bye'
    pass

post_syncdb.connect(init_app, sender=ask_librarian.models)



def init_groups(sender, **kwargs):
    """
    Проверка на существование или создание группы librarians для управления ответами
    """
    librarians, created = Group.objects.get_or_create(name='librarians')
    print librarians, created
    if librarians:
        print 'Group librarians was created'

post_syncdb.connect(init_groups, sender=ask_librarian.models)