class ParserResult:
    building = None
    floor = None
    room_no = None
    course_name = None
    section = None
    week = None
    weekday = None

    def __init__(self, building, floor, room_no, section, week, weekday):
        self.building = building
        self.floor = floor
        self.room_no = room_no
        self.section = section
        self.week = week
        self.weekday = weekday

    def show(self):
        print("building:", self.building)
        print("floor:", self.floor)
        print("room_no:", self.room_no)
        print("section:", self.section)
        print("week:", self.week)
        print("weekday:", self.weekday)
