separator = ("_\\" * 15) + "_"
right_arrow = "<:rightarrow:484382334582390784>"


def has_role(member, role_id):
    if any(_.id == role_id for _ in member.roles):
        return True
    return False
