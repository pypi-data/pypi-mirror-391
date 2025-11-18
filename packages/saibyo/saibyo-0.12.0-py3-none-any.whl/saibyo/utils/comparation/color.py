def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """
    Transforms a hexadecimal color string into an RGB tuple.

    Parameters
    ----------
    hex_color : str
        The hexadecimal color string, e.g., '#FF5733'.

    Returns
    -------
    tuple[int, int, int]
        A tuple representing the RGB values, e.g., (255, 87, 51).

    """
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:  # noqa: PLR2004
        msg = f"Invalid color: {hex_color}"
        raise ValueError(msg)

    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    return (r, g, b)
