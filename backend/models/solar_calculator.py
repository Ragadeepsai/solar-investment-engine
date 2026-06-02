def calculate_subsidy(system_size_kw: float) -> float:
    if system_size_kw <= 2:
        return system_size_kw * 30000
    elif system_size_kw <= 3:
        return 78000
    else:
        return 78000
