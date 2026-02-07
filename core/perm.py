import typing

class Perm(typing.TypedDict):
	is_viewable: bool
	is_editable: bool
	is_movable: bool
	is_deletable: bool
	can_change_acl: bool