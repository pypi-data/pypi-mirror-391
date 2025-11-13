def strip_whitespaces(df):
    def stripper(x):
        if x and isinstance(x, str):
            return x.strip()
        else:
            return x

    return df.map(stripper)
