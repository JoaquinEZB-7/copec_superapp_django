def clp(n):
    """Formato miles chileno: 48200 -> '48.200'"""
    return f"{int(round(n)):,}".replace(",", ".")

def dec1(n):
    """Un decimal con coma: 13.2 -> '13,2'"""
    return f"{n:.1f}".replace(".", ",")
