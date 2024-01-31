# helper functions to avoid crowding the hbfunc

def split_names(args):
    """
    If comparing weapons, need to split on the & (NOTE: will break if weapons have & in them)
    """
    fullstr = ' '.join(args)

    if '&' not in fullstr:
        return [] 

    names = fullstr.split(' & ')

    
    if len(names) < 2:
        return []

    return names[0].split(" "), names[1].split(" ")  # RETURN IN LIST FORMAT (for the closest() call)
