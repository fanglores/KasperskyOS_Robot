from pydantic import BaseModel, conint, confloat


"""  DataSchema  """


class EngineCommandSchema(BaseModel):
    type_engine: str
    speed: int #conint(ge=-100, le=100)
    time: float #confloat(gt=0)


"""  Command template  """


class Engine:
    speed: int
    status: bool
    time_worked: float

    def __init__(self, speed, time):
        self.speed = speed
        self.time_worked = time
        self.status = False

    def back_command(self):
        self.speed *= -1
        self.status = False

    def status_complete(self):
        self.status = True


class EngineRight(Engine):
    type_engine = 'right'

    def __init__(self, speed, time):
        super().__init__(speed, time)


class EngineLeft(Engine):
    type_engine = 'left'

    def __init__(self, speed, time):
        super().__init__(speed, time)


class EngineTank(Engine):
    type_engine = 'tank'

    def __init__(self, speed, time):
        super().__init__(speed, time)


class Commands:
    all_commands = []
    dict_all_command = []
    finish_command = []

    def add_new_command(self, type_command, speed, time):
        if type_command == 'right':
            new_command = EngineRight(speed, time)
        elif type_command == 'left':
            new_command = EngineLeft(speed, time)
        elif type_command == 'tank':
            new_command = EngineTank(speed, time)
        else:
            return None

        print(type_command, speed, time)
        schema = EngineCommandSchema(type_engine=type_command,
                                     time=time,
                                     speed=speed)

        self.dict_all_command.append(schema)
        self.all_commands.append(new_command)

        print("[ADD NEW COMMAND ENGINE] : " + str(schema.dict()))
        return schema


