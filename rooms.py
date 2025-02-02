class Player:
	id = 0
	score = 0
	bet = 0

	def __init__(self, id):
		self.id = id


class Room:
	id = 0
	players = []
	started = False

	def __init__(self, id):
		self.id = id


def find_room_by_id(id, rooms):
	for room in rooms:
		if room.id == id:
			return room
	return None


def find_room_by_player(player_id, rooms):
	for room in rooms:
		for player in room.players:
			if player.id == player_id:
				return room
	return None