class Raycaster:
    """Raio 2D simplificado contra bounding box da obra ativa."""

    @staticmethod
    def intersects(origin, direction, bounds):
        ox, oy = origin
        dx, dy = direction
        left, top, right, bottom = bounds

        tx_min = float("-inf")
        tx_max = float("inf")
        ty_min = float("-inf")
        ty_max = float("inf")

        if abs(dx) < 1e-9:
            if ox < left or ox > right:
                return False
        else:
            tx1 = (left - ox) / dx
            tx2 = (right - ox) / dx
            tx_min, tx_max = min(tx1, tx2), max(tx1, tx2)

        if abs(dy) < 1e-9:
            if oy < top or oy > bottom:
                return False
        else:
            ty1 = (top - oy) / dy
            ty2 = (bottom - oy) / dy
            ty_min, ty_max = min(ty1, ty2), max(ty1, ty2)

        return max(tx_min, ty_min) <= min(tx_max, ty_max) and min(tx_max, ty_max) >= 0
