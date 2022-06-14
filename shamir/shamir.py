"""
    API
    get_shares(k, n, s) -> shares:
        k - the number of shares that sufficent to know the secret
        n - the number of shares we share
        s - the secret

        shares - list of tuples
        [(1, 8), (4, 22) ... ]


    combine get_secret(shares) - > s:
        shares - list of tuples
        [(1, 8), (4, 22) ... ]

        s - the secret


"""