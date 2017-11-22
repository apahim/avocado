from avocado import Test


class TestCit(Test):

    def test(self):
        self.log.info("CIT p1: %s", self.params.get('p1'))
        self.log.info("CIT p2: %s", self.params.get('p2'))
        self.log.info("CIT p3: %s", self.params.get('p3'))
