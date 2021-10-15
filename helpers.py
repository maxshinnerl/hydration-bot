# helper functions to avoid crowding the hbfunc

def split_names(args):
    """
    If comparing weapons, need to split on the & (NOTE: will break if weapons have & in them)
    """
    fullstr = ' '.join(args)
    names = fullstr.split(' & ')
    return names[0], names[1]
