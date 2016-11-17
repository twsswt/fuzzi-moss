class Bob (object):
    def __call__(self, *args, **kwargs):
        print "HERE"
        return False

bob = Bob()

Bob()()