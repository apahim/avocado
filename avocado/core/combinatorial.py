import json

from avocado.core import varianter

class Nwise(object):

    def __init__(self, variants, combined_elements=2):
        """
        :param combinations: List of Avocado Variants
        :param combined_elements: N-wise number of elements to be
                                  combined together
        """
        self.variants = variants
        self.combined_elements = combined_elements

    def outcome(self):
        # Iterating the variants object
        print '================='
        for variant in self.variants.itertests():
            print('COMBINATION: %s' % variant['variant_id'])
            for node in variant['variant']:
                for key, value in node.environment.iteritems():
                    print(' KEY: %s, VALUE: %s' % (key ,value))

        print '================='
        # Serializing the variants object and iterating the
        # serialized object
        serialized_variants = self.variants.dump()
        for variant in serialized_variants:
            print('COMBINATION: %s' % variant['variant_id'])
            for node in variant['variant']:
                for item in node[1]:
                    print(' KEY: %s, VALUE: %s' % (item[1] ,item[2]))
        print '================='

        # Creating a variants object out of the serialized object
        new_variants = varianter.Varianter(state=serialized_variants)

        return new_variants
