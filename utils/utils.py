def truly_empty(dict_of_dicts):
        '''Query for a dict of empty dicts.
        '''
        for key in dict_of_dicts:
            if len(dict_of_dicts[key]):
                return False
        return True