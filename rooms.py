class Player:
	def __init__(self, id, chat_id):
		self.id = id
		self.bet=0
		self.score=0
		self.chat_id=chat_id


class Room:
	id = 0
	players = []
	started = False

	def __init__(self, id):
		self.id = id
		self.players=[]
		self.started=False


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